import RPi.GPIO as GPIO
import time

class LimitSwitch:
    """
    This will have a pull-up resistor so triggering the limit switch will bring it from HIGH to LOW
    """
    def __init__(self, NO_pin, interrupt_handle_function, interrupt_handle_function_args_list):
        self.NO_pin = NO_pin
        self.interrupt_handle_function = interrupt_handle_function
        self.interrupt_handle_function_args_list = interrupt_handle_function_args_list
        
    def init_interrupt_pin_and_service(self):
        """
        Initializes the NO_pin to be input and initializes the interrupt service
        """
        GPIO.setup(self.NO_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.NO_pin, GPIO.BOTH, callback=self.interrupt_callback, bouncetime=200)

    # Interrupt handler function
    def interrupt_callback(self, channel):
        """
        NOTE: The channel must be included as an argument even if not used
        """
        self.interrupt_handle_function(*self.interrupt_handle_function_args_list)

if __name__ == "__main__":
    import LimitSwitchTestCases
    import GPIO_Utility
    import traceback
    
    GPIO_Utility.setModeBCM()
    try:
        LimitSwitchTestCases.test_simple()
    except Exception as e:
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {e}")
        print("Traceback:")
        traceback.print_exc()  # Shows full traceback
    finally:
        GPIO_Utility.gpioCleanup()