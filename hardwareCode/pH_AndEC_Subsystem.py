from pPump import PeristalticPump
from AtlasI2C_Sensor import AtlasI2C_Sensor
import threading as th

class pH_AndEC_Subsystem:
    def __init__(self, pH_UpPumpPin, pH_DownPumpPin, baseA_PumpPin, baseB_PumpPin, pH_SensorKeyWord, EC_SensorKeyword, writeDataToCSV : bool):
        self.pH_UpPumpPin = pH_UpPumpPin
        self.pH_DownPumpPin = pH_DownPumpPin
        self.baseA_PumpPin = baseA_PumpPin
        self.baseB_PumpPin = baseB_PumpPin
        self.pH_Sensor = AtlasI2C_Sensor(pH_SensorKeyWord, writeDataToCSV=writeDataToCSV)
        self.EC_Sensor = AtlasI2C_Sensor(EC_SensorKeyword, writeDataToCSV=writeDataToCSV)
    
    def startContPollingThreads(self):
        self.pH_Sensor.startContPollThread()
        self.EC_Sensor.startContPollThread()
        
    def terminateContPollingThreads(self):
        self.pH_Sensor.terminateContPollThread()
        self.EC_Sensor.terminateContPollThread()
        
    def