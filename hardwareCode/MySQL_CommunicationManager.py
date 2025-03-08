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
    def __init__(self, mySQL_ConnectionInformation : MySQL_ConnectionInformation, menu_management_system : MenuManagementSystem, database_pH_values_queue : Queue, database_EC_values_queue : Queue, pH_UpPumpStatus : Status, pH_DownPumpStatus : Status, baseA_PumpStatus : Status, baseB_PumpStatus : Status, doPerformEnqueue, pumpWaterStatus : Status):
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
        
        self.requestPollingThread = None
        self.requestPollingThreadActive = False
        
        # will use one thread to control this but doesn't necessarily have to upload both pH and EC data at the same time
        # whether it does or not depends on whether the circular_buffer attributes are None or not
        self.insertPH_AndEC_DataThread = None
        self.insertPH_AndEC_DataThreadActive = False
        
        self.insertPeristalticPumpStatusThread = None
        self.insertPeristalticPumpStatusThreadActive = False
        
        self.insertPumpWaterStatusThread = None
        self.insertPumpWaterStatusThreadActive = False
        
        # This will store the connection object
        self.conn = None
        # This will store the connection cursor object
        self.cursor = None
        
        self.doPerformEnqueue = doPerformEnqueue
    
    def add_menu_management_system_options_for_pump_water(self, pumpWater : PumpWater):
        
        # Pump Water Command Options
        if self.menu_management_system != None:
            self.menu_management_system.add_option("[PumpWater]-manual_turn_on_pump", pumpWater.manual_turn_on_pump)
            self.menu_management_system.add_option("[PumpWater]-manual_turn_off_pump", pumpWater.manual_turn_off_pump)
            self.menu_management_system.add_option("[PumpWater]-set_pwm_duty_cycle", pumpWater.set_pwm_duty_cycle)
            self.menu_management_system.add_option("[PumpWater]-switch_to_automatic", pumpWater.switch_to_automatic)
            self.menu_management_system.add_option("[PumpWater]-switch_to_manual", pumpWater.switch_to_manual)
        else:
            print("No menu management system object present")
            
        
      
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
        
    def startInsertPumpWaterStatusThread(self):
        if self.insertPumpWaterStatusThreadActive == False and self.insertPumpWaterStatusThread == None:
            self.insertPumpWaterStatusThreadActive = True
            self.insertPumpWaterStatusThread = threading.Thread(target=self.insertPumpWaterStatusThreadTarget, daemon=True)
            self.insertPumpWaterStatusThread.start()
        
    def terminateInsertPumpWaterStatusThread(self):
        if self.insertPumpWaterStatusThreadActive == True and self.insertPumpWaterStatusThread != None:
            self.insertPumpWaterStatusThreadActive = False
            self.insertPumpWaterStatusThread.join()
            self.insertPumpWaterStatusThread = None
        
    def insertPumpWaterStatusThreadTarget(self):
        while self.insertPumpWaterStatusThreadActive:
            
            nonStaleStatusDictsList = []
            
            if self.pumpWaterStatus != None:
                
                while not self.pumpWaterStatus.statusActivityQueue.empty():
                    statusDict : dict = self.pumpWaterStatus.statusActivityQueue.get()
                    nonStaleStatusDictsList.append(statusDict)
                    
            if len(nonStaleStatusDictsList) != 0:

                entriesToAddAsTuples = []
                for statusDict in nonStaleStatusDictsList:
                    statusDict : dict # define this for type hints
                    alias = statusDict[PumpWater.FieldKeys.ALIAS]
                    pwm_freq = statusDict[PumpWater.FieldKeys.PWM]
                    on_off_state = statusDict[PumpWater.FieldKeys.ON_OFF_STATE]
                    mode = statusDict[PumpWater.FieldKeys.MODE]
                    auto_cycle_thread_active = statusDict[PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE]
                    
                    timestamp = statusDict["timestamp"]
                    
                    entryTuple = (alias, pwm_freq, on_off_state, mode, auto_cycle_thread_active, timestamp)
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
                        
                            query = "INSERT INTO waterPumpActivity (alias, pwm_freq, on_off_state, mode, auto_cycle_thread_active, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
                            cursor.execute(query, (entryToAddAsTuple[0], entryToAddAsTuple[1], entryToAddAsTuple[2], entryToAddAsTuple[3], entryToAddAsTuple[4], entryToAddAsTuple[5]))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        print("Successfully Inserted Into waterPumpActivity Table")
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
        while self.requestPollingThreadActive:
            # only do something if there are requests
            if self._retrieve_current_number_of_requests() != 0:  
                request_tuple = self._pop_most_recent_request() # only do something
                command = request_tuple[0]
                args_list = request_tuple[1]
                if self.doPerformEnqueue == True:
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
    MySQL_CommunicationManagerTestCases.test_inserting_into_ec_and_pH_data_tables()
    
    exit()
    