def test_establish_and_terminate_connection_methods():
    from MySQL_CommunicationManager import MySQL_ServerCommunicationManager, MySQL_ConnectionInformation
    import time
    
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
    
    mySQL_ServerCommunicationManager = MySQL_ServerCommunicationManager(mySQL_ConnectionInformation, None, None, None)
    
    mySQL_ServerCommunicationManager.establish_connection_with_server()
    
    time.sleep(3)
    
    mySQL_ServerCommunicationManager.terminate_connection_with_server()
    
def test_pop_and_enqueue():
    from MySQL_CommunicationManager import MySQL_ServerCommunicationManager, MySQL_ConnectionInformation
    from MenuManagementSystem import MenuManagementSystem
    import time
    
    def set_pwm_cycle_test_callback(PWM_val):
        print("[PumpWater]-set_pwm_duty_cycle was triggered")
        print(f"PWM Value: {PWM_val}")
        
        
    def manual_turn_on_pump_callback():
        print(" [PumpWater]-manual_turn_on_pump was triggered")
    
    # initialize menu management system
    
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
    