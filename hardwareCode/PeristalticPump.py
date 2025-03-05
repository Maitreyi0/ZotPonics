import RPi.GPIO as GPIO
import GPIO_Utility
import datetime
from Status import Status
import threading as th
import time

# Overview:
# - this class is for the pump subsystem which involves the pump and a corresponding relay
# - the relay is needed because the pump requires 12V to operate and the rpi can't supply this directly

class PeristalticPump:
    
    # Extend the base FieldKeys class for the peristaltic pump
    class FieldKeys(Status.FieldKeys):
        PIN = "pin"
        PUMP_ACTIVE = "pumpActive"
    
    DEFAULT_DELAY_SECONDS = 1 # the default value for the turnOnWithDuration method's seconds argument
    # it shouldn't be too high to avoid changing the properties of the water too much
    
    # pin: this is the pin that will be used to activate the pump (when the pin is set to HIGH)
    # - this pin can directly be connected with the anode of the pump or a relay IN pin
    # alias: this is a name we give to the pump just so we can identify it
    def __init__(self, pin, alias, isOutermostEntity, debugMode):
        
        # so that we don't have to separately run this command before initializing pump object
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()
            
        self.status = Status(alias, isOutermostEntity, debugMode)
        
        self.pin = pin
        # self.status.addStatusFieldTuple(PeristalticPump.FieldKeys.ALIAS, alias) # this one not necessary since alias done by status
        
        fieldKeys = [value for key, value in PeristalticPump.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            self.status.addStatusFieldTuple(fieldKey, None)
        
        self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PIN, pin)
        self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PUMP_ACTIVE, False)
        
        # True when voltage is being supplied, False when voltage is not being supplied
        self.onWithDurationSeconds = PeristalticPump.DEFAULT_DELAY_SECONDS # start with the default, can change later on
        
        GPIO_Utility.initializeOutputPin(pin)

    def turnOn(self):
        if(self.status.getStatusFieldTupleValueUsingKey("pumpActive") == False):
            # turn on the pump
            GPIO.output(self.pin, GPIO.HIGH)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PUMP_ACTIVE, True)
        else:
            raise Exception("peristaltic pump wasn't off when trying to turn on")
        
    def turnOff(self):
        # note: turn off will only interact with the "on" mode, it won't do anything to "onWithDuration"
        if(self.status.getStatusFieldTupleValueUsingKey(PeristalticPump.FieldKeys.PUMP_ACTIVE) == True):
            # turn off the pump
            GPIO.output(self.pin, GPIO.LOW)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PUMP_ACTIVE, False)

        else:
            raise Exception("peristaltic pump wasn't off when trying to turn on")
        
    def turnOnWithDuration(self, seconds):
        
        if (self.status.getStatusFieldTupleValueUsingKey(PeristalticPump.FieldKeys.PUMP_ACTIVE) == False):
            # turn on pump
            GPIO.output(self.pin, GPIO.HIGH)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PUMP_ACTIVE, True)
            
            # initialize timer
            startTime = datetime.datetime.now()
            while (datetime.datetime.now() - startTime).total_seconds() < seconds:
                pass
            
            # turn off pump
            GPIO.output(self.pin, GPIO.LOW)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue(PeristalticPump.FieldKeys.PUMP_ACTIVE, False)
        else:
            raise Exception("Tried to turn on pump with duration when already on")

def test_case_turn_on_with_duration(pumpPin):
    pPumpPin = pumpPin
    
    pump = PeristalticPump(pPumpPin, "pPump", True, False)
    
    input("Input anything to turn on with duration: ")
    
    pump.turnOnWithDuration(pump.onWithDurationSeconds)
    
    input("Input anything to end program: ")
    
    print("This is the final state of the status activity queue")
    while not pump.status.statusActivityQueue.empty():
        item = pump.status.statusActivityQueue.get()
        print(item)
    
    GPIO_Utility.gpioCleanup()
    
    exit()

if __name__ == "__main__":
    pumpPH_UP = 22
    pumpPH_DOWN = 23
    pumpBASE_A = 21
    pumpBASE_B = 20
    
    # test_case_turn_on_with_duration(20)
    # test_case_turn_on_with_duration(21)
    # test_case_turn_on_with_duration(23)
    test_case_turn_on_with_duration(22)