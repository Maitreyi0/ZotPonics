from MenuManagementSystem import MenuManagementSystem
from CircularBuffer import CircularBuffer
import mysql.connector
from mysql.connector import Error
import MySQLdb
import sshtunnel
import time
import json
import threading

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
    def __init__(self, mySQL_ConnectionInformation : MySQL_ConnectionInformation, menu_management_system : MenuManagementSystem, database_pH_values_circular_buffer : CircularBuffer, database_EC_values_circular_buffer : CircularBuffer, doPerformEnqueue):
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
        
        self.database_pH_values_circular_buffer = database_pH_values_circular_buffer
        
        self.database_EC_values_circular_buffer = database_EC_values_circular_buffer
        
        self.requestPollingThread = None
        self.requestPollingThreadActive = False
        
        # will use one thread to control this but doesn't necessarily have to upload both pH and EC data at the same time
        # whether it does or not depends on whether the circular_buffer attributes are None or not
        self.insertPH_AndEC_DataThread = None
        self.insertPH_AndEC_DataThreadActive = False
        
        # This will store the connection object
        self.conn = None
        # This will store the connection cursor object
        self.cursor = None
        
        self.doPerformEnqueue = doPerformEnqueue
            
    # THESE DON"T WORK
    # def establish_connection_with_server(self):
    #     if self.conn == None:
    #         try:
    #             sshtunnel.SSH_TIMEOUT = 20.0
    #             sshtunnel.TUNNEL_TIMEOUT = 20.0
                
    #             with sshtunnel.SSHTunnelForwarder(
    #                 ('ssh.pythonanywhere.com'),
    #                 ssh_username=self.mySQL_ConnectionInformation.ssh_user, 
    #                 ssh_password=self.mySQL_ConnectionInformation.ssh_pass,
    #                 remote_bind_address=(self.mySQL_ConnectionInformation.remote_bind_address, self.mySQL_ConnectionInformation.remote_port)
    #             ) as tunnel:
    #                 self.conn = MySQLdb.connect(
    #                     user=self.mySQL_ConnectionInformation.db_user,
    #                     passwd=self.mySQL_ConnectionInformation.db_pass,
    #                     host=self.mySQL_ConnectionInformation.remote_host,
    #                     port=tunnel.local_bind_port,
    #                     db=self.mySQL_ConnectionInformation.db_name,
    #                 )
    #                 self.cursor = self.conn.cursor()
    #         except Exception as e:
    #             print(f"Could not establish connection with database due to: {e}")
    #     else:
    #         print("Already connected to database")
            
    # def terminate_connection_with_server(self):
    #     if self.conn != None:
    #         print("Connection terminated...")
    #         self.cursor.close()
    #         self.conn.close()
    #         self.conn = None
    #         self.cursor = None
    #     else:
    #         print("Not connected to remote database")
        
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
        
    def insertPH_AndEC_DataThreadTarget(self):
        while self.insertPH_AndEC_DataThreadActive:
            
            time.sleep(1) # timeout
        
    def start_requestPollingThread(self):
        if self.requestPollingThreadActive == False and self.requestPollingThread == None:
            self.requestPollingThreadActive = True
            self.requestPollingThread = threading.Thread(target=self.requestPollingThreadTarget, daemon=True)
            self.requestPollingThread.start()
        
        
    def start_insertPH_AndEC_DataThread(self):
        NotImplemented
        
    def terminate_requestPollingThread(self):
        if self.requestPollingThreadActive == True and self.requestPollingThread != None:
            self.requestPollingThreadActive = False
            print("Setting requestPollingThreadActive to false")
            self.requestPollingThread.join()
            self.requestPollingThread = None
            print("Request Polling Thread has been stopped")
        
    def terminate_insertPH_AndEC_DataThread(self):
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
    MySQL_CommunicationManagerTestCases.test_pop_and_enqueue()
    
    exit()
    