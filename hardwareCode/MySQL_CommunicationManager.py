from MenuManagementSystem import MenuManagementSystem
from CircularBuffer import CircularBuffer
import mysql.connector
from mysql.connector import Error
import MySQLdb
import sshtunnel
import time
import json
import threading
from Status import Status
from PeristalticPump import PeristalticPump
from PumpWater import PumpWater
from queue import Queue
from PiCamera import PiCamera

# We will access the remote host via an SSH tunnel (think of it like a proxy/intermediate point we are connecting to before connecting to our actual destination)
class MySQL_ConnectionInformation:
    def __init__(self, ssh_host, ssh_user, ssh_pass, remote_bind_address, remote_host, remote_port, db_user, db_pass, db_name):
        """
        This is just an information storage class
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.remote_bind_address = remote_bind_address
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

class MySQL_ServerCommunicationManager:
    def __init__(self, mySQL_ConnectionInformation : MySQL_ConnectionInformation, menu_management_system : MenuManagementSystem, database_pH_values_queue : Queue, database_EC_values_queue : Queue, pH_UpPumpStatus : Status, pH_DownPumpStatus : Status, baseA_PumpStatus : Status, baseB_PumpStatus : Status, doPerformEnqueue, pumpWaterStatus : Status, overallSystemStatus : Status, piCamera : PiCamera):
        """
        The existence of this class will help contain all the threads related to communicating with the MySQL database
        
        @param
        menu_management_system: Need this to initialize the thread to start polling requests from the Requests table in the database and using menu_management_system.enqueue_command to enqueue it
        
        @param
        database_pH_values_circular_buffer: Need this to initialize the thread to start periodically putting new values from it in the pH_values table in the database
        
        @param
        database_EC_values_circular_buffer: Need this to initialize the thread to start periodically putting new values from it in the EC_values table in the database
        
        @param
        db_name: The name of the specific database on the MySQL server you want to connect to
        """
        
        self.mySQL_ConnectionInformation = mySQL_ConnectionInformation
        
        self.menu_management_system = menu_management_system
        
        self.database_pH_values_queue = database_pH_values_queue
        
        self.database_EC_values_queue = database_EC_values_queue
        
        self.pH_UpPumpStatus = pH_UpPumpStatus
        self.pH_DownPumpStatus = pH_DownPumpStatus
        self.baseA_PumpStatus = baseA_PumpStatus
        self.baseB_PumpStatus = baseB_PumpStatus
        self.pumpWaterStatus = pumpWaterStatus
        self.overallSystemStatus = overallSystemStatus # We assume that overallSystem object is created first then we create the communication manager with overallSystemStatus 
        
        self.piCamera = piCamera # needed for the capture and insert image thread
        
        self.requestPollingThread = None
        self.requestPollingThreadActive = False
        
        # will use one thread to control this but doesn't necessarily have to upload both pH and EC data at the same time
        # whether it does or not depends on whether the circular_buffer attributes are None or not
        self.insertPH_AndEC_DataThread = None
        self.insertPH_AndEC_DataThreadActive = False
        
        self.insertPeristalticPumpStatusThread = None
        self.insertPeristalticPumpStatusThreadActive = False
        
        self.captureAndInsertImageThread = None
        self.captureAndInsertImageThreadActive = False
        
        self.insertStatusThread = None
        self.insertStatusThreadActive = False
        
        # This will store the connection object
        self.conn = None
        # This will store the connection cursor object
        self.cursor = None
        
        self.doPerformEnqueue = doPerformEnqueue
      
    def startCaptureAndInsertImageThread(self):
        if self.captureAndInsertImageThreadActive == False and self.captureAndInsertImageThread == None:
            self.captureAndInsertImageThreadActive = True
            self.captureAndInsertImageThread = threading.Thread(target=self.captureAndInsertImageThreadTarget, daemon=True)
            self.captureAndInsertImageThread.start()
        
    def captureAndInsertImageThreadTarget(self):
        """
        The capturing portion will call the camera's method
        """
        while self.captureAndInsertImageThreadActive == True:
            # Capture the image first
            if self.piCamera != None:
                self.piCamera.capture_image("imageCapture.jpg") # stored in captured_images dir by default
                
                # NEED TO IMPLEMENT STILL
                self.uploadImageToDatabase()
            
            time.sleep(1) # Timeout
            
    def terminateCaptureAndInsertImageThreadTarget(self):
        if self.captureAndInsertImageThreadActive == True and self.captureAndInsertImageThread != None:
            self.captureAndInsertImageThreadActive = False
            self.captureAndInsertImageThread.join()
            self.captureAndInsertImageThread = None
        
    def uploadImageToDatabase(self):
        NotImplemented
      
    def startInsertPH_AndEC_DataThread(self):
        if self.insertPH_AndEC_DataThreadActive == False and self.insertPH_AndEC_DataThread == None:
            self.insertPH_AndEC_DataThreadActive = True
            self.insertPH_AndEC_DataThread = threading.Thread(target=self.insertPH_AndEC_DataThreadTarget, daemon=True)
            self.insertPH_AndEC_DataThread.start()
        else:
            print("Could not start insertPH_AndEC_DataThread")
    
    def terminateInsertPH_AndEC_DataThread(self):
        if self.insertPH_AndEC_DataThreadActive == True and self.insertPH_AndEC_DataThread != None:
            self.insertPH_AndEC_DataThreadActive = False
            self.insertPH_AndEC_DataThread.join()
            self.insertPH_AndEC_DataThread = None
        else:
            print("Could not terminate insertPH_AndEC_DataThread")
        
    def insertPH_AndEC_DataThreadTarget(self):
        while self.insertPH_AndEC_DataThreadActive == True:
        
            print("Running insertPH_AndEC_DataThread")
        
            if self.database_pH_values_queue != None or self.database_EC_values_queue != None:
                
                try:
                    sshtunnel.SSH_TIMEOUT = 20.0
                    sshtunnel.TUNNEL_TIMEOUT = 20.0
                    
                    with sshtunnel.SSHTunnelForwarder(
                        ('ssh.pythonanywhere.com'),
                        ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                        ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                        remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
                    ) as tunnel:
                        conn = MySQLdb.connect(
                            user=self.mySQL_ConnectionInformation.db_user,
                            passwd=self.mySQL_ConnectionInformation.db_pass,
                            host=self.mySQL_ConnectionInformation.remote_host,
                            port=tunnel.local_bind_port,
                            db=self.mySQL_ConnectionInformation.db_name,
                        )
                        
                        cursor = conn.cursor()
                        
                        if self.database_pH_values_queue != None:
                            while not self.database_pH_values_queue.empty():
                                val_time_tuple = self.database_pH_values_queue.get()
                                query = "INSERT INTO pH_data (pH, timestamp) VALUES (%s, %s)"
                                cursor.execute(query, (val_time_tuple[0], val_time_tuple[1]))
                        
                        if self.database_EC_values_queue != None:
                            while not self.database_EC_values_queue.empty():
                                val_time_tuple = self.database_EC_values_queue.get()
                                query = "INSERT INTO ec_data (ec, timestamp) VALUES (%s, %s)"
                                cursor.execute(query, (val_time_tuple[0], val_time_tuple[1]))
                                
                        # checking if capacity is reached (currently is 25)
                        # Count rows in pH_data
                        cursor.execute("SELECT COUNT(*) FROM pH_data")
                        row_count = cursor.fetchone()[0]

                        if row_count > 25:
                            cursor.execute("""
                                DELETE p FROM pH_data p
                                JOIN (
                                    SELECT id FROM pH_data ORDER BY timestamp ASC LIMIT %s
                                ) subquery ON p.id = subquery.id;
                            """, (row_count - 25,))  # Pass the number of extra rows to delete

                        # Count rows in ec_data
                        cursor.execute("SELECT COUNT(*) FROM ec_data")
                        row_count = cursor.fetchone()[0]

                        if row_count > 25:
                            cursor.execute("""
                                DELETE p FROM ec_data p
                                JOIN (
                                    SELECT id FROM ec_data ORDER BY timestamp ASC LIMIT %s
                                ) subquery ON p.id = subquery.id;
                            """, (row_count - 25,))  # Pass the number of extra rows to delete
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        print("Successfully Inserted Into EC and PH Data Tables")
                except Exception as e:
                    print(f"Error encountered: {e}")
                    
            time.sleep(1) # timeout
        print("insertPH_AndEC_DataThread has ended")
        
    def startInsertStatusThread(self):
        if self.insertStatusThreadActive == False and self.insertStatusThread == None:
            self.insertStatusThreadActive = True
            self.insertStatusThread = threading.Thread(target=self.insertStatusThreadTarget, daemon=True)
            self.insertStatusThread.start()
        
    def terminateInsertPumpWaterStatusThread(self):
        if self.insertStatusThreadActive == True and self.insertStatusThread != None:
            self.insertStatusThreadActive = False
            self.insertStatusThread.join()
            self.insertStatusThread = None
        
    def insertStatusThreadTarget(self):
        """
        This thread will be for all status objects that mySQL_CommunicationManager is currently attached to EXCEPT for the peristaltic pumps, that is a separate thread
        """
        from OverallSystemV2 import OverallSystem
        
        while self.insertStatusThreadActive:
            
            print("Iteration of insertStatusThreadTarget running...")
            
            # Initialize the relevant lists
            pumpWaterStatusDictsList = []
            pumpWaterStatusTuplesToAddToDatabase = []
            overallSystemStatusDictsList = []
            overallSystemStatusTuplesToAddToDatabase = []
            
            # doing for pump water first
            if self.pumpWaterStatus != None:
                
                while not self.pumpWaterStatus.statusActivityQueue.empty():
                    statusDict : dict = self.pumpWaterStatus.statusActivityQueue.get()
                    pumpWaterStatusDictsList.append(statusDict)
                    
                if len(pumpWaterStatusDictsList) != 0:
                    
                    for statusDict in pumpWaterStatusDictsList:
                        statusDict : dict # define this for type hints
                        alias = statusDict[PumpWater.FieldKeys.ALIAS]
                        pwm_freq = statusDict[PumpWater.FieldKeys.PWM]
                        on_off_state = statusDict[PumpWater.FieldKeys.ON_OFF_STATE]
                        mode = statusDict[PumpWater.FieldKeys.MODE]
                        auto_cycle_thread_active = statusDict[PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE]
                        
                        timestamp = statusDict["timestamp"]
                        
                        pumpWaterStatusTuple = (alias, pwm_freq, on_off_state, mode, auto_cycle_thread_active, timestamp)
                        pumpWaterStatusTuplesToAddToDatabase.append(pumpWaterStatusTuple)
               
            # doing for overall system
            if self.overallSystemStatus != None:

                print("overallSystem is not None")
    
                
                while not self.overallSystemStatus.statusActivityQueue.empty():
                    print("Emptying queue...")
                    statusDict : dict = self.overallSystemStatus.statusActivityQueue.get()
                    overallSystemStatusDictsList.append(statusDict)
                    
                if len(overallSystemStatusDictsList) != 0:
                    
                    for statusDict in overallSystemStatusDictsList:
                        statusDict : dict
                        alias = statusDict[OverallSystem.FieldKeys.ALIAS]
                        operation_mode = statusDict[OverallSystem.FieldKeys.OPERATION_MODE]
                        ph_up_pump_connected = statusDict[OverallSystem.FieldKeys.PH_UP_PUMP_CONNECTED]
                        ph_down_pump_connected = statusDict[OverallSystem.FieldKeys.PH_DOWN_PUMP_CONNECTED]
                        base_a_pump_connected = statusDict[OverallSystem.FieldKeys.BASE_A_PUMP_CONNECTED]
                        base_b_pump_connected = statusDict[OverallSystem.FieldKeys.BASE_B_PUMP_CONNECTED]
                        ph_sensor_connected = statusDict[OverallSystem.FieldKeys.PH_SENSOR_CONNECTED]
                        ec_sensor_connected = statusDict[OverallSystem.FieldKeys.EC_SENSOR_CONNECTED]
                        pump_water_connected = statusDict[OverallSystem.FieldKeys.PUMP_WATER_CONNECTED]
                        my_sql_communication_manager_connected = statusDict[OverallSystem.FieldKeys.MY_SQL_COMMUNICATION_MANAGER_CONNECTED]
                        menu_management_system_connected = statusDict[OverallSystem.FieldKeys.MENU_MANAGEMENT_SYSTEM_CONNECTED]
                        
                        timestamp = statusDict["timestamp"]
                        
                        overallSystemStatusTuple = (alias, operation_mode, ph_up_pump_connected, ph_down_pump_connected, base_a_pump_connected, base_b_pump_connected, ph_sensor_connected, ec_sensor_connected, pump_water_connected, my_sql_communication_manager_connected, menu_management_system_connected, timestamp)
                        overallSystemStatusTuplesToAddToDatabase.append(overallSystemStatusTuple)
                        print("Appended overallSystemStatusTuple...")
                        
            if len(pumpWaterStatusTuplesToAddToDatabase) != 0 or len(overallSystemStatusTuplesToAddToDatabase) != 0:
                    
                try:
                    sshtunnel.SSH_TIMEOUT = 20.0
                    sshtunnel.TUNNEL_TIMEOUT = 20.0
                    
                    with sshtunnel.SSHTunnelForwarder(
                        ('ssh.pythonanywhere.com'),
                        ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                        ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                        remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
                    ) as tunnel:
                        conn = MySQLdb.connect(
                            user=self.mySQL_ConnectionInformation.db_user,
                            passwd=self.mySQL_ConnectionInformation.db_pass,
                            host=self.mySQL_ConnectionInformation.remote_host,
                            port=tunnel.local_bind_port,
                            db=self.mySQL_ConnectionInformation.db_name,
                        )
                        
                        cursor = conn.cursor()
                        
                        for pumpWaterStatusTupleToAdd in pumpWaterStatusTuplesToAddToDatabase:
                        
                            query = "INSERT INTO waterPumpActivity (alias, pwm_freq, on_off_state, mode, auto_cycle_thread_active, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
                            cursor.execute(query, (pumpWaterStatusTupleToAdd[0], pumpWaterStatusTupleToAdd[1], pumpWaterStatusTupleToAdd[2], pumpWaterStatusTupleToAdd[3], pumpWaterStatusTupleToAdd[4], pumpWaterStatusTupleToAdd[5]))
                        
                        for overallSystemStatusTupleToAdd in overallSystemStatusTuplesToAddToDatabase:
                            
                            query = "INSERT INTO overallSystemActivity (alias, operation_mode, ph_up_pump_connected, ph_down_pump_connected, base_a_pump_connected, base_b_pump_connected, ph_sensor_connected, ec_sensor_connected, pump_water_connected, my_sql_communication_manager_connected, menu_management_system_connected, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            cursor.execute(query, (overallSystemStatusTupleToAdd[0], overallSystemStatusTupleToAdd[1], overallSystemStatusTupleToAdd[2], overallSystemStatusTupleToAdd[3], overallSystemStatusTupleToAdd[4], overallSystemStatusTupleToAdd[5], overallSystemStatusTupleToAdd[6], overallSystemStatusTupleToAdd[7], overallSystemStatusTupleToAdd[8], overallSystemStatusTupleToAdd[9], overallSystemStatusTupleToAdd[10], overallSystemStatusTupleToAdd[11]))
                            
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        print("Successfully Inserted Status into Corresponding Tables")
                except Exception as e:
                    print(f"Error encountered: {e}")
                    
            time.sleep(1) # timeout
                
        
    def insertPeristalticPumpStatusThreadTarget(self):
        while self.insertPeristalticPumpStatusThreadActive:
            
            nonStaleStatusDictsList = []
            
            # only insert new data if status has been updated and not stale
            if self.pH_UpPumpStatus != None:
                
                while not self.pH_UpPumpStatus.statusActivityQueue.empty():
                    statusDict = self.pH_UpPumpStatus.statusActivityQueue.get()
                    nonStaleStatusDictsList.append(statusDict)
            
            if self.pH_DownPumpStatus != None:
                
                while not self.pH_DownPumpStatus.statusActivityQueue.empty():
                    statusDict = self.pH_DownPumpStatus.statusActivityQueue.get()
                    nonStaleStatusDictsList.append(statusDict)
                    
            if self.baseA_PumpStatus != None:
                
                while not self.baseA_PumpStatus.statusActivityQueue.empty():
                    statusDict = self.baseA_PumpStatus.statusActivityQueue.get()
                    nonStaleStatusDictsList.append(statusDict)
                   
            if self.baseB_PumpStatus != None: 
                
                while not self.baseB_PumpStatus.statusActivityQueue.empty():
                    statusDict = self.baseB_PumpStatus.statusActivityQueue.get()
                    nonStaleStatusDictsList.append(statusDict)
            
            if len(nonStaleStatusDictsList) != 0:

                entriesToAddAsTuples = []
                for statusDict in nonStaleStatusDictsList:
                    statusDict : dict # define this for type hints
                    alias = statusDict[PeristalticPump.FieldKeys.ALIAS]
                    pin = statusDict[PeristalticPump.FieldKeys.PIN]
                    pumpActive = statusDict[PeristalticPump.FieldKeys.PUMP_ACTIVE]
                    timestamp = statusDict["timestamp"]
                    
                    entryTuple = (alias, pin, pumpActive, timestamp)
                    entriesToAddAsTuples.append(entryTuple)
                    
                try:
                    sshtunnel.SSH_TIMEOUT = 20.0
                    sshtunnel.TUNNEL_TIMEOUT = 20.0
                    
                    with sshtunnel.SSHTunnelForwarder(
                        ('ssh.pythonanywhere.com'),
                        ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                        ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                        remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
                    ) as tunnel:
                        conn = MySQLdb.connect(
                            user=self.mySQL_ConnectionInformation.db_user,
                            passwd=self.mySQL_ConnectionInformation.db_pass,
                            host=self.mySQL_ConnectionInformation.remote_host,
                            port=tunnel.local_bind_port,
                            db=self.mySQL_ConnectionInformation.db_name,
                        )
                        
                        cursor = conn.cursor()
                        
                        for entryToAddAsTuple in entriesToAddAsTuples:
                        
                            query = "INSERT INTO pPumpActivity (alias, pin, pumpActive, timestamp) VALUES (%s, %s, %s, %s)"
                            cursor.execute(query, (entryToAddAsTuple[0], entryToAddAsTuple[1], entryToAddAsTuple[2], entryToAddAsTuple[3]))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        print("Successfully Inserted Into pPumpActivity Table")
                except Exception as e:
                    print(f"Error encountered: {e}")
                    
            time.sleep(1) # timeout
        
    def startInsertPeristalticPumpStatusThread(self):
        if self.insertPeristalticPumpStatusThreadActive == False and self.insertPeristalticPumpStatusThread == None:
            self.insertPeristalticPumpStatusThreadActive = True
            self.insertPeristalticPumpStatusThread = threading.Thread(target=self.insertPeristalticPumpStatusThreadTarget, daemon=True)
            self.insertPeristalticPumpStatusThread.start()
        
        
    def terminateInsertPeristalticPumpStatusThread(self):
        if self.insertPeristalticPumpStatusThreadActive == True and self.insertPeristalticPumpStatusThread != None:
            self.insertPeristalticPumpStatusThreadActive = False
            self.insertPeristalticPumpStatusThread.join()
            self.insertPeristalticPumpStatusThread = None
        
    def requestPollingThreadTarget(self):
        from OverallSystemV2 import OverallSystem
        
        
        while self.requestPollingThreadActive:
            # only do something if there are requests
            if self._retrieve_current_number_of_requests() != 0:  
                request_tuple = self._pop_most_recent_request() # only do something
                command = request_tuple[0]
                args_list = request_tuple[1]
                if self.doPerformEnqueue == True:
                    
                    # If in manual mode, make sure command isn't in automaticOnlyCommands set
                    if self.overallSystemStatus.getStatusFieldTupleValueUsingKey(OverallSystem.FieldKeys.OPERATION_MODE) == OverallSystem.OperationModeEnum.MANUAL:
                        if command not in OverallSystem.automaticOnlyCommands:
                            self.menu_management_system.enqueue_command(command, *args_list)
                    # If in auto mode, make sure command isn't in manualOnlyCommands
                    if self.overallSystemStatus.getStatusFieldTupleValueUsingKey(OverallSystem.FieldKeys.OPERATION_MODE) == OverallSystem.OperationModeEnum.AUTO:
                        if command not in OverallSystem.manualOnlyCommands:
                            self.menu_management_system.enqueue_command(command, *args_list)

                print(f"Retrieved Command: {command} with args: {args_list}")
            else:
                print("Request Table is empty")
            print("timeout commencing...")
            time.sleep(1) # timeout
            
        
    def insertRequest(self, command, arguments: list):
        try:
            sshtunnel.SSH_TIMEOUT = 20.0
            sshtunnel.TUNNEL_TIMEOUT = 20.0
            
            with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
            ) as tunnel:
                conn = MySQLdb.connect(
                    user=self.mySQL_ConnectionInformation.db_user,
                    passwd=self.mySQL_ConnectionInformation.db_pass,
                    host=self.mySQL_ConnectionInformation.remote_host,
                    port=tunnel.local_bind_port,
                    db=self.mySQL_ConnectionInformation.db_name,
                )
                json_encoded_string = json.dumps(arguments)
                query = "INSERT INTO requests (command, arguments) VALUES (%s, %s)"
                cursor = conn.cursor()
                cursor.execute(query, (command, json_encoded_string))
                conn.commit()
                cursor.close()
                conn.close()
                print("Successfully Inserted Into Requests Table")
        except Exception as e:
            print(f"Error encountered: {e}")
        
    def start_requestPollingThread(self):
        if self.requestPollingThreadActive == False and self.requestPollingThread == None:
            self.requestPollingThreadActive = True
            self.requestPollingThread = threading.Thread(target=self.requestPollingThreadTarget, daemon=True)
            self.requestPollingThread.start()
        
    def terminate_requestPollingThread(self):
        if self.requestPollingThreadActive == True and self.requestPollingThread != None:
            self.requestPollingThreadActive = False
            print("Setting requestPollingThreadActive to false")
            self.requestPollingThread.join()
            self.requestPollingThread = None
            print("Request Polling Thread has been stopped")
        
    def terminateInsertPH_AndEC_DataThread(self):
        NotImplemented
        
    def _retrieve_most_recent_command_arg_pair(self) -> tuple:
        """
        The returned tuple will have 3 items, i.e., (primary key, command, arguments)
        """
        
        try:
            sshtunnel.SSH_TIMEOUT = 20.0
            sshtunnel.TUNNEL_TIMEOUT = 20.0
            
            with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
            ) as tunnel:
                conn = MySQLdb.connect(
                    user=self.mySQL_ConnectionInformation.db_user,
                    passwd=self.mySQL_ConnectionInformation.db_pass,
                    host=self.mySQL_ConnectionInformation.remote_host,
                    port=tunnel.local_bind_port,
                    db=self.mySQL_ConnectionInformation.db_name,
                )
                query = "SELECT id, command, arguments FROM requests ORDER BY id DESC LIMIT 1"
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                conn.commit()
                cursor.close()
                conn.close()
                print("Successfully Retrieved Most Recent Request/Command-Args Pair")
        except Exception as e:
            print(f"Error encountered: {e}")
        
        return result
        
    def _pop_most_recent_request(self) -> tuple:
        """
        This will retrieve the most recent request and pop it from the database
    
        Will be in the following format:
        ("command", [arg1, arg2, arg3, ...])
        """
        
        request_entry = self._retrieve_most_recent_command_arg_pair()
        primary_key = request_entry[0]
        command = request_entry[1]
        args_list_json_string = request_entry[2]
        args_list = None
        if args_list_json_string != None:
            args_list = json.loads(args_list_json_string) # load json string as a list
        self._delete_request_by_id(primary_key)
        return (command, args_list)
    
    def _delete_request_by_id(self, ID):    
        
        try:
            sshtunnel.SSH_TIMEOUT = 20.0
            sshtunnel.TUNNEL_TIMEOUT = 20.0
            
            with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
            ) as tunnel:
                conn = MySQLdb.connect(
                    user=self.mySQL_ConnectionInformation.db_user,
                    passwd=self.mySQL_ConnectionInformation.db_pass,
                    host=self.mySQL_ConnectionInformation.remote_host,
                    port=tunnel.local_bind_port,
                    db=self.mySQL_ConnectionInformation.db_name,
                )
                query = "DELETE FROM requests WHERE id = %s"
                cursor = conn.cursor()
                cursor.execute(query, (ID,))
                tot_num_rows = cursor.fetchone()
                conn.commit()
                print("DELETE Successfully Submitted")
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"Error encountered: {e}")
        
    def _retrieve_current_number_of_requests(self):
        try:
            sshtunnel.SSH_TIMEOUT = 20.0
            sshtunnel.TUNNEL_TIMEOUT = 20.0
            
            with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
                ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
                remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
            ) as tunnel:
                conn = MySQLdb.connect(
                    user=self.mySQL_ConnectionInformation.db_user,
                    passwd=self.mySQL_ConnectionInformation.db_pass,
                    host=self.mySQL_ConnectionInformation.remote_host,
                    port=tunnel.local_bind_port,
                    db=self.mySQL_ConnectionInformation.db_name,
                )
                query = "SELECT COUNT(*) AS total_rows FROM requests"
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                tot_num_rows = result[0]
                cursor.close()
                conn.close()
                print("Successfully retrieved number of requests in request table")
                return tot_num_rows
                
        except Exception as e:
            print(f"Error encountered: {e}")
        
if __name__ == "__main__":
    import MySQL_CommunicationManagerTestCases
    import GPIO_Utility
    
    try:
        MySQL_CommunicationManagerTestCases.test_inserting_into_ec_and_pH_data_tables()
    except KeyboardInterrupt as e:
        GPIO_Utility.gpioCleanup()
    
    exit()