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
    
    DEFAULT_DELAY_SECONDS = 1 # the default value for the turnOnWithDuration method's seconds argument
    # it shouldn't be too high to avoid changing the properties of the water too much
    
    # pin: this is the pin that will be used to activate the pump (when the pin is set to HIGH)
    # - this pin can directly be connected with the anode of the pump or a relay IN pin
    # alias: this is a name we give to the pump just so we can identify it
    def __init__(self, pin, alias, isOutermostEntity, debugMode):
        
        # so that we don't have to separately run this command before initializing pump object
        if isOutermostEntity:
            GPIO_Utility.setModeBCM()
            
        self.status = Status(isOutermostEntity, debugMode)   
        
        self.pin = pin
        self.printID = "[" + alias + "]: "
        self.status.addStatusFieldTuple("alias", alias)
        self.status.addStatusFieldTuple("pin", pin)
        self.status.addStatusFieldTuple("pumpActive", False) # True when voltage is being supplied, False when voltage is not being supplied
        self.status.addStatusFieldTuple("activeDescription", "")
        self.onWithDurationSeconds = PeristalticPump.DEFAULT_DELAY_SECONDS # start with the default, can change later on
        
        GPIO_Utility.initializeOutputPin(pin)

    def turnOn(self):
        if(self.status.getStatusFieldTupleValue("pumpActive") == False):
            # turn on the pump
            GPIO.output(self.pin, GPIO.HIGH)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue("pumpActive", True)
            self.status.setStatusFieldTupleValue("activeDescription", "On, with no set duration")
        else:
            raise Exception(self.printID + "pump wasn't off when trying to turn on")
        
    def turnOff(self):
        # note: turn off will only interact with the "on" mode, it won't do anything to "onWithDuration"
        if(self.status.getStatusFieldTupleValue("pumpActive") == True):
            # turn off the pump
            GPIO.output(self.pin, GPIO.LOW)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue("pumpActive", False)
            
            self.status.setActiveDescription("Off")
        else:
            raise Exception(self.printID + "pump wasn't on when trying to turn off")
        
    def turnOnWithDuration(self, seconds):
        
        if (self.status.getStatusFieldTupleValue("pumpActive") == False):
            # turn on pump
            GPIO.output(self.pin, GPIO.HIGH)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue("pumpActive", True)
            self.status.setStatusFieldTupleValue("activeDescription", "On, with duration of " + str(seconds) + " seconds")
            
            # initialize timer
            startTime = datetime.datetime.now()
            while (datetime.datetime.now() - startTime).total_seconds() < seconds:
                pass
            
            # turn off pump
            GPIO.output(self.pin, GPIO.LOW)
            
            # update status accordingly
            self.status.setStatusFieldTupleValue("pumpActive", False)
            self.status.setStatusFieldTupleValue("activeDescription", "Off")
        else:
            raise Exception("Tried to turn on pump with duration when already on")

    def threadTarget(self):
        while self.status.getStatusFieldTupleValue("pumpActive") == False:
            time.sleep(0.1)
        self.status.updateStatusDict()
        self.status.updateStatusString(True)
        print(self.status.statusString)
        

def testCase1(pumpPin):
    pPumpPin = pumpPin
    
    pump = PeristalticPump(pPumpPin, "pPump", True, False)
    
    input("Input anything to turn on with duration: ")
    
    pumpThread = th.Thread(target=pump.threadTarget)
    pumpThread.start()
    
    pump.turnOnWithDuration(pump.onWithDurationSeconds)
    
    pumpThread.join()

    pump.status.updateStatusDict()
    pump.status.updateStatusString(True)
    print(pump.status.statusString)
    
    input("Input anything to end program: ")
    
    GPIO_Utility.gpioCleanup()
    
    exit()

if __name__ == "__main__":
    testCase1(20)