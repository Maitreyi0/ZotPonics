def test_pop_from_requests_table_and_enqueue_request():
    from MySQL_CommunicationManager import MySQL_ServerCommunicationManager, MySQL_ConnectionInformation
    from MenuManagementSystem import MenuManagementSystem
    
    def set_pwm_cycle_test_callback(PWM_val):
        print("[PumpWater]-set_pwm_duty_cycle was triggered")
        print(f"PWM Value: {PWM_val}")
        
    def manual_turn_on_pump_callback():
        print(" [PumpWater]-manual_turn_on_pump was triggered")
    
    # Create an instance of MenuManagementSystem with a 5-command queue size
    menu_system = None
    menu_system = MenuManagementSystem(max_queue_size=5)
    menu_system.add_option("[PumpWater]-set_pwm_duty_cycle was triggered", set_pwm_cycle_test_callback)
    menu_system.add_option("[PumpWater]-manual_turn_on_pump", manual_turn_on_pump_callback)
    menu_system.start_processing()
    
    ssh_host='ssh.pythonanywhere.com'
    ssh_user='superlords1'
    ssh_pass='BinhAn@1962'
    remote_bind_address='superlords1.mysql.pythonanywhere-services.com'
    remote_host = '127.0.0.1'
    remote_port=3306
    db_user='superlords1'
    db_pass='zotponics123'
    db_name='superlords1$default'
    
    mySQL_ConnectionInformation = MySQL_ConnectionInformation(ssh_host, ssh_user, ssh_pass, remote_bind_address, remote_host, remote_port, db_user, db_pass, db_name)
    
    doPerformEnqueue = True # For testing just the request polling separately
    
    mySQL_ServerCommunicationManager = MySQL_ServerCommunicationManager(mySQL_ConnectionInformation, menu_system, None, None, doPerformEnqueue)
    
    # insert some requests for testing first
    mySQL_ServerCommunicationManager.insertRequest("[PumpWater]-set_pwm_duty_cycle was triggered", [50])
    mySQL_ServerCommunicationManager.insertRequest("[PumpWater]-set_pwm_duty_cycle was triggered", [25])
    mySQL_ServerCommunicationManager.insertRequest("[PumpWater]-manual_turn_on_pump", [])
    mySQL_ServerCommunicationManager.insertRequest("[PumpWater]-manual_turn_on_pump", [])

    mySQL_ServerCommunicationManager.start_requestPollingThread()
    input("Input anything to terminate threads and end program: ")
    print("Terminating the thread")
    mySQL_ServerCommunicationManager.terminate_requestPollingThread()
    mySQL_ServerCommunicationManager.menu_management_system.stop_processing()
    
    exit()
    
def test_inserting_into_waterPump_activity_table():
    from MySQL_CommunicationManager import MySQL_ServerCommunicationManager, MySQL_ConnectionInformation
    from PumpWater import PumpWater
    import time
    
    # Initialize Water Pump---------------------------------------------
    # Initialize the status args dict
    statusArgsDict = {}
    statusArgsDict["alias"] = "pumpWater"
    statusArgsDict["isTopLevelStatusObject"] = True
    statusArgsDict["debugModeOn"] = True
    
    pumpWater = PumpWater(in1_pin=5,in2_pin=6,pwm_pin=12,statusArgsDict=statusArgsDict)
    pumpWater.set_pwm_duty_cycle(50) # should set the PWM cycle before turning on to avoid any un-intended behavior
    # ------------------------------------------------------------------
    
    # Initialize Communication Manager----------------------------------
    
    ssh_host='ssh.pythonanywhere.com'
    ssh_user='superlords1'
    ssh_pass='BinhAn@1962'
    remote_bind_address='superlords1.mysql.pythonanywhere-services.com'
    remote_host = '127.0.0.1'
    remote_port=3306
    db_user='superlords1'
    db_pass='zotponics123'
    db_name='superlords1$default'
    
    mySQL_ConnectionInformation = MySQL_ConnectionInformation(ssh_host, ssh_user, ssh_pass, remote_bind_address, remote_host, remote_port, db_user, db_pass, db_name)
    
    doPerformEnqueue = False # Since won't have a menu system attached for this test, will just set as False, this attribute won't be used for this test
    
    mySQL_ServerCommunicationManager = MySQL_ServerCommunicationManager(mySQL_ConnectionInformation=mySQL_ConnectionInformation, menu_management_system=None, database_pH_values_circular_buffer=None, database_EC_values_circular_buffer=None, doPerformEnqueue=doPerformEnqueue, pH_UpPumpStatus=None, pH_DownPumpStatus=None, baseA_PumpStatus=None, baseB_PumpStatus=None, pumpWaterStatus=pumpWater.status)
    
    # ------------------------------------------------------------------
    
    # Running the program-----------------------------------------------
    
    mySQL_ServerCommunicationManager.startInsertPumpWaterStatusThread()
    
    pumpWater.manual_turn_on_pump()
    time.sleep(5)
    pumpWater.manual_turn_off_pump()
    pumpWater.shutdown()
    
    input("Input anything to terminate threads and end program: ")
    mySQL_ServerCommunicationManager.terminateInsertPumpWaterStatusThread()
    
    # ------------------------------------------------------------------
    
    
def test_inserting_into_pPump_activity_table():
    from MySQL_CommunicationManager import MySQL_ServerCommunicationManager, MySQL_ConnectionInformation
    from MenuManagementSystem import MenuManagementSystem
    from PeristalticPump import PeristalticPump
    
    # Initialize Peristaltic Pumps--------------------------------------
    pinPH_UP = 22
    pinPH_DOWN = 23
    pinBASE_A = 21
    pinBASE_B = 20
    
    phUpPump = PeristalticPump(pinPH_UP, "phUpPump", True, False)
    phDownPump = PeristalticPump(pinPH_DOWN, "phDownPump", True, False)
    baseAPump = PeristalticPump(pinBASE_A, "baseAPump", True, False)
    baseBPump = PeristalticPump(pinBASE_B, "baseBPump", True, False)
    # ------------------------------------------------------------------
    
    # Initialize Communication Manager----------------------------------
    ssh_host='ssh.pythonanywhere.com'
    ssh_user='superlords1'
    ssh_pass='BinhAn@1962'
    remote_bind_address='superlords1.mysql.pythonanywhere-services.com'
    remote_host = '127.0.0.1'
    remote_port=3306
    db_user='superlords1'
    db_pass='zotponics123'
    db_name='superlords1$default'
    
    mySQL_ConnectionInformation = MySQL_ConnectionInformation(ssh_host, ssh_user, ssh_pass, remote_bind_address, remote_host, remote_port, db_user, db_pass, db_name)
    
    doPerformEnqueue = False # Since won't have a menu system attached for this test, will just set as False, this attribute won't be used for this test
    
    mySQL_ServerCommunicationManager = MySQL_ServerCommunicationManager(mySQL_ConnectionInformation=mySQL_ConnectionInformation, menu_management_system=None, database_pH_values_circular_buffer=None, database_EC_values_circular_buffer=None, doPerformEnqueue=doPerformEnqueue, pH_UpPumpStatus=phUpPump.status, pH_DownPumpStatus=phDownPump.status, baseA_PumpStatus=baseAPump.status, baseB_PumpStatus=baseBPump.status)
    # ------------------------------------------------------------------
    
    # Running the program ----------------------------------------------
    
    mySQL_ServerCommunicationManager.startInsertPeristalticPumpStatusThread()
    
    # Change the status of the pumps
    phUpPump.turnOnWithDuration(3)
    
    input("Input anything to terminate threads and end program: ")
    mySQL_ServerCommunicationManager.terminateInsertPeristalticPumpStatusThread()
    
    # ------------------------------------------------------------------
    
    