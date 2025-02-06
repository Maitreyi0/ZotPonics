import RPi.GPIO as GPIO
import time

# Pin setup
PIN = 26  # GPIO 26

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(PIN, GPIO.OUT)  # Set GPIO 26 as output

try:
    # Set GPIO 26 HIGH
    GPIO.output(PIN, GPIO.HIGH)
    print("GPIO 26 is HIGH. Press Ctrl+C to turn it LOW.")

    # Keep the program running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Handle the interrupt to turn GPIO 26 LOW
    print("\nKeyboard interrupt detected! Turning GPIO 26 LOW.")
    GPIO.output(PIN, GPIO.LOW)

finally:
    # Clean up GPIO
    GPIO.cleanup()
    print("GPIO cleanup complete. Exiting program.")