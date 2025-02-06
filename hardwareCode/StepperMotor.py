import RPi.GPIO as GPIO
import time
from my_utils import MenuProgram as MP
import GPIO_Utility

class StepperMotor:
    
    stepsPerRevolution = 200
    
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
            GPIO.output(self.dir_pin, GPIO.LOW)
        except Exception:
            print("Something went wrong trying to configure pins for stepper motor")
            

    def set_direction(self, clockwise=True):
        """
        Set the motor direction.

        Args:
        clockwise (bool): Set to True for clockwise, False for counterclockwise.
        """
        GPIO.output(self.dir_pin, GPIO.HIGH if clockwise else GPIO.LOW)

    def step(self, delay=0.001):
        """
        Perform a single step.

        Args:
        delay (float): Time in seconds for the high state of the step pulse.
                      Adjust for your driver's step timing requirements.
        """
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(delay)
        
    def perform_full_revolution(self):
        for i in range(0, StepperMotor.stepsPerRevolution):
            self.step()

    def cleanup(self):
        """
        Clean up the GPIO pins when done.
        """
        GPIO.cleanup()
        
if __name__ == "__main__":
    
    # Initialize pins and stepper motor
    GPIO_Utility.setModeBCM()
    # Vertical Stepper Motor
    stepperMotorVert = StepperMotor(6, 5)
    # Horizontal Stepper Motor 1
    stepperMotorHorz1 = StepperMotor(25, 24)
    # Horizontal Stepper Motor 2
    stepperMotorHorz2 = StepperMotor(18, 17)
    
    menuProgram = MP.MenuProgram()
    menuProgram.add_option("Rotate vert stepper motor one full revolution", stepperMotorVert.perform_full_revolution)
    menuProgram.add_option("Rotate horz 1 stepper motor one full revolution", stepperMotorHorz1.perform_full_revolution)
    menuProgram.add_option("Rotate horz 2 stepper motor one full revolution", stepperMotorHorz2.perform_full_revolution)
    menuProgram.run()
    
    GPIO_Utility.gpioCleanup()