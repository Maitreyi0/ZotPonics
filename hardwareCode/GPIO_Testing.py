import RPi.GPIO as GPIO

# Set BCM mode
GPIO.setmode(GPIO.BCM)

# Define the pins
pins_to_turn_off = [6, 5]

# Set up the pins as outputs and turn them off
for pin in pins_to_turn_off:
    GPIO.setup(pin, GPIO.OUT)  # Set pin as output
    GPIO.output(pin, GPIO.LOW)  # Turn the pin off

# Cleanup (optional: remove this if you want the pins to stay in their state)
# GPIO.cleanup()

print("Pins 6 and 5 have been turned off.")

input("Input anything to end program")