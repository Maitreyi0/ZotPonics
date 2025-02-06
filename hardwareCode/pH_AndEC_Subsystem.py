from hardwareCode.PeristalticPump import PeristalticPump
from AtlasI2C_Sensor import AtlasI2C_Sensor
import threading as th
import GPIO_Utility
from Status import Status
from AtlasI2C_SensorAndPumps import AtlasI2C_SensorAndPumps
import pdb

class pH_AndEC_Subsystem:
    def __init__(self, alias, pH_SubsystemAlias, EC_SubsystemAlias, pH_UpPumpAlias, pH_UpPumpPin, pH_DownPumpAlias, pH_DownPumpPin, baseA_PumpAlias, baseA_PumpPin, baseB_PumpAlias, baseB_PumpPin, pH_SensorKeyWord, EC_SensorKeyword, contPollThreadIndependent, writeDataToCSV : bool, debugMode, isOutermostEntity, generateMatPlotLibImages):
        
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()
        
        self.pH_UpPumpPin = pH_UpPumpPin
        self.pH_DownPumpPin = pH_DownPumpPin
        self.baseA_PumpPin = baseA_PumpPin
        self.baseB_PumpPin = baseB_PumpPin
        
        # initialize pH Subsystem
        self.pH_Subsystem = AtlasI2C_SensorAndPumps(alias=pH_SubsystemAlias, pumpA_Pin=pH_UpPumpPin, pumpA_Alias=pH_UpPumpAlias, pumpB_Pin=pH_DownPumpPin, pumpB_Alias=pH_DownPumpAlias, sensorKeyWord=pH_SensorKeyWord, writeDataToCSV=writeDataToCSV, debugMode=debugMode, contPollThreadIndependent=contPollThreadIndependent, isOutermostEntity=False, generateMatPlotLibImages=generateMatPlotLibImages, sensorAlias="phSensor")
        
        # initialize EC Subsystem
        self.EC_Subsystem = AtlasI2C_SensorAndPumps(alias=EC_SubsystemAlias, pumpA_Pin=baseA_PumpPin, pumpA_Alias=baseA_PumpAlias, pumpB_Pin=baseB_PumpPin, pumpB_Alias=baseB_PumpAlias, sensorKeyWord=EC_SensorKeyword, writeDataToCSV=writeDataToCSV, debugMode=debugMode, contPollThreadIndependent=contPollThreadIndependent, isOutermostEntity=False, generateMatPlotLibImages=generateMatPlotLibImages, sensorAlias="ecSubsystem")
        
        # intiailize Status object
        self.status = Status(isOutermostEntity, debugMode)
        self.status.addStatusFieldTuple("alias", alias)
        self.status.addStatusFieldTuple("pH Subsystem Status", self.pH_Subsystem.status)
        self.status.addStatusFieldTuple("EC Subsystem Status", self.EC_Subsystem.status)
    
    def startSubSystems(self, subsystem, option):
        """_summary_

        Args:
            subsystem (_String_): Will be "all", "pH", or "EC"
            option (_String_): Will be "contPoll", "cond", "all"
        """
        if subsystem == "all":
            self.pH_Subsystem.startSystem(option)
            self.EC_Subsystem.startSystem(option)
        elif subsystem == "pH":
            self.pH_Subsystem.startSystem(option)
        elif subsystem == "EC":
            self.EC_Subsystem.startSystem(option)
        else:
            raise Exception("Invalid option for starting subsystems")
        
    def shutdownSubSystems(self):
        self.pH_Subsystem.shutDownSystem()
        self.EC_Subsystem.shutDownSystem()
        
    def addToListCondThreadTuplesPumpDuration(self, subsystemAlias, comparator, rightOperand, pumpAlias, isPersistent, description):
        subsystemOfInterest = None
        if subsystemAlias == self.pH_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.pH_Subsystem
        elif subsystemAlias == self.EC_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.EC_Subsystem
        else:
            raise Exception("Issue adding cond thread tuple, invalid subsystem alias")
        
        subsystemOfInterest.addToListCondThreadTuplesPumpDuration(comparator, rightOperand, pumpAlias, isPersistent, description)
        
    def addToListCondThreadTuplesGeneral(self, subsystemAlias, comparator, rightOperand, isPersistent, callback, callbackArgsList : list,description):
        subsystemOfInterest = None
        if subsystemAlias == self.pH_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.pH_Subsystem
        elif subsystemAlias == self.EC_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.EC_Subsystem
        else:
            raise Exception("Issue adding cond thread tuple, invalid subsystem alias")
        
        subsystemOfInterest.addToListCondThreadTuplesGeneral(comparator, rightOperand, isPersistent, callback, callbackArgsList, description)
        
    def removeFromListCondThreadTuples(self, subsystemAlias, condThreadTupleAlias):
        subsystemOfInterest = None
        if subsystemAlias == self.pH_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.pH_Subsystem
        elif subsystemAlias == self.EC_Subsystem.status.getStatusFieldTupleValue("alias"):
            subsystemOfInterest = self.EC_Subsystem
        else:
            raise Exception("Issue adding cond thread tuple, invalid subsystem alias")
        
        subsystemOfInterest.sensor.removeFromListCondThreadTuples(condThreadTupleAlias)
        
    def turnOnPumpWithDuration(self, alias, seconds):
        pumpOfInterest = None
        pumpOfInterestFound = False # assume false initially
        for pump in self.pH_Subsystem.pumpList:
            if pump.status.getStatusFieldTupleValue("alias") == alias:
                pumpOfInterest = pump
                pumpOfInterestFound = True
                break
        if pumpOfInterestFound == False:
            for pump in self.EC_Subsystem.pumpList:
                if pump.status.getStatusFieldTupleValue("alias") == alias:
                    pumpOfInterest = pump
                    pumpOfInterestFound = True
                    break
        
        if pumpOfInterestFound == True:
            pumpOfInterest.turnOnWithDuration(seconds)
        else:
            raise Exception("Could not locate pump with matching alias")

    def interruptThreadHandling(self):
        """
        This is for when an exception is thrown. Active threads must be stopped before
        """
        self.shutdownSubSystems()
            
        
        
        
def testCase():
    
    # try:
    pH_UpPin = 22
    pH_DownPin = 23
    baseA_Pin = 20
    baseB_Pin = 21
    
    enableThreads = True
    
    PH_SENSOR_KEY_WORD = "pH"
    EC_SENSOR_KEY_WORD = "EC"
    pH_SubsystemAlias = "pH_Subsystem"
    ecSubsystemAlias = "ecSubsystem"
    
    # initialize the pH and EC Subsystem object 
    pH_AndEC_SubsystemObj = pH_AndEC_Subsystem(alias="pHandEC_Subsystem", pH_SubsystemAlias="pH_Subsystem", EC_SubsystemAlias="ecSubsystem", pH_UpPumpAlias="pH_UpPump", pH_UpPumpPin=pH_UpPin, pH_DownPumpAlias="pH_DownPump", pH_DownPumpPin=pH_DownPin, baseA_PumpAlias="baseA_Pump", baseA_PumpPin=baseA_Pin, baseB_PumpAlias="baseB_Pump", baseB_PumpPin=baseB_Pin, pH_SensorKeyWord=PH_SENSOR_KEY_WORD, EC_SensorKeyword=EC_SENSOR_KEY_WORD, contPollThreadIndependent=False, writeDataToCSV=False, debugMode=True, isOutermostEntity=True, generateMatPlotLibImages=True)
    
    input("Input anything to add cond threads for pH Up and Down: ")
    
    # add to list of cond thread tuples
    # this will test
    # pH_AndEC_SubsystemObj.addToListCondThreadTuplesPumpDuration(pH_SubsystemAlias, ">", 3, "pH_DownPump", True, "As long as pH is above 5, keep dispensing pH Down solution")
    
    # pH_AndEC_SubsystemObj.addToListCondThreadTuplesPumpDuration(pH_SubsystemAlias, "<", 9, "pH_UpPump", True, "As long as pH is below 5, keep dispensing pH Up solution")
    
    if enableThreads:
        input("Input anything to turn on continuous polling and conditional threads: ")
        pH_AndEC_SubsystemObj.startSubSystems("pH", "all")
    
    input("Input anything to shut down system and exit program: ")
    
    pH_AndEC_SubsystemObj.status.updateStatusDict()
    pH_AndEC_SubsystemObj.status.updateStatusString(includeHorizontalLines=True)
    print("Status right before program end")
    print(pH_AndEC_SubsystemObj.status.statusString)
    if enableThreads:
        pH_AndEC_SubsystemObj.shutdownSubSystems()
        
    pH_AndEC_SubsystemObj.pH_Subsystem.sensor.plotImagesManager.generateAllPlots()
            
    # except KeyboardInterrupt:
    #     print("\nKeyboard Interrupt detected")
    #     pH_AndEC_SubsystemObj.interruptThreadHandling()
    # finally:
    #     GPIO_Utility.gpioCleanup()
    #     exit()
            
if __name__ == "__main__":
    # pdb.set_trace()
    testCase()