class MenuManagementSystemProtocol:
    
    # Store on database for:
    # General Example:
    # "Do Action X": ("[<alias>]-<method name>", <alias>.<method name>)
    # Row X, Col Y: "[<alias>]-<method name>"
    # Row X, Col (Y+1): arg1
    # Row X, Col (Y+2): arg2
    # ...
    # Row X, Col (Y+N): argN
    # Specific Examples:
    # "Manually Turn on Pump": ("[PumpWater]-manual_turn_on_pump", PumpWater.manual_turn_off_pump)
    # This:
    # Row X, Col Y: "[PumpWater]-manual_turn_on_pump"
    # "Set PWM Duty Cycle": ("[PumpWater]-set_pwm_duty_cycle", PumpWater.set_pwm_duty_cycle)
    # This:
    # Row X, Col Y: "[PumpWater]-set_pwm_duty_cycle"
    # Row X, Col (Y+1): 50 (as an example)
    
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
    