"""
AtlasI2C_SensorAndPumps.py

This module provides the class, AtlasI2C_SensorAndPumps, which encapsulates the sensor and pump classes so that they can be treated as one unit.

This class will contain three main things: the sensor object, first pump object, and second pump object (since the pH and EC subsystems individually have two pumps associated with them)

This is the class that will represent the pH and EC subsystems individually. The pH and EC subsystem will be an encapsulation of two instances of this class.

"""

import GPIO_Utility
from hardwareCode.PeristalticPump import PeristalticPump
import AtlasI2C_Sensor as SensorModule
from Status import Status
import time
import AtlasI2C_SensorAndPumpsTestCases
from AtlasI2C_Sensor import AtlasI2C_Sensor
from FileOutputManagementSystem import FileOutputManagementSystem

PeristalticPump()

# September 11, 2024: I am going to make this class support variable pumps and sensors
class AtlasI2C_SensorAndPumps():
    def __init__(self, alias, sensor, pumpsList, debugMode, isOutermostEntity):
        """
        Initializes the AtlasI2C_SensorAndPumps class with pre-created sensor and pump objects.
        
        Args:
            alias (str): Alias for this system.
            sensor (AtlasI2C_Sensor): Pre-created sensor object.
            pumps (list): List of pre-created PeristalticPump objects.
            debugMode (bool): Flag for enabling debug mode.
            isOutermostEntity (bool): Flag to indicate if this is the outermost entity.
        """
        
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()

        self.printID = "[" + alias + "]: "
        self.pumpList = pumpsList  # Use the provided list of pump objects
        self.sensor = sensor   # Use the provided sensor object
        self.status = Status(isOutermostEntity, debugMode)
        
        # Set status fields
        self.status.addStatusFieldTuple("alias", alias)
        self.status.addStatusFieldTuple("sensorStatus", self.sensor.status)
        
        # Add pump status objects to the status field
        leftString = "pump"
        num = 1
        rightString = "Status"
        for pump in self.pumpList:
            keyString = leftString + str(num) + rightString
            self.status.addStatusFieldTuple(keyString, pump.status)
            num += 1
        
    def startSystem(self, option):
        """
        This starts all the threads of the system
        Args:
            option (_String_): Will be "contPoll", "cond", or "all"
        """
        if option == "all":
            self.startSensorContPollThread()
            self.startSensorCondThread()
        elif option == "contPoll":
            self.startSensorContPollThread()
        elif option == "cond":
            self.startSensorCondThread()
        
    def terminateSystem(self):
        """
        This ends all the threads of the system
        """
        self.terminateSensorContPollThread()
        self.terminateSensorCondThread()
        
    def startSensorContPollThread(self):
        self.sensor.startContPollThread()
        
    def terminateSensorContPollThread(self):
        self.sensor.terminateContPollThread()
        
    def startSensorCondThread(self):
        self.sensor.startCondThread()
        
    def terminateSensorCondThread(self):
        self.sensor.terminateCondThread()
        
    def addToListCondThreadTuplesGeneral(self, comparator, rightOperand, isPersistent, callback, callbackArgsList : list, description):
        
        newCondThreadTupleDescription = description
        
        self.sensor.addToListCondThreadTuples(comparator, rightOperand, callback, callbackArgsList, isPersistent, newCondThreadTupleDescription)
    
    # pump callback functions
    def addToListCondThreadTuplesPumpDuration(self, comparator, rightOperand, pumpAlias, isPersistent, description):
        """
        This will add a condition thread tuple with the callback function being onWithDuration of a Pump class object. Each pump duration condition thread tuple can be for different pumps.
        """
        pumpOfInterest = None
        for pump in self.pumpList:
            if(pump.status.getStatusFieldTupleValue("alias") == pumpAlias):
                pumpOfInterest = pump
                break
        if pumpOfInterest == None:
            raise Exception(self.printID + "Could not locate pump of interest for adding onWithDuration as cond thread tuple callback")
        else:
            # we can change the number of seconds the pumps are turned on for but will do this via another method
            
            newCondThreadTupleDescription = description
            
            self.sensor.addToListCondThreadTuples(comparator, rightOperand, pumpOfInterest.turnOnWithDuration, [pumpOfInterest.onWithDurationSeconds], isPersistent, newCondThreadTupleDescription)

    
    def removeFromListCondThreadTuples(self, alias):
        self.sensor.removeFromListCondThreadTuples(alias)
        
    def shutDownSystem(self):
        self.terminateSensorContPollThread()
        self.terminateSensorCondThread()
        
    def turnOnPumpWithDuration(self, alias, seconds):
        pumpOfInterest = None
        for pump in self.pumpList:
            if(pump.status.getStatusFieldTupleValue("alias") == alias):
                pumpOfInterest = pump
                break
        if pumpOfInterest == None:
            raise Exception(self.printID + "Could not locate pump of interest for adding onWithDuration as cond thread tuple callback")
        else:
            pumpOfInterest.turnOnWithDuration(seconds)
    
    def addStandardLowerBoundPumpCondition(self, val, pumpAlias):
        self.addToListCondThreadTuplesPumpDuration(comparator="<", rightOperand=val, pumpAlias=pumpAlias, isPersistent=True, description=f"lessThan{val}")
        
    def addStandardUpperBoundPumpCondition(self, val, pumpAlias):
        self.addToListCondThreadTuplesPumpDuration(comparator=">", rightOperand=val, pumpAlias=pumpAlias, isPersistent=True, description=f"greaterThan{val}")
    
if __name__ == "__main__":
    
    GPIO_Utility.setModeBCM()
    
    # this test case tests for pH
    
    pH_UpPin = 22
    pH_DownPin = 23
    baseA_Pin = 20
    baseB_Pin = 21
    
    pumpsList = []
    pumpsList.append(PeristalticPump(pH_DownPin, "phDown", False, False))
    pumpsList.append(PeristalticPump(pH_UpPin, "phUp", False, False))
    
    fileOutputManagementSystem = FileOutputManagementSystem(fileName="AtlasI2C_SensorAndPumps.log", includeTimeStamp=True)
    
    sensorOptions = [AtlasI2C_Sensor.PH_SENSOR_KEY_WORD, AtlasI2C_Sensor.EC_SENSOR_KEY_WORD]
    sensorKeyWord = sensorOptions[0]
    sensor = AtlasI2C_Sensor(sensorKeyWord, debugMode=True, contPollThreadIndependent=False, isOutermostEntity=False, generateMatPlotLibImages=True, alias="AtlasI2C_Sensor", fileOutputManagementSystem=fileOutputManagementSystem)
    
    sensorAndPumpsSubsystem = AtlasI2C_SensorAndPumps(alias="phSubsystem", sensor=sensor, pumpsList=pumpsList, debugMode=True, isOutermostEntity=True)
    
    input("Input anything to start cont poll and cond threads: ")
    sensorAndPumpsSubsystem.startSensorContPollThread()
    sensorAndPumpsSubsystem.startSensorCondThread()
    
    input("Input anything to add pump cond thread tuple (lessThan9) to list: ")
    sensorAndPumpsSubsystem.addStandardLowerBoundPumpCondition(val=9, pumpAlias="phUp")
    sensorAndPumpsSubsystem.sensor.addStatusToLog(update=True)
    
    input("Input anything to remove lessThan9 from list: ")
    sensor.removeFromListCondThreadTuples("lessThan9")
    sensor.addStatusToLog(update=True)
    
    time.sleep(2) # delay to allow the callback to trigger before the input statement
    input("Input anything to terminate cont poll and cond thread and end program: ")
    
    sensor.terminateContPollThread()
    sensor.terminateCondThread()
    sensor.addStatusToLog(update=True)
    
    sensor.activityLogManager.massWriteQueueToFile()
    sensor.massGeneratePlotImages()

    sensorAndPumpsSubsystem.shutDownSystem()
    
    
    GPIO_Utility.gpioCleanup()