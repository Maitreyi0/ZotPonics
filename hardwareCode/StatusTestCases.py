from Status import Status

class StatusTestCases:
    
    @classmethod
    def generateListOfMethodNames(cls):
        # Initialize the status args dict
        statusArgsDict = {}
        statusArgsDict["alias"] = "status"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        status = Status.init_from_dict(statusArgsDict)
        
        methodsToAddAsOptionsStatus = [
            status.startAutoUpdateStatusDictAndStringThread,
            status.terminateAutoUpdateStatusDictAndStringThread,
            status.returnAutoUpdatedStatusString
        ]
    
    @classmethod
    # cls is needed for how calling from class works
    def initFromDictAndPrint(cls):
        statusArgsDict = {}
        statusArgsDict["alias"] = "statusObject"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        status : Status = Status.init_from_dict(statusArgsDict)
        status.addStatusFieldTuple("Field1", "Val1")
        status.addStatusFieldTuple("Field2", "Val2")
        status.addStatusFieldTuple("Field3", "Val3")
        
        status.updateStatusDict()
        status.updateStatusString(includeHorizontalLines=True)
        print(status.statusString)
    
    @classmethod
    def threadTestCase(cls):
        import time
        
        statusArgsDict = {}
        statusArgsDict["alias"] = "statusObject"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        status : Status = Status.init_from_dict(statusArgsDict)

        print("Status string immediately after initialization and initial manual dict and string updates: ")
        status.updateStatusDict()
        status.updateStatusString(includeHorizontalLines=True)
        print(status.statusString)
        print("Adding two status fields and not performing manual dict and string updates...")
        status.addStatusFieldTuple("testKey1", "testValue1")
        status.addStatusFieldTuple("testKey2", "testValue2")
        print("Re-printing status string, should be the same as previous: ")
        print(status.statusString)
        print("Starting the auto update thread (from this point on in the test case, won't perform manual updates anymore)...")
        status.startAutoUpdateStatusDictAndStringThread()
        time.sleep(1)
        print("Should now be different status string: ")
        print(status.statusString)
        newVal = input("Input something to modify testKey2's value with: ")
        status.setStatusFieldTupleValue("testKey2", newVal)
        time.sleep(1)
        print("New status string: ")
        print(status.statusString) # Only printing because assume that the dict and string attributes are automatically updated
        
        input("Input anything to create another status object called subStatusObject: ")
        
        subStatusArgsDict = {}
        subStatusArgsDict["alias"] = "subStatusObject"
        subStatusArgsDict["isTopLevelStatusObject"] = False
        subStatusArgsDict["debugModeOn"] = True
        
        status_sub : Status = Status.init_from_dict(subStatusArgsDict)
        
        print("Adding some fields to subStatusObject...")
        status_sub.addStatusFieldTuple("field1", "cd")
        status_sub.addStatusFieldTuple("field2", "gh")
        print("Adding the sub status object as a field to the overall status object...")
        status.addStatusFieldTuple("status1", status_sub)
        time.sleep(1)
        print("Final Overall Status String: ")
        print(status.statusString)
        
        status.terminateAutoUpdateStatusDictAndStringThread()