import RPi.GPIO as GPIO

def setModeBCM():
    # could mean that a mode hasn't been set yet or the set mode isn't BCM
    if GPIO.getmode() != GPIO.BCM:
        GPIO.setmode(GPIO.BCM)
    return

def initializeOutputPin(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    
def initializeInputPin(pin):
    GPIO.setup(pin, GPIO.IN)
    
def gpioCleanup():
    GPIO.cleanup()