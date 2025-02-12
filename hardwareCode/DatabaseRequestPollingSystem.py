from MenuManagementSystem import MenuManagementSystem
from MYSQL import retrieve_most_recent_command, retrieve_most_recent_arguments
import threading
import time
from Status import Status

class DatabaseRequestPollingSystem:
    
    class FieldKeys(Status.FieldKeys):
        REQUEST_POLLING_THREAD_ACTIVE = "requestPollingThreadActive"
        DEBUG_RETRIEVAL = "debugRetrieval"
        
    def __init__(self, menu_management_system : MenuManagementSystem, statusArgsDict):
        if menu_management_system == None:
            raise Exception("Menu Management System is none")
        self.menu_management_system = menu_management_system
        
        # thread variables
        self.pollingThreadActive = False
        self.pollingThread = None
        
        self.status : Status = Status.init_from_dict(statusArgsDict)
        
        # add additional field keys
        fieldKeys = [value for key, value in DatabaseRequestPollingSystem.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            self.status.addStatusFieldTuple(fieldKey, None)
            
        self.status.setStatusFieldTupleValue(DatabaseRequestPollingSystem.FieldKeys.REQUEST_POLLING_THREAD_ACTIVE, False)
        
        self.status.setStatusFieldTupleValue(DatabaseRequestPollingSystem.FieldKeys.DEBUG_RETRIEVAL, False) # Will initialize as false, have to turn it on for debug
    
    def retrieveCommand(self):
        
        # using MYSQL API functions to get most recent commands and arguments 
        command = retrieve_most_recent_command()
        arguments = retrieve_most_recent_arguments()
        
        # countermeasure
        for i in range(0, len(arguments)):
            if arguments[i] == 'self':
                arguments.pop(i)
                break # expecting at most one instance of 'self'

        if self.status.getStatusFieldTupleValueUsingKey(DatabaseRequestPollingSystem.FieldKeys.DEBUG_RETRIEVAL) == True:
            print("Won't enqueue command, just retrieving")
            print(f"Retrieved Command: {command}, Retrieved Arguments: {arguments}")
        else:
            self.menu_management_system.enqueue_command(command, *arguments)

        # this supports at most 3 arguments
        # if len(arguments) == 1:
        #     self.menu_management_system.enqueue_command(command, arguments[0])
        #     print("Arguments: 1")
        # elif len(arguments) == 2:
        #     self.menu_management_system.enqueue_command(command, arguments[0], arguments[1])
        #     print("Arguments: 2")
        # elif len(arguments) == 3:
        #     self.menu_management_system.enqueue_command(command, arguments[0], arguments[1], arguments[2])
        #     print("Arguments: 3")
        # else:
        #     self.menu_management_system.enqueue_command(command)
        #     print("Arguments: 0")

    def polling_thread_target(self):
        while self.pollingThreadActive:
            self.retrieveCommand()
            time.sleep(5)

    def start_polling_thread(self):
        if not self.pollingThreadActive:
            self.pollingThread = threading.Thread(target=self.polling_thread_target, daemon=True) # use daemon for insurance
            self.pollingThreadActive = True
            self.pollingThread.start()

    def terminate_polling_thread(self):
        if self.pollingThreadActive:
            self.pollingThreadActive = False
            self.pollingThread.join() # wait to join
            self.pollingThread = None


if __name__ == "__main__":
    import DatabaseRequestPollingSystemTestCases
    
    DatabaseRequestPollingSystemTestCases.test_poll_thread_debug()
    
    exit()