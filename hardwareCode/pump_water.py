import RPi.GPIO as GPIO
from Status import Status
import threading as th
import GPIO_Utility

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

class PumpDriver:
    
    def __init__(self, in1_pin, in2_pin, pwm_pin, alias, isOutermostEntity, frequency=1000):
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
        self.alias = alias
        self.isOutermostEntity = isOutermostEntity
        # CONVENTION: GPIO Setup and Cleanup done by outermost entity
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()
        self.frequency = frequency
        
        # GPIO mode should be set at this point
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm_pin, self.frequency)
        self.pwm.start(0)  # Start with 0% duty cycle (off)
        
        # Turn off initially
        self.turn_off()

    def turn_on(self):
        """Turns on the pump by setting IN1 HIGH and IN2 LOW."""
        GPIO.output(self.in1_pin, GPIO.HIGH)
        GPIO.output(self.in2_pin, GPIO.LOW)

    def turn_off(self):
        """Turns off the pump by setting both IN1 and IN2 LOW."""
        GPIO.output(self.in1_pin, GPIO.LOW)
        GPIO.output(self.in2_pin, GPIO.LOW)

    def set_pwm(self, duty_cycle):
        """
        Set the PWM duty cycle.

        :param duty_cycle: Duty cycle (0 to 100)
        """
        if 0 <= duty_cycle <= 100:
            self.pwm.ChangeDutyCycle(duty_cycle)
        else:
            raise ValueError("Duty cycle must be between 0 and 100")

    def cleanup(self):
        """Clean up GPIO resources."""
        self.pwm.stop()
        self.turn_off()
        # CONVENTION: GPIO Setup and Cleanup done by outermost entity
        if self.isOutermostEntity:
            GPIO_Utility.gpioCleanup()
        
if __name__ == "__main__":
    
    import time
    
    pumpDriver = PumpDriver(in1_pin=5,in2_pin=6,pwm_pin=12,alias="pumpDriver",isOutermostEntity=True)
    pumpDriver.turn_on()
    pumpDriver.set_pwm(50)
    time.sleep(1)
    pumpDriver.cleanup()
    
    exit()