import time
import threading as th



class Status:
    
    class FieldKeys:
        ALIAS = "alias"
    
    def __init__(self, alias, isTopLevel : bool, debugModeOn : bool):
        """
        Initialize a Status class object.
        
        :param alias: This will be one of the tuples that the tuples list will be initialized with (Makes sense that each Status object has the alias of the entity it is a status of)
        :param topLevel: True if this status is the outermost status, False if not (this is used for proper function of some methods), won't be a part of tuples
        :param debugModeOn: If true, will print out statements regarding some things happening within the status object, won't be a part of tuples
        """
        self.statusFieldTuples = [] # empty list, will be populated with two-tuples (i.e., (statusFieldKey, statusFieldValue))
        
        # these attributes will reflect the list of status field tuples
        self.statusDict = {} # directly derived from the list of status field tuples, empty dict initially
        self.statusString = None # directly derived from the statusDict
        
        self.debugMode = debugModeOn
        
        # flag for indicating that a status field value got changed
        # NOTE: Only accounts for changes in the current status level, sub status objects won't be accounted for (so basically this applies for all current level status field tuples that aren't status objects)
        self.statusFieldTuplesModified = False
        
        # initialize the tuples
        fieldKeys = [value for key, value in Status.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            self.addStatusFieldTuple(fieldKey, None)
        
        self.setStatusFieldTupleValue(Status.FieldKeys.ALIAS, alias) # The first tuple of the tuple list
        
        # this is the thread that will use the status field value got changed flag to update the corresponding status dict and string
        # NOTE: This is a recursive function so only run this thread on the upper-most level
        self.autoUpdateStatusDictAndStringThread = None
        self.autoUpdateStatusDictAndStringThreadActive = False # false initially
        
        # the point of this flag is to determine whether the autoUpdateStatusDictAndStringThreadTarget can be started from the current status object or not, since should only run this on the top-most level status object 
        self.isTopLevelStatusObject = isTopLevel
    
    @classmethod
    def init_from_dict(cls, dict):
        """
        The dict should contain the necessary key:value pairs
        """
        # will be attributes of the status class
        isTopLevelStatusObject = dict["isTopLevelStatusObject"]
        debugModeOn = dict["debugModeOn"]
        
        # will be tuples of the tuple list
        alias = dict[Status.FieldKeys.ALIAS]
        return Status(alias,isTopLevelStatusObject,debugModeOn)
        
       
    def autoUpdateStatusDictAndStringThreadTarget(self):
        while self.autoUpdateStatusDictAndStringThreadActive == True:
            self.updateStatusDict()
            self.updateStatusString(True)
            time.sleep(0.5)
            
        if self.debugMode == True:
            print("autoUpdateStatusDictAndStringThread terminated")
            
        return
        
    def startAutoUpdateStatusDictAndStringThread(self):
        """
        The thread should only be started after there exist status field tuples in the corresponding instance
        """
        if self.autoUpdateStatusDictAndStringThreadActive == False and self.isTopLevelStatusObject == True:
            self.autoUpdateStatusDictAndStringThread = th.Thread(target=self.autoUpdateStatusDictAndStringThreadTarget)
            self.autoUpdateStatusDictAndStringThreadActive = True
            self.autoUpdateStatusDictAndStringThread.start()
        else:
            raise Exception("Could not start autoUpdateStatusDictAndStringThread")
        
    def terminateAutoUpdateStatusDictAndStringThread(self):
        if self.autoUpdateStatusDictAndStringThreadActive == True:
            self.autoUpdateStatusDictAndStringThreadActive = False # setting this to false exits the while loop of the target
            
        else:
            raise Exception("Could not terminate autoUpdateStatusDictAndStringThread, check thread variables")
        
    def getStatusFieldTupleUsingKey(self, statusFieldKey):
        
        foundStatusFieldTuple = None
        
        for statusFieldTuple in self.statusFieldTuples:
            if statusFieldTuple[0] == statusFieldKey:
                foundStatusFieldTuple = statusFieldTuple
                break
        
        # if can't find a tuple given key, will return none
        if foundStatusFieldTuple != None:
            return foundStatusFieldTuple
        else:
            raise Exception("Could not locate status field tuple from given key")
        
    def addStatusFieldTuple(self, statusFieldKey, statusFieldValue):
        
        keyAlreadyExist = False # assume false initially
        
        try:
            self.getStatusFieldTupleUsingKey(statusFieldKey)
            # if this runs successfully, it means duplicate
            keyAlreadyExist = True
            raise Exception("Tried adding tuple with duplicate key")
        except Exception as e:
            keyAlreadyExist = False # for sure false
            newStatusFieldTuple = [statusFieldKey, statusFieldValue]
            self.statusFieldTuples.append(newStatusFieldTuple)
            self.statusFieldTuplesModified = True
            
        
    def removeStatusFieldTupleUsingKey(self, statusFieldKey):
        foundStatusFieldTuple = self.getStatusFieldTupleUsingKey(statusFieldKey)
        
        self.statusFieldTuples.remove(foundStatusFieldTuple)
        
        self.statusFieldTuplesModified = True
        
    def getStatusFieldTupleValueUsingKey(self, statusFieldKey):
        """
        Need the status field key in order to get the status field value
        """
        
        foundStatusFieldTuple = self.getStatusFieldTupleUsingKey(statusFieldKey)
        
        return foundStatusFieldTuple[1] # since index 1 of the tuple houses the status field value
    
    def setStatusFieldTupleValue(self, statusFieldKey, newValue):
        
        foundStatusFieldTuple = self.getStatusFieldTupleUsingKey(statusFieldKey)
        
        foundStatusFieldTuple[1] = newValue
        self.statusFieldTuplesModified = True
        
        return
    
    def updateStatusDict(self) -> None:
        """
        The dict will be generated from the tuples list. Will update the dicts of all sub-status that are included as values
        
        NOTE: For sub status objects, their status dicts will also be updated. Afterwards, their dict will be assigned a value of the outer dict
        
        NOTE: Only have to run this at the top-most level, same with updateStatusString. Also, only run this when you want to update the dict specifically (e.g., when you want to export status data or generate the most up to date status string). The function of the sensor and pumps will not be affected if the dict or string is not updated
        """
        
        for statusFieldTuple in self.statusFieldTuples:
            statusFieldKey = statusFieldTuple[0]
            statusFieldValue = statusFieldTuple[1]
            # this is for a sub-status object
            if isinstance(statusFieldValue, Status):
                statusObject = statusFieldValue
                statusObject.updateStatusDict() # recursion
                self.statusDict[statusFieldKey] = statusObject.statusDict
            else:
                if self.statusFieldTuplesModified == True:
                    self.statusDict[statusFieldKey] = statusFieldValue
        self.statusFieldTuplesModified = False # Reset the flag for the current level status object
    
    def updateStatusStringRecursion(self, keyValuePairKey, keyValuePairValue, level) -> None:
        self.statusString += "\n"
        for i in range(0, level):
            self.statusString += "\t"
        self.statusString += str(keyValuePairKey) + ": "
        if isinstance(keyValuePairValue, dict):
            for keyValuePairKey1, keyValuePairValue1 in keyValuePairValue.items():
                self.updateStatusStringRecursion(keyValuePairKey1, keyValuePairValue1, level+1)
        else:
            self.statusString += str(keyValuePairValue) # terminating condition
    
    def updateStatusString(self, includeHorizontalLines : bool):
        """
        Make sure that the status dict is updated before running this method since the contents of the status string will be based on the current state of that
        """
        
        if len(self.statusDict) >= 1:
            self.statusString = "" # reset the status string first
            
            if includeHorizontalLines == True:
                self.statusString += "---------------------------------------------"
                
            for key, value in self.statusDict.items():
                
                # self.statusString += "\n" + str(key) + ": "
                self.updateStatusStringRecursion(key, value, 0)
                    
            if includeHorizontalLines == True:
                self.statusString += "\n---------------------------------------------"
        else:
            self.statusString = "Status dict empty right now"
            if self.debugMode == True:
                print("Empty dict currently")
    
    def returnAutoUpdatedStatusString(self):
        if self.autoUpdateStatusDictAndStringThreadActive:
            return self.statusString
        else:
            raise Exception("The auto update thread is not active")
    
if __name__ == "__main__":
    # Import from test cases to test
    from StatusTestCases import StatusTestCases
    
    StatusTestCases.threadTestCase()
    
    exit()
