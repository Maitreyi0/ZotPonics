import json
from CircularBuffer import CircularBuffer as CB

# The objects of this class are meant to be written into a text file for another program to read
class AtlasI2C_SubsystemData():
    
    pH_DataJsonPath = "pH_data.json"
    
    ec_DataJsonPath = "ec_data.json"
    
    def __init__(self, deviceKeyword, CB, condThreadIsActive, contPollThreadIsActive):
        self.deviceKeyword = deviceKeyword
        self.CB = CB
        self.condThreadIsActive = condThreadIsActive
        self.contPollThreadIsActive = contPollThreadIsActive
        
    def toDict(self):
        return {
            "deviceKeyword": self.deviceKeyword,
            "CB": self.CB.toDict(),
            "condThreadIsActive": self.condThreadIsActive,
            "contPollThreadIsActive": self.contPollThreadIsActive
        }
        
    # filePath should be for one of the json files of the sensor objects
    def readJsonReturnObj(filePath):
        jsonFile = open(filePath, "r")
        
        jsonDict = json.load(jsonFile)
        
        jsonFile.close()
        
        deviceKeyword = jsonDict["deviceKeyword"]
        CB_Size = jsonDict["CB"]["size"]
        CB_Buffer = jsonDict["CB"]["buffer"]
        CB_Index = jsonDict["CB"]["index"]
        CB_CurrentSize = jsonDict["CB"]["currentSize"]
        condThreadIsActive = jsonDict["condThreadIsActive"]
        contPollThreadIsActive = jsonDict["contPollThreadIsActive"]
        
        CB_Object = CB()
        
def writeDataToFile(self):
        AtlasI2C_SubsystemDataObject = AtlasI2C_SubsystemData(self)
        
        outputFile = open(self.dataFilePath, "w")
        
        json.dump(AtlasI2C_SubsystemDataObject.toDict(), outputFile)
        
        outputFile.close()