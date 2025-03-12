import RPi.GPIO as GPIO
import time
import GPIO_Utility
from Status import Status

class StepperMotor:
    
    STEPS_PER_REVOLUTION = 200 # Could change based on the specific stepper motor driver used
    DELAY = 0.001
    """
    Time in seconds for the high state of the step pulse, depending on the stepper motor driver, there is a minimum for this
        - 1 ms seems to work fine
        - The lower the delay, the faster we can step
    """
    
    def __init__(self, step_pin, dir_pin):
        """
        Initialize a StepperMotor instance.

        Args:
        step_pin (int): GPIO pin connected to the step pin of the motor driver.
        dir_pin (int): GPIO pin connected to the direction pin of the motor driver.
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        
        try:
            GPIO.setup(self.step_pin, GPIO.OUT)
            GPIO.setup(self.dir_pin, GPIO.OUT)
            
            # Initialize pins
            GPIO.output(self.step_pin, GPIO.LOW)
            GPIO.output(self.dir_pin, GPIO.LOW) # default direction corresponds with LOW (counter-clockwise)
        except Exception:
            print("Something went wrong trying to configure pins for stepper motor")
            
    def set_direction(self, clockwise=True):
        """
        Set the motor direction.

        Args:
        clockwise (bool): Set to True for clockwise, False for counterclockwise.
        """
        GPIO.output(self.dir_pin, GPIO.HIGH if clockwise else GPIO.LOW)

    def step(self):
        # Perform a single step.
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(StepperMotor.DELAY)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(StepperMotor.DELAY) # Just to be safe, will match the LOW duration with the HIGH duration
        
    def perform_full_revolution(self):
        for i in range(0, StepperMotor.STEPS_PER_REVOLUTION):
            self.step()
        
        
if __name__ == "__main__":
    import StepperMotorTestCases
    import GPIO_Utility
    
    GPIO_Utility.setModeBCM()
    try:
        StepperMotorTestCases.test_motion_simple()
        print("Test Complete...")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        GPIO_Utility.gpioCleanup()