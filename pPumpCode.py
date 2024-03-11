import RPi.GPIO as GPIO
import datetime

delay_seconds = 1
RELAY_IN_1 = 21
# RELAY_IN_2 = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_IN_1, GPIO.OUT)
# GPIO.setup(RELAY_IN_2, GPIO.OUT)

GPIO.output(RELAY_IN_1, GPIO.HIGH)
# GPIO.output(RELAY_IN_2, GPIO.HIGH)

start_time = datetime.datetime.now()

while(datetime.datetime.now() - start_time).total_seconds() < delay_seconds:
    pass
    
GPIO.cleanup()