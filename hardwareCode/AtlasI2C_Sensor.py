from AtlasI2C import AtlasI2C as AL
import time
import AtlasI2C_Utility as ALU
import threading as th
from CircularBuffer import CircularBuffer as CB
from Status import Status
import RPi.GPIO as GPIO
import GPIO_Utility
from datetime import datetime
from PlotImagesManager import PlotImagesManager
from FileOutputManagementSystem import FileOutputManagementSystem
import pdb
from queue import Queue

# Overview
# Threads:
# - Continuous Polling Thread: This will continuously read values from the sensors and store them in the circular buffer. This thread interacts with the sensor directly.
# - Condition Thread: This is a thread that will monitor the values in the circular buffer to see when a certain condition is met (i.e., read value is greater than a specified value or read value is less than a specified value). This thread does not interact with the sensor directly.
# Thread Flags:
# - these flags will be evaluated by the thread target functions to determine when they should terminate

# NOTE: we cannot reuse a thread object once its corresponding thread has terminated (have to initialize a new thread object)
# - however, we still store thread objects as attributes to ensure they have ended before continuing code (by running the join method)

# As of August 26, 2024, this class only fully supports the pH and EC subsystems
class AtlasI2C_Sensor:
    
    # Extend the base FieldKeys class for the sensor
    class FieldKeys(Status.FieldKeys):
        KEYWORD = "keyword"
        LATEST_READING = "latestReading"
        CONT_POLLING_THREAD_ACTIVE = "contPollingThreadActive"
        COND_THREAD_ACTIVE = "condThreadActive"
        COND_THREAD_DESCRIPTION = "condThreadDescription"
    
    # units: (pH, unitless), (EC, micro-siemens)
    PH_SENSOR_KEY_WORD = "pH"
    EC_SENSOR_KEY_WORD = "EC"
    
    CB_SIZE = 100 # This means there will be at most 100 sensor readings at any given time
    
    CB_GET_READING_DELAY = 2 # the time, in seconds, in between attempts to get readings from CB
    
    SENSOR_GET_READING_DELAY = 2 # the time, in seconds, in between attempts to get readings from sensor
    
    COND_THREAD_DELAY = 5 # in seconds
    
    IMAGES_FILE_PATH_BASE = "plotImages"
    
    # the parameter, keyword, is used to locate the specific Atlas I2C device that will be associated with the subsystem object. It will also be stored in the attribute, deviceKeyword, for future reference
    # once the device is found, it will be stored in the attribute, device
    def __init__(self, keyword : str, debugMode : bool, contPollThreadAsynchronous : bool, isOutermostEntity : bool, alias : str, fileOutputManagementSystem, generateMatPlotLibImages=False):
        
        self.alias = alias
        
        self.generateMatPlotLibImages = generateMatPlotLibImages # this will use the existing data to generate matplotlib images
        
        # for debug messages, we will insert them into this queue instead of printing to terminal
        if debugMode == True:
            self.activityLogManager = fileOutputManagementSystem
        
        if self.generateMatPlotLibImages == True:
            directoryPath = keyword + AtlasI2C_Sensor.IMAGES_FILE_PATH_BASE
            self.plotImagesManager = PlotImagesManager(directoryPath, AtlasI2C_Sensor.CB_SIZE)
        
        self.isOutermostEntity = isOutermostEntity
        if self.isOutermostEntity:
            GPIO_Utility.setModeBCM()
            
        
        self.status = Status(alias, isOutermostEntity, debugMode)
        fieldKeys = [value for key, value in AtlasI2C_Sensor.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            # print(f"Current Field Key: {fieldKey}")
            self.status.addStatusFieldTuple(fieldKey, None)
        
        # flag to determine whether should execute print statements or not
        self.debugMode = debugMode
        
        # set value of attribute, deviceKeyword
        # NOTE: This is used to locate the correct ATLAS I2C device
        self.deviceKeyword = keyword
        
        # the status object holds important details about the status of the corresponding sensor object
        
        # set initial values for status field tuples for proper program execution
        self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.KEYWORD, keyword) # add keyword field to it
        self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE, False)
        self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.COND_THREAD_ACTIVE, False)
        
        
        # contPollThreadAsynchronous: flag for determining whether the cont poll thread will be synchronized with reading from CB
        # if set to False (would mean Synchronous), will wait until the latest value of CB has been read before getting next value
        # if set to True, will just keep adding values to CB independently
        self.contPollThreadAsynchronous = contPollThreadAsynchronous
        
        # locating the device and set value of attribute, device
        self.device = None
        atlasDevicesList = AL.get_devices()
        for atlasDevice in atlasDevicesList:
            deviceInfo = atlasDevice.get_device_info()
            if keyword in deviceInfo:
                self.device = atlasDevice
                
        # initialize circular buffer and store it in attribute, CB
        self.condThreadCB = CB(AtlasI2C_Sensor.CB_SIZE)
        
        self.pushToDatabaseQueue = Queue() # each time a value is acquired from the sensor, it will be added to both the CB and Queue
        # we use queue for the database so that we can pull more than one new value at a time (so can put more data with each connect)

        # thread attributes:
        self.condThread = None # initially none since no condition thread running
        self.contPollThread = None # initially none since no continuous polling thread running
        
        self.CB_Lock = th.Lock() # create a lock for the CB, this is to ensure that only one thread interacts with the CB at any given time
        # as of August 29, 2024, the continuous polling and condition threads access the CB
        
        # FOR NEW IMPLEMENTATION OF COND THREAD
        # each tuple is: (<comparator>, <rightOperand>, <callbackFunction>, <argsListForCallback>, <isPersistent>, <alias>)
        # NOTE: persistence means that after a callback is triggered, it won't get removed from the list so can execute again (until manually removed)
        self.listCondThreadTuples = []
        
        # this pin will be for an LED
        self.turnOnLED_TestCallbackPin = 5
        # set the pin to output and then low
        GPIO_Utility.initializeOutputPin(self.turnOnLED_TestCallbackPin)
        GPIO.output(self.turnOnLED_TestCallbackPin, GPIO.LOW)
        
    def turnOnLED_TestCallback(self):
        # turn on pump
        GPIO.output(self.turnOnLED_TestCallbackPin, GPIO.HIGH)
        
        startTime = datetime.datetime.now()
        while (datetime.datetime.now() - startTime).total_seconds() < 5:
            pass
        
        # turn off pump
        GPIO.output(self.turnOnLED_TestCallbackPin, GPIO.LOW)   
    
    # setter method for conditional thread description
    def setCondThreadDescriptionStatusField(self):
        """
        NOTE: This method uses information from listCondThreadTuples to generate the description.
        """
        self.status.setStatusFieldTupleValue("condThreadDescription", "") # start with this initially
        
        newCondThreadDescription = ""
        
        if len(self.listCondThreadTuples) >= 1:
            for condThreadTuple in self.listCondThreadTuples:
                condThreadDescriptionEntry = ""
                comparator = condThreadTuple[0]
                rightOperand = condThreadTuple[1]
                callbackFunction = condThreadTuple[2]
                # condThreadTuple[3] not in use
                isPersistent = condThreadTuple[4]
                alias = condThreadTuple[5]
                condThreadDescriptionEntry += "("
                condThreadDescriptionEntry += comparator
                condThreadDescriptionEntry += str(rightOperand)
                condThreadDescriptionEntry += ", "
                condThreadDescriptionEntry += callbackFunction.__name__
                condThreadDescriptionEntry += ", "
                if isPersistent == True:
                    condThreadDescriptionEntry += "Persistent"
                else:
                    condThreadDescriptionEntry += "Non-persistent"
                condThreadDescriptionEntry += ", "
                condThreadDescriptionEntry += alias
                condThreadDescriptionEntry += "), "
                newCondThreadDescription += condThreadDescriptionEntry
        else:
            newCondThreadDescription += "No existing cond threads"
            
        self.status.setStatusFieldTupleValue("condThreadDescription", newCondThreadDescription)
    
    # status setter and update methods
    # this set of methods does what the setter methods do in the status class as well as update the status
    
    def addToListCondThreadTuples(self, comparator, rightOperand, callbackFunction, argsListForCallback, isPersistent, description):
        """
        Example set of arguments: (">", 20, someCallbackFunction, ['a', 'b', 'c'], True, "alias1") 
        """
        condThreadTuple = (comparator, rightOperand, callbackFunction, argsListForCallback, isPersistent, description)
        self.listCondThreadTuples.append(condThreadTuple)
        self.setCondThreadDescriptionStatusField() # update the status
        if self.debugMode == True:
            self.activityLogManager.addItem("Added cond thread tuple: " + str(condThreadTuple))
        
    # all you need is the alias in order to locate a specific cond thread tuple
    def removeFromListCondThreadTuples(self, alias):
        
        removedCondThreadTuple = False # assume false initially
        
        for condThreadTuple in self.listCondThreadTuples:
            if condThreadTuple[5] == alias:
                if self.debugMode == True:
                    self.activityLogManager.addItem("Removed cond thread tuple: " + str(condThreadTuple))
                self.listCondThreadTuples.remove(condThreadTuple)
                removedCondThreadTuple = True
                break
        if removedCondThreadTuple == False:
            raise Exception("Could not find cond thread tuple to remove")
        
        # update after removing
        self.setCondThreadDescriptionStatusField()
     
    def getReading(self):
        """
        Returns a single reading from the subsystem's sensor
        """
        # send command to get reading response from sensor
        reading = ALU.send_message_and_return_response(self.device, "R")
        
        # parse the response for just the numerical value and then return
        readingVal = ALU.extract_num_val(reading)
        
        return readingVal
        
    def startCondThread(self):
        """
        This method only starts the thread. NOTE: There doesn't have to be a condThreadTuple for the thread to start. It just won't assess any conditions
        """
        # NEW IMPLEMENTATION
        if(self.status.getStatusFieldTupleValueUsingKey("condThreadActive") == False):
            # initialize condThread
            self.condThread = th.Thread(target=self.condThreadTarget)
            # set status variables
            self.status.setStatusFieldTupleValue("condThreadActive", True)
            # self.status.setCondThreadState(True)
            self.condThread.start()
            if self.debugMode == True:
                self.activityLogManager.addItem("Cond thread started")
        else:
            raise Exception("Could not create cond thread, check thread variables")
    
    def condThreadTarget(self):
        """
        comparator: Should either be ">" (greater than) or "<" (less than)
        """
        
        # NEW METHOD BODY
        while(self.status.getStatusFieldTupleValueUsingKey("condThreadActive") == True):
            if len(self.listCondThreadTuples) != 0:
                if(self.condThreadCB.mostRecentValueAccessed == False and self.condThreadCB.currentSize >= 1):
                    
                    trackedThreads = [] # because each condition callback will be executed in a separate thread, we should keep track of them so can join all of them afterwards
                    
                    tuplesToRemove = []
                    
                    currentReading = self.condThreadCB.get_latest_value(bypassAccessedFlag=False)
                    
                    # INJECT CODE HERE
                    
                    for condThreadTuple in self.listCondThreadTuples:
                        
                        conditionSatisfied = False # assume false initially
                        
                        # make it more obvious the values in the tuple
                        comparator = condThreadTuple[0]
                        rightOperand = condThreadTuple[1]
                        callbackFunction = condThreadTuple[2]
                        argsListForCallback = condThreadTuple[3]
                        isPersistent = condThreadTuple[4]
                        
                        if (comparator == ">") and (currentReading > rightOperand):
                            conditionSatisfied = True
                        elif (comparator == "<") and (currentReading < rightOperand):
                            conditionSatisfied = True
                        
                        if conditionSatisfied == True:
                            # callbackFunction(*argsListForCallback)
                            newThread = th.Thread(target=callbackFunction, args=argsListForCallback)
                            trackedThreads.append(newThread)
                            newThread.start()
                            if isPersistent != True:
                                tuplesToRemove.append(condThreadTuple)
                    # join all threads before proceeding
                    if len(trackedThreads) != 0:
                        for trackedThread in trackedThreads:
                            trackedThread.join()
                            
                    # remove tuples that are non-persistent
                    for condThreadTuple in tuplesToRemove:
                        # if not persistent, after the 
                        self.listCondThreadTuples.remove(condThreadTuple)
                    # because we removed a cond thread tuple, have to update the cond thread description status field
                    self.setCondThreadDescriptionStatusField()
                    
            time.sleep(AtlasI2C_Sensor.COND_THREAD_DELAY)
        
        if(self.debugMode == True):
            self.activityLogManager.addItem("Conditional thread has been terminated")
        return
    
    def terminateCondThread(self):
        
        if self.status.getStatusFieldTupleValueUsingKey("condThreadActive") == True:
            self.status.setStatusFieldTupleValue("condThreadActive", False)
    
    def startContPollThread(self):
        # only start a new thread when there is no existing thread of the same kind
        if (self.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == False):
            self.contPollThread = th.Thread(target=self.contPollThreadTarget)
            self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE, True) # NOTE: It is important that this line of code comes before starting the thread, because the target function expects the flag to be true when it starts
            self.contPollThread.start()
            if self.debugMode == True:
                self.activityLogManager.addItem("Cont Poll Thread started")
        return
            
    def contPollThreadTarget(self):
        while (self.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == True):
            # print("Running the continuous polling thread...")
            
            # get the current time to store as CB entry along with the data value
            current_time = datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S") # timestamp field
            
            if self.contPollThreadAsynchronous == False:
                
                # this if statement is to synchronize between this thread and the conditional thread in order to prevent the continuous polling thread from getting too far ahead
                if(self.condThreadCB.mostRecentValueAccessed == True):
                    currentReading = self.getReading()
                    self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.LATEST_READING, currentReading)
                    if(self.debugMode == True):
                        self.activityLogManager.addItem("Got reading, " + str(currentReading) + ", and adding to CB")
                    with self.CB_Lock:
                        
                        self.condThreadCB.add((currentReading, current_time_str)) # a new sensor reading is added at this point
                        if self.generateMatPlotLibImages == True:
                            latestListCB_Values = self.condThreadCB.getCB_Values()
                            self.activityLogManager.addItem("latestListCB_Values: " + str(latestListCB_Values))
                            self.plotImagesManager.saveListOfVals(latestListCB_Values)
                    
                    # adding the same value to pushToDatabaseCB
                    self.pushToDatabaseQueue.put((currentReading, current_time_str))
            else:
                currentReading = self.getReading()
                self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.LATEST_READING, currentReading)
                if(self.debugMode == True):
                    self.activityLogManager.addItem("Got reading, " + str(currentReading) + ", and adding to CB")
                with self.CB_Lock:
                    self.condThreadCB.add((currentReading, current_time_str)) # a new sensor reading is added at this point
                    
                # adding the same value to pushToDatabaseCB
                self.pushToDatabaseQueue.put((currentReading, current_time_str))
            time.sleep(AtlasI2C_Sensor.SENSOR_GET_READING_DELAY)
        if(self.debugMode == True):
            self.activityLogManager.addItem("Continuous Polling Thread has been terminated")
        
    def terminateContPollThread(self):
        # manually set value of flags to cancel the thread
        if self.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == True:
            self.status.setStatusFieldTupleValue(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE, False)
            self.contPollThread = None
        # wait for the thread target to exit before setting variable value to None
    
    def addStatusToLog(self, update : bool):
        # if true then update both dict and string, if false just update string since dict should have been updated recursively
        if update == True:
            self.status.updateStatusDict()
            self.status.updateStatusString(True)
            self.activityLogManager.addItem(self.status.statusString)
            
    def massGeneratePlotImages(self):
        if self.generateMatPlotLibImages == True:
            self.plotImagesManager.generateAllPlots()
        else:
            Exception("Option for generating plot images was not enabled")

if(__name__ == "__main__"):
    import AtlasI2C_SensorTestCases
    AtlasI2C_SensorTestCases.testCase2()