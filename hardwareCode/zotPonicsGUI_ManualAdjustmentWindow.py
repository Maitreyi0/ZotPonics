import GPIO_Utility
import tkinter as tk
from AtlasI2C_SensorAndPumps import AtlasI2C_SensorAndPumps
import threading as th
from Status import Status
import time

class StatusLabelAndManualActivationButtonWidget:
    """
    A statusLabelAndButtonWidget object includes a label that will store the status of a component and the button will perform some action related to that component
    """
    def __init__(self, parent, label_text, button_text, buttonCallback, buttonCallbackArgsList : list):
        # Create a frame to hold the label and button
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH)

        # Text box (label here)
        self.label = tk.Label(self.frame, text=label_text, font=("Helvetica", 14), relief=tk.SOLID, width=15, height=7)
        self.label.pack(pady=5, expand=True, fill=tk.BOTH)

        # Button
        self.button = tk.Button(self.frame, text=button_text, bg="green", fg="white", font=("Helvetica", 12), command=lambda: buttonCallback(*buttonCallbackArgsList))
        self.button.pack(pady=5, expand=True, fill=tk.BOTH)

    def update_label(self, new_text):
        """Update the label text."""
        self.label.config(text=new_text)

    def configure_button(self, command):
        """Attach a command to the button."""
        self.button.config(command=command)

class ManualAdjustmentWindow:
    def __init__(self, root, alias, sensorAndPumpsObject1 : AtlasI2C_SensorAndPumps, sensorAndPumpsObject2 : AtlasI2C_SensorAndPumps, isOuterMostEntity : bool, debugMode : bool):
        """_summary_

        Args:
            NOTE: We need two because one is for (pH and pumps) and the other is for (EC and pumps)
            sensorAndPumpsObject1: One of two sensor and pump subsystem objects.
            sensorAndPumpsObject2: The other sensor and pump subsystem objects.
        """
        
        # Immediate Level Status Object Stuff
        # -------------------------------------------
        self.status = Status(topLevel=isOuterMostEntity, debugMode=debugMode)
        self.status.addStatusFieldTuple("alias", alias) # this will be used in the title of the corresponding window
        self.status.addStatusFieldTuple("updateLabelsThreadActive", False) # false initially
        # -------------------------------------------
        
        # GUI Stuff
        # -------------------------------------------
        
        self.root = root
        self.root.title(alias)
        self.debugMode = debugMode

        # Create a container frame to hold all widgets
        self.container = tk.Frame(self.root)
        self.container.pack(padx=10, pady=10, fill=tk.BOTH)
        
        # List to store all StatusWidget instances
        self.listStatusWidgets = []
        
        self.updateLabelsThread = None # Will hold the update labels thread, for updating the labels in the window
        
        # These lists will be used by the updateLabels thread
        self.listStatusObjects = []
        
        # populating the status objects list
        self.listStatusObjects.append(sensorAndPumpsObject1.sensor.status)
        for pump in sensorAndPumpsObject1.pumpList:
            pumpStatus = pump.status
            self.listStatusObjects.append(pumpStatus)
        
        # -------------------------------------------
        
        # Sensor and Pumps Subsystems Stuff (First One)
        # -------------------------------------------
        
        sensorAndPumpsObject1.status.updateStatusDict() # to prepare up-to-date values for the GUI to extract data from

        # Update the sensor status string and then create widget with that as the initial string
        sensorAndPumpsObject1.sensor.status.updateStatusString(True)
        sensorStatusString = sensorAndPumpsObject1.sensor.status.statusString
        self.add_widget(sensorStatusString, "Get Reading", sensorAndPumpsObject1.sensor.getReading, [])
        
        # Update pump status strings and create the widgets
        for pump in sensorAndPumpsObject1.pumpList:
            pump.status.updateStatusString(True)
            pumpStatusString = pump.status.statusString
            self.add_widget(pumpStatusString, "Dispense", pump.turnOnWithDuration, [pump.onWithDurationSeconds])
        
        # -------------------------------------------
        
        # Sensor and Pumps Subsystems Stuff (Second One)
        # -------------------------------------------
        
        # -------------------------------------------

    def add_widget(self, label_text, button_text, buttonCallback, buttonCallbackArgsList):
        """Create and add a new StatusWidget to the container."""
        widget = StatusLabelAndManualActivationButtonWidget(self.container, label_text, button_text, buttonCallback, buttonCallbackArgsList)
        self.listStatusWidgets.append(widget)  # Store the widget instance so that it can be accessed

    def get_widget(self, index):
        """Retrieve a specific widget by index."""
        if 0 <= index < len(self.listStatusWidgets):
            return self.listStatusWidgets[index]
        else:
            print("Invalid index.")
            return None
        
    def startUpdateLabelsThread(self) -> th.Thread:
        """
        This thread will update all labels in listStatusObjects by acquiring the statusStrings from the status objects in listStatusObjects
        NOTE: The indexes of the lists should match
        """
        if self.status.getStatusFieldTupleValue("updateLabelsThreadActive") == False:
            self.updateLabelsThread = th.Thread(target=self.updateLabelsThreadTarget)
            
            self.status.setStatusFieldTupleValue("updateLabelsThreadActive", True)
            
            self.updateLabelsThread.start()
        else:
            raise Exception("Could not create cond thread, check thread variables")
        
    
    def updateLabelsThreadTarget(self):
        while self.status.getStatusFieldTupleValue("updateLabelsThreadActive") == True:
            
            lenListStatusWidgets = len(self.listStatusWidgets)
            
            for i in range (0, lenListStatusWidgets):
                currentWidget = self.lenListStatusWidgets[i]
                currentStatus = self.listStatusObjects[i]
                currentStatusString = currentStatus.statusString
                
                currentWidget.update_label(currentStatusString)
            
            time.sleep(0.5)
            
    def terminateUpdateLabelsThread(self):
        
        if self.status.getStatusFieldTupleValue("updateLabelsThreadActive") == True:
            self.status.setStatusFieldTupleValue("updateLabelsThreadActive", False)
        else:
            raise Exception("Could not terminate cond thread, check thread variables")
        
    def run(self):
        self.root.mainloop()

def testCase():
    baseA_Pin = 20
    baseB_Pin = 21
    
    sensorAndPumpsSubsystem = AtlasI2C_SensorAndPumps("ec_Subsystem", baseA_Pin, "baseA", baseB_Pin, "baseB", "EC", False, True, False, True)
    
    root = tk.Tk()
    root.geometry("800x600")
    app = ManualAdjustmentWindow(root, sensorAndPumpsSubsystem)
    app.run()
    
    app.terminateUpdateLabelsThread()
    GPIO_Utility.gpioCleanup()
    exit()

if __name__ == "__main__":
    testCase()