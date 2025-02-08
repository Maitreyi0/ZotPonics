class MenuManagementSystemProtocol:
    from PumpWater import PumpWater
    
    PumpWater = {
        "Manually Turn on Pump": ("[PumpWater]-manual_turn_on_pump", PumpWater.manual_turn_off_pump),
        "Manually Turn off Pump": ("[PumpWater]-manual_turn_off_pump", PumpWater.manual_turn_off_pump),
        "Switch to Automatic Mode": ("[PumpWater]-switch_to_automatic", PumpWater.switch_to_automatic),
        "Switch to Manual Mode": ("[PumpWater]-switch_to_manual", PumpWater.switch_to_manual),
        "Set PWM Duty Cycle": ("[PumpWater]-set_pwm_duty_cycle", PumpWater.set_pwm_duty_cycle),
        "Start Automatic Thread": ("[PumpWater]-start_automatic_thread", PumpWater.start_automatic_thread),
        "Terminate Automatic Thread": ("[PumpWater]-terminate_automatic_thread", PumpWater.terminate_automatic_thread),
        "Shut Down": ("[PumpWater]-shutdown", PumpWater.shutdown),
    }
    
    PumpWaterStatus = {}
    