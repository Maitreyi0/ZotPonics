class OverallSystemTestCases:

    @classmethod
    def startOverallSystemAsConsoleProgram(self):
        import GPIO_Utility
        from hardwareCode.OverallSystemDeprecated import OverallSystem
        from PumpWater import PumpWater
        from MenuManagementSystem import MenuManagementSystem
        from ConsoleProgram import ConsoleProgram
        
        """
        No remote functionality available, will acquire inputs from user input in console
        """
        
        # GPIO setup
        GPIO_Utility.setModeBCM()
        
        # Overall System Initialization
        statusArgsDictOverallSystem = {}
        statusArgsDictOverallSystem["alias"] = "OverallSystem"
        statusArgsDictOverallSystem["isTopLevelStatusObject"] = True
        statusArgsDictOverallSystem["debugModeOn"] = True
        
        overallSystem = OverallSystem(statusArgsDict=statusArgsDictOverallSystem)
        
        # Water Pump Subsystem Initialization
        statusArgsDictPumpWater = {}
        statusArgsDictPumpWater["alias"] = "PumpWater"
        statusArgsDictPumpWater["isTopLevelStatusObject"] = False
        statusArgsDictPumpWater["debugModeOn"] = True
        
        pumpWater = PumpWater(in1_pin=5,in2_pin=6,pwm_pin=12,statusArgsDict=statusArgsDictPumpWater)
        
        # Menu Management System Initialization
        menuManagementSystem = MenuManagementSystem()
        # Syntax: <alias>-<method name>
        # Add options to the menu system
        # From Water Pump
        pumpWaterAlias = statusArgsDictPumpWater["alias"]
        methodsToAddAsOptionsPumpWater = [
            pumpWater.manual_turn_on_pump, 
            pumpWater.manual_turn_off_pump, 
            pumpWater.switch_to_automatic, 
            pumpWater.switch_to_manual, 
            pumpWater.set_pwm_duty_cycle_wrapper_for_console_program, 
            pumpWater.shutdown, 
            pumpWater.start_automatic_thread_wrapper_for_console_program, 
            pumpWater.terminate_automatic_thread
        ]
        
        menuManagementSystem.mass_add_options_to_menu_management_system(pumpWaterAlias, methodsToAddAsOptionsPumpWater)
            
        # Start the menu management system's queue processing in a separate thread
        menuManagementSystem.start_processing()
        
        # Initialize the console program to interface with the menu management system
        consoleProgram = ConsoleProgram(menuManagementSystem)
        # Start the console program to allow user input
        consoleProgram.start()
        
        consoleProgram.wait_until_exit()
        
        menuManagementSystem.stop_processing()
        
        overallSystem.shutdown()
        
        exit()