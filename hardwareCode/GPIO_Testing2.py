import RPi.GPIO as GPIO
import time

# Setup
stepPin = 6  # GPIO pin connected to the step pin of the motor driver
stepsPerRevolution = 200  # Number of steps per revolution (adjust for your motor)

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(stepPin, GPIO.OUT)  # Set the step pin as an output

# Spin the stepper motor 1 revolution slowly
for i in range(stepsPerRevolution):
    # These two lines result in 1 step
    GPIO.output(stepPin, GPIO.HIGH)
    time.sleep(0.002)  # Delay for 2000 microseconds (2 ms)
    GPIO.output(stepPin, GPIO.LOW)
    time.sleep(0.002)  # Delay for 2000 microseconds (2 ms)

# Cleanup
GPIO.cleanup()
print("Stepper motor completed one revolution.")