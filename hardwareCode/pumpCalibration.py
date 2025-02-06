from hardwareCode.PeristalticPump import PeristalticPump
import GPIO_Utility

if __name__ == "__main__":
    
    # GPIO setup
    GPIO_Utility.setModeBCM()
    
    # pump pins
    pH_UpPumpPin = 22
    pH_DownPumpPin = 23
    baseA_PumpPin = 21
    baseB_PumpPin = 20
    
    # initialize pump objects
    pH_UpPump = PeristalticPump(pH_UpPumpPin)
    pH_DownPump = PeristalticPump(pH_DownPumpPin)
    baseA_Pump = PeristalticPump(baseA_PumpPin)
    baseB_Pump = PeristalticPump(baseB_PumpPin)
    
    # print("Calibrating pH Up Pump")
    # pH_UpPump.turnOn()
    # input("Input anything to turn off once pump fully filled: ")
    # pH_UpPump.turnOff()
    
    # input("Input anything to continue to next pump: ")
    
    print("Calibrating pH Down Pump")
    pH_DownPump.turnOn()
    input("Input anything to turn off once pump fully filled: ")
    pH_DownPump.turnOff()
    
    # print("Calibrating Base A Pump")
    # baseA_Pump.turnOn()
    # input("Input anything to turn off once pump fully filled: ")
    # baseA_Pump.turnOff()
    
    # print("Calibrating Base B Pump")
    # baseB_Pump.turnOn()
    # input("Input anything to turn off once pump fully filled: ")
    # baseB_Pump.turnOff()
    
    # GPIO cleanup
    GPIO_Utility.gpioCleanup()
    
    exit()
    