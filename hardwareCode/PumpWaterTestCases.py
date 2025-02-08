from PumpWater import PumpWater

class PumpWaterTestCases:
    @classmethod
    def testPumpDriverBasic(cls):
        import time
    
        # Initialize the status args dict
        statusArgsDict = {}
        statusArgsDict["alias"] = "pumpWater"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        pumpWater = PumpWater(in1_pin=5,in2_pin=6,pwm_pin=12,statusArgsDict=statusArgsDict)
        pumpWater.set_pwm_duty_cycle(50) # should set the PWM cycle before turning on to avoid any un-intended behavior
        pumpWater.manual_turn_on_pump()
        time.sleep(5)
        pumpWater.manual_turn_off_pump()
        pumpWater.shutdown()
    
    @classmethod
    def testAutoCycleThread(cls):
        # Initialize the status args dict
        statusArgsDict = {}
        statusArgsDict["alias"] = "pumpWater"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        pumpWater = PumpWater(in1_pin=5,in2_pin=6,pwm_pin=12,statusArgsDict=statusArgsDict)
        print("Setting PWM to 50 duty cycle...")
        print("Switching to automatic mode...")
        pumpWater.switch_to_automatic()
        pumpWater.set_pwm_duty_cycle(50) # set the PWM cycle after switching because switching resets it to 0% duty cycle
        input("Input anything to start an automatic thread (5 seconds on, 10 seconds off): ")
        
        pumpWater.start_automatic_thread(5, 10)
        
        input("Input anything to stop the thread and clean up")
        pumpWater.shutdown()
    
    @classmethod
    def generateListOfMethodNames(cls):
        # Initialize the status args dict
        statusArgsDict = {}
        statusArgsDict["alias"] = "pumpWater"
        statusArgsDict["isTopLevelStatusObject"] = True
        statusArgsDict["debugModeOn"] = True
        
        pumpWater = PumpWater(in1_pin=5,in2_pin=6,pwm_pin=12,statusArgsDict=statusArgsDict)
        
        method_names = [pumpWater.manual_turn_on_pump.__name__, pumpWater.manual_turn_off_pump.__name__]
        print(method_names)
