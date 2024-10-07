"""
AtlasI2C_SensorAndPumps.py

This module provides the class, AtlasI2C_SensorAndPumps, which encapsulates the sensor and pump classes so that they can be treated as one unit.

This class will contain three main things: the sensor object, first pump object, and second pump object (since the pH and EC subsystems individually have two pumps associated with them)

This is the class that will represent the pH and EC subsystems individually. The pH and EC subsystem will be an encapsulation of two instances of this class.

"""

import GPIO_Utility
from pPump import PeristalticPump
import AtlasI2C_Sensor as SensorModule
from Status import Status
import time

# September 11, 2024: I am going to make this class support variable pumps and sensors
class AtlasI2C_SensorAndPumps():
    def __init__(self, alias, pumpA_Pin, pumpA_Alias, pumpB_Pin, pumpB_Alias, sensorKeyWord, writeDataToCSV, debugMode, contPollThreadIndependent, isOutermostEntity):
        
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()
        
        # the status objects of the sensor and pumps already contain most of the information. As of September 13, 2024, this specific status object will just contain the aliases of the sensor and pumps
        
        self.alias = alias # this is just so we know what this sensor and pumps subsystem is, w/o an alias it would be hard to tell
        self.printID = "[" + self.alias + "]: "
        self.pumpList = []
        self.pumpList.append(PeristalticPump(pumpA_Pin, pumpA_Alias, False))
        self.pumpList.append(PeristalticPump(pumpB_Pin, pumpB_Alias, False))
        self.sensor = SensorModule.AtlasI2C_Sensor(sensorKeyWord, writeDataToCSV=writeDataToCSV, debugMode=debugMode, contPollThreadIndependent=contPollThreadIndependent, isOutermostEntity=False)
        self.status = Status(isOutermostEntity, debugMode)
        self.status.addStatusFieldTuple("alias", alias)
        # lower-level status objects will be stored as status objects of higher-level status objects still
        # NOTE: Will not store lower-level status objects as strings or dicts
        self.status.addStatusFieldTuple("sensorStatus", self.sensor.status)
        
        # for the status field tuples involving the pump status objects, the keys will be non-meaningful names such as "pump1", "pump2", etc.
        # the reason for this is because the aliases of the pumps are already in the pump status objects so having their aliases as the keys as well would be redundant
        leftString = "pump"
        num = 1
        rightString = "Status"
        for pump in self.pumpList:
            keyString = leftString + str(num) + rightString
            self.status.addStatusFieldTuple(keyString, pump.status)
            num += 1
        
    def startSystem(self):
        """
        This starts all the threads of the system
        """
        self.startSensorContPollThread()
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
            if(pump.alias == pumpAlias):
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
        
        self.sensor.condThread.join()
        self.sensor.contPollThread.join()
        
        GPIO_Utility.gpioCleanup()
    
def testCase():
    pH_UpPin = 22
    pH_DownPin = 23
    baseA_Pin = 20
    baseB_Pin = 21
    
    sensorAndPumpsSubsystem = AtlasI2C_SensorAndPumps("ec_Subsystem", baseA_Pin, "baseA", baseB_Pin, "baseB", "EC", False, True, False, True)
    
    sensorAndPumpsSubsystem.addToListCondThreadTuplesGeneral(">", 100, False, sensorAndPumpsSubsystem.sensor.turnOnLED_TestCallback, [], "Will turn on LED for 5 seconds and then turn back off")
    sensorAndPumpsSubsystem.addToListCondThreadTuplesPumpDuration(">", 100, "baseA", True, "turn on baseA pump")
    
    sensorAndPumpsSubsystem.status.updateStatusDict()
    sensorAndPumpsSubsystem.status.updateStatusString(includeHorizontalLines=True)
    
    print(sensorAndPumpsSubsystem.status.statusString)
    
    input("Input anything to start cont poll and cond threads: ")
    
    sensorAndPumpsSubsystem.startSensorContPollThread()
    sensorAndPumpsSubsystem.startSensorCondThread()
    
    input("Input anything to end program: ")

    sensorAndPumpsSubsystem.shutDownSystem()

    exit()
    
if __name__ == "__main__":
    testCase()