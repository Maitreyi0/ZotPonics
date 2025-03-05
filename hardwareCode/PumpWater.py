import RPi.GPIO as GPIO
from Status import Status
import threading as th
import GPIO_Utility
import time

# Overview:
# The PumpWater class is for the water pump of the hydroponics system
# There will be two modes of operation: automatic, manual
# Automatic:
# - While this mode is active, there will be a thread that cycles water periodically
# Manual:
#- While this mode is active, water will only be cycled when the corresponding method is called (will need to specify the number of seconds)

# The PumpDriver sub-class is for the motor driver that is used to control the pump (used since it allows for PWM control of the pump)
# There will be three main functions:
# - Turn on (when IN1 = HIGH, IN2 = LOW)
# - Turn off (when IN1 = LOW, IN2 = LOW)
# - Output software PWM signal

class PumpWater:
    
    # Extend the base FieldKeys class for the water pump subsystem
    class FieldKeys(Status.FieldKeys):
        PWM = "PWM Duty Cycle"
        ON_OFF_STATE = "On/Off" # this is for the pump
        MODE = "Mode"
        AUTO_CYCLE_THREAD_ACTIVE = "automaticCycleThreadActive" # some threads being active are useful for the user to see so will have them as part of status instead of direct attributes
        
    class ModeEnum:
        AUTO = "Automatic"
        MANUAL = "Manual"
        
    class OnOffEnum:
        ON = "On"
        OFF = "Off"
    
    def __init__(self, in1_pin, in2_pin, pwm_pin, statusArgsDict, frequency=1000):
        """
        Initialize the PumpDriver.

        :param in1_pin: GPIO pin for IN1
        :param in2_pin: GPIO pin for IN2
        :param pwm_pin: GPIO pin for PWM control
        :param frequency: Frequency for PWM signal (default is 1000Hz)
        """
        
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.pwm_pin = pwm_pin
        # CONVENTION: GPIO Setup and Cleanup done by top level entity, the top level entity corresponds with the top level status
        self.status : Status = Status.init_from_dict(statusArgsDict)
        if self.status.isTopLevelStatusObject:
            GPIO_Utility.setModeBCM()
        # Initialize relevant status fields using the FieldKeys class
        # NOTE: PumpWater.FieldKeys.__dict__ doesn't include the parent class attributes so can use this, so won't try to add alias again
        fieldKeys = [value for key, value in PumpWater.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            # print(f"Current Field Key: {fieldKey}")
            self.status.addStatusFieldTuple(fieldKey, None)
            
        self.frequency = frequency
        
        # Assumed: GPIO mode is initialized at this point
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm_pin, self.frequency)
        self.pwm.start(0)  # Start with 0% duty cycle (off)
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.PWM, 0)
        
        # Turn off initially: sets in1 and in2 both to LOW
        self.turn_off()
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)
        
        # Set some initial field tuple values (other fields will be set later on)
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, False)
        # Initialized mode is manual
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.MODE, PumpWater.ModeEnum.MANUAL)
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE, False)
        
        # Periodic Pumping Thread Variables
        self.automaticThread = None
        # for this thread, will use status field AUTO_CYCLE_THREAD_ACTIVE as the condition to terminate
        
    def automaticThreadTarget(self, on_duration, off_duration):
        """
        Two conditions must be true simultaneously for this while loop to continue running
        """
        while self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == True:

            print("Pump ON")
            self.turn_on()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.ON)

            start_time = time.time()
            while time.time() - start_time < on_duration:
                if not self.automaticThreadActive:
                    break
                time.sleep(0.1)

            # Will break again to break out of the outer while loop to terminate thread
            if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == False:
                break
            
            print("Pump OFF")
            self.turn_off()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)

            start_time = time.time()
            while time.time() - start_time < off_duration:
                if not self.automaticThreadActive:
                    break
                time.sleep(0.1)
                
            # Don't need another break here because re-evaluating the outer while loop condition immediately after

        print("Automatic pump thread stopping.")
    
    def start_automatic_thread(self, on_duration, off_duration):
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == PumpWater.ModeEnum.AUTO and self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == False:
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE, True)
            self.automaticThread = th.Thread(target=self.automaticThreadTarget, args=[on_duration, off_duration])
            self.automaticThread.start()
            
    def start_automatic_thread_wrapper_for_console_program(self, on_duration_str, off_duration_str):
        self.start_automatic_thread(int(on_duration_str), int(off_duration_str))
            
    def terminate_automatic_thread(self):
        """
        Terminating the thread
        """
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == True:
            
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE, False)
            self.automaticThread.join()
            self.turn_off() # just turn off in the case that we are on the active portion of the cycle when terminating
            self.automaticThread = None
        else:
            raise Exception("Could not terminate AutomaticThread, check thread variables")
            

    # manual turn on and off, if manually controlling should call these
    def manual_turn_on_pump(self):
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == "Manual":
            self.turn_on()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.ON)
        else:
            print("Did not turn on pump, not in manual control mode")
            
    def manual_turn_off_pump(self):
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == "Manual":
            self.turn_off()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)
        else:
            print("Did not turn off pump, not in manual control mode")

    def switch_to_automatic(self):
        """
        Switching to automatic will disable all manual control. Automatic mode threads are not automatically started
        """
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == "Manual":
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.MODE, "Automatic")
            # reset everything when switching
            self.set_pwm_duty_cycle(0)
            self.turn_off()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)
        else:
            print("Already in automatic mode")
        
    def switch_to_manual(self):
        """
        Switching to manual will cause any running automatic mode threads to cancel
        """
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == PumpWater.ModeEnum.AUTO:
            
            # To handle the case when the automatic thread is running while switching to manual mode
            if self.automaticThreadActive:
                self.terminate_automatic_thread()
            
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.MODE, PumpWater.ModeEnum.MANUAL)
            # reset everything after switching to manual
            self.set_pwm_duty_cycle(0)
            self.turn_off()
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)
        else:
            print("Already in manual mode")

    def turn_on(self):
        """Turns on the pump by setting IN1 HIGH and IN2 LOW."""
        GPIO.output(self.in1_pin, GPIO.HIGH)
        GPIO.output(self.in2_pin, GPIO.LOW)

    def turn_off(self):
        """Turns off the pump by setting both IN1 and IN2 LOW."""
        GPIO.output(self.in1_pin, GPIO.LOW)
        GPIO.output(self.in2_pin, GPIO.LOW)

    def set_pwm_duty_cycle(self, duty_cycle):
        """
        Set the PWM duty cycle.

        :param duty_cycle: Duty cycle (0 to 100)
        """
        if 0 <= duty_cycle <= 100:
            self.pwm.ChangeDutyCycle(duty_cycle)
            self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.PWM, duty_cycle)
        else:
            raise ValueError("Duty cycle must be between 0 and 100")
        
    def set_pwm_duty_cycle_wrapper_for_console_program(self, duty_cycle_str):
        """
        This is necessary b/c console input is stored as string by default
        """
        duty_cycle = int(duty_cycle_str)
        self.set_pwm_duty_cycle(duty_cycle)

    def shutdown(self):
        """
        Shuts down this subsystem's activity
        """
        self.pwm.stop() # Frees up the gpio pin reserved for pwm
        self.turn_off() # Turn off the motor for the driver
        self.status.setStatusFieldTupleValue(PumpWater.FieldKeys.ON_OFF_STATE, PumpWater.OnOffEnum.OFF)
        if self.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == "Automatic":
            self.switch_to_manual() # Switch to manual before closing since this action terminates active automatic threads for us automatically
            
        # CONVENTION: GPIO Setup and Cleanup done by outermost entity
        if self.status.isTopLevelStatusObject:
            GPIO_Utility.gpioCleanup()
        
if __name__ == "__main__":
    from PumpWaterTestCases import PumpWaterTestCases
    
    PumpWaterTestCases.testPumpDriverBasic()
    
    exit()