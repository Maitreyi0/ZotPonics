import threading
import queue
import time

from Status import Status

import GPIO_Utility
from PeristalticPump import PeristalticPump
from AtlasI2C_Sensor import AtlasI2C_Sensor
from PumpWater import PumpWater

from MySQL_CommunicationManager import MySQL_ServerCommunicationManager
from MenuManagementSystem import MenuManagementSystem

class OverallSystem:
    
    manualOnlyCommands = [
        "[Special]-switch_to_automatic",
        # Have to create methods to insert the following commands
        "[PumpWater]-manual_turn_on_pump",
        "[PumpWater]-manual_turn_off_pump",
        "[PumpWater]-turn_on_with_duration",
        "[pHUpPump]-manual_turn_on_pump",
        "[pHUpPump]-manual_turn_off_pump",
        "[pHDownPump]-manual_turn_on_pump",
        "[pHDownPump]-manual_turn_off_pump",
        "[baseA]-manual_turn_on_pump",
        "[baseA]-manual_turn_off_pump",
        "[baseB]-manual_turn_on_pump",
        "[baseB]-manual_turn_off_pump",
         
    ] # these commands can only be used in manual mode
    
    automaticOnlyCommands = [
        "[Special]-switch_to_manual",
    ] # these commands can only be used when in automatic mode
    
    universalCommands = [] # these commands can be used when the system is in either manual or automatic mode
    
    class FieldKeys(Status.FieldKeys):
        OPERATION_MODE = "operationMode" # either manual or automatic
        PH_UP_PUMP_CONNECTED = "pH_UpPumpConnected"
        PH_DOWN_PUMP_CONNECTED = "pH_DownPumpConnected"
        BASE_A_PUMP_CONNECTED = "baseA_PumpConnected"
        BASE_B_PUMP_CONNECTED = "baseB_PumpConnected"
        PH_SENSOR_CONNECTED = "pH_SensorConnected"
        EC_SENSOR_CONNECTED = "ec_SensorConnected"
        PUMP_WATER_CONNECTED = "pumpWaterConnected"
        MY_SQL_COMMUNICATION_MANAGER_CONNECTED = "mySQL_CommunicationManagerConnected"
        MENU_MANAGEMENT_SYSTEM_CONNECTED = "menuManagementSystemConnected"
        
    class OperationModeEnum:
        AUTO = "Automatic"
        MANUAL = "Manual"
    
    def __init__(self, alias, pH_UpPump : PeristalticPump, pH_DownPump : PeristalticPump, baseA_Pump : PeristalticPump, baseB_Pump : PeristalticPump, pH_Sensor : AtlasI2C_Sensor, ec_Sensor : AtlasI2C_Sensor, pumpWater : PumpWater, mySQL_CommunicationManager : MySQL_ServerCommunicationManager, menuManagementSystem : MenuManagementSystem, isOutermostEntity : bool, ):
        self.pH_UpPump = pH_UpPump
        self.pH_DownPump = pH_DownPump
        self.baseA_Pump = baseA_Pump
        self.baseB_Pump = baseB_Pump
        self.pH_Sensor = pH_Sensor
        self.ec_Sensor = ec_Sensor
        self.pumpWater = pumpWater
        self.mySQL_CommunicationManager = mySQL_CommunicationManager
        self.menuManagementSystem = menuManagementSystem
        
        # init overall system status
        self.status = Status(alias=alias, isTopLevel=isOutermostEntity, debugModeOn=False)
        
        # initialize the status keys
        fieldKeys = [value for key, value in OverallSystem.FieldKeys.__dict__.items() if not key.startswith("__")]
        for fieldKey in fieldKeys:
            self.status.addStatusFieldTuple(fieldKey, None)
        
        # set the status values such that none have None values
        
        # start off as manual mode
        self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.OPERATION_MODE, OverallSystem.OperationModeEnum.MANUAL)
        
        if pH_UpPump != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_UP_PUMP_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_UP_PUMP_CONNECTED, False)
            
        if pH_DownPump != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_DOWN_PUMP_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_DOWN_PUMP_CONNECTED, False)
            
        if baseA_Pump != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.BASE_A_PUMP_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.BASE_A_PUMP_CONNECTED, False)
            
        if baseB_Pump != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.BASE_B_PUMP_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.BASE_B_PUMP_CONNECTED, False)
        
        if pH_Sensor != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_SENSOR_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PH_SENSOR_CONNECTED, False)
            
        if ec_Sensor != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.EC_SENSOR_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.EC_SENSOR_CONNECTED, False)
            
        if pumpWater != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PUMP_WATER_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.PUMP_WATER_CONNECTED, False) 
        
        if mySQL_CommunicationManager != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.MY_SQL_COMMUNICATION_MANAGER_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.MY_SQL_COMMUNICATION_MANAGER_CONNECTED, False)

        if menuManagementSystem != None:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.MENU_MANAGEMENT_SYSTEM_CONNECTED, True)
        else:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.MENU_MANAGEMENT_SYSTEM_CONNECTED, False)
            
    def attach_communication_manager(self, mySQL_CommunicationManager : MySQL_ServerCommunicationManager):
        """
        We need this because at the time of overallSystem object creation, we assume that mySQL_CommunicationManager doesn't exist yet
        """
        self.mySQL_CommunicationManager = mySQL_CommunicationManager
        self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.MY_SQL_COMMUNICATION_MANAGER_CONNECTED, True)
    
    def add_menu_management_system_options_manual_only(self):
        if self.menuManagementSystem is not None:
            self.menuManagementSystem.add_option("[Special]-switch_to_automatic", self.target_for_switch_to_automatic_command)
            
            if self.pumpWater is not None:
                self.menuManagementSystem.add_option("[PumpWater]-manual_turn_on_pump", self.pumpWater.turn_on)
                self.menuManagementSystem.add_option("[PumpWater]-manual_turn_off_pump", self.pumpWater.turn_off)
                self.menuManagementSystem.add_option("[PumpWater]-turn_on_with_duration", self.pumpWater.turnOnWithDuration)
            if self.pH_UpPump is not None:
                self.menuManagementSystem.add_option("[pHUpPump]-manual_turn_on_pump", self.pH_UpPump.turnOn)
                self.menuManagementSystem.add_option("[pHUpPump]-manual_turn_off_pump", self.pH_UpPump.turnOff)
            if self.pH_DownPump is not None:
                self.menuManagementSystem.add_option("[pHDownPump]-manual_turn_on_pump", self.pH_DownPump.turnOn)
                self.menuManagementSystem.add_option("[pHDownPump]-manual_turn_off_pump", self.pH_DownPump.turnOff)
            if self.baseA_Pump is not None:
                self.menuManagementSystem.add_option("[baseA]-manual_turn_on_pump", self.baseA_Pump.turnOn)
                self.menuManagementSystem.add_option("[baseA]-manual_turn_off_pump", self.baseA_Pump.turnOff)
            if self.baseB_Pump is not None:
                self.menuManagementSystem.add_option("[baseB]-manual_turn_on_pump", self.baseB_Pump.turnOn)
                self.menuManagementSystem.add_option("[baseB]-manual_turn_off_pump", self.baseB_Pump.turnOff)
            
        else:
            print("Menu Management System not attached")
    
    def target_for_switch_to_manual_command(self):
        """
        This is the corresponding function for the command option, [Special]-switch_to_manual
        """
        if self.pH_Sensor is not None:
            if self.pH_Sensor.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == True:
                self.pH_Sensor.terminateContPollThread()
        
        if self.ec_Sensor is not None:
            if self.ec_Sensor.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == True:
                self.ec_Sensor.terminateContPollThread()
        
        if self.pumpWater is not None:
            if self.pumpWater.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == PumpWater.ModeEnum.AUTO:
                if self.pumpWater.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == True:
                    self.pumpWater.terminate_automatic_thread()
                self.pumpWater.switch_to_manual()
                
        self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.OPERATION_MODE, OverallSystem.OperationModeEnum.MANUAL)
    
    def add_menu_management_system_options_automatic_only(self):
        if self.menuManagementSystem is not None:
            self.menuManagementSystem.add_option("[Special]-switch_to_manual", self.target_for_switch_to_manual_command)
        else:
            print("Menu Management System not attached")
    
    def target_for_switch_to_automatic_command(self):
        """
        This is the corresponding function for the command option, [Special]-switch_to_automatic
        """
        if self.pH_Sensor != None:
            if self.pH_Sensor.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == False:
                self.pH_Sensor.startContPollThread()
        
        if self.ec_Sensor != None:
            if self.ec_Sensor.status.getStatusFieldTupleValueUsingKey(AtlasI2C_Sensor.FieldKeys.CONT_POLLING_THREAD_ACTIVE) == False:
                self.ec_Sensor.startContPollThread()
            
        if self.pumpWater != None:
            if self.pumpWater.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.MODE) == PumpWater.ModeEnum.MANUAL:
                self.pumpWater.switch_to_automatic()
                if self.pumpWater.status.getStatusFieldTupleValueUsingKey(PumpWater.FieldKeys.AUTO_CYCLE_THREAD_ACTIVE) == False:
                    self.pumpWater.start_automatic_thread()
                    
        self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.OPERATION_MODE, OverallSystem.OperationModeEnum.AUTO)
        
    
    def add_menu_management_system_options_special_options(self):
        """
        These don't come from any specific subsystem, they will dictate the behavior of menu_management_system to manage what commands can actually be enqueued
        """
        if self.menu_management_system != None:
            self.menu_management_system.add_option("[Special]-switch_to_manual", self.switch_to_manual)
            self.menu_management_system.add_option("[Special]-switch_to_automatic", self.switch_to_automatic)
    
    def switch_to_manual(self):
        if self.status.getStatusFieldTupleValueUsingKey(OverallSystem.FieldKeys.OPERATION_MODE) == OverallSystem.OperationModeEnum.AUTO:
            self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.OPERATION_MODE, OverallSystem.OperationModeEnum.MANUAL)
            # If switching from manual to automatic, should cancel all the automatic threads
            if self.pH_Sensor != None:
                # If active will terminate
                self.pH_Sensor.terminateCondThread()
                self.pH_Sensor.terminateContPollThread()
            
            if self.ec_Sensor != None:
                # If active will terminate
                self.ec_Sensor.terminateCondThread()
                self.ec_Sensor.terminateContPollThread()
                
            if self.pumpWater != None:
                self.pumpWater.switch_to_manual()
    
    def switch_to_automatic(self):
        """
        NOTE: During automatic mode, the user should not be able to trigger any commands. The only commands they should be able to trigger will be to switch back to manual mode
        """
        # Turn on/restart all the relevant threads
        self.status.setStatusFieldTupleValue(OverallSystem.FieldKeys.OPERATION_MODE, OverallSystem.OperationModeEnum.AUTO)
        
        NotImplemented

    
if __name__ == "__main__":
    import OverallSystemTestCases
    try:
        OverallSystemTestCases.test_local_command_insertion()
    except KeyboardInterrupt as e:
        GPIO_Utility.gpioCleanup()
    
    exit()