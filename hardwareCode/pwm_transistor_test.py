import RPi.GPIO as GPIO
import time

# Pin setup
PWM_PIN = 26  # GPIO 26
DUTY_CYCLE = 50  # 50% duty cycle
FREQ = 50  # 50 Hz (20 ms period)

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(PWM_PIN, GPIO.OUT)

# Create PWM instance on GPIO 26
pwm = GPIO.PWM(PWM_PIN, FREQ)  # Frequency = 50 Hz

try:
    print("Starting PWM on GPIO 26. Press Ctrl+C to stop.")
    while True:
        print("PWM ON for 5 seconds")
        pwm.start(DUTY_CYCLE)  # Turn PWM on with 50% duty cycle
        time.sleep(5)  # Wait for 5 seconds

        print("PWM OFF for 5 seconds")
        pwm.stop()  # Turn PWM off
        time.sleep(5)  # Wait for 5 seconds

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Cleaning up GPIO.")

finally:
    # Stop PWM and set pin to high-impedance mode
    print("Stopping PWM and setting GPIO pin to high-impedance mode.")
    pwm.stop()
    GPIO.setup(PWM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_OFF)  # Set pin to Hi-Z
    GPIO.cleanup()
    print("Pin is now in high-impedance state. Exiting program.")