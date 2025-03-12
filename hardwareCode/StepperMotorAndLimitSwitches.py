from Status import Status

class StepperMotorAndLimitSwitches:
    
    class FieldKeys(Status.FieldKeys):
        DIR_A_HALT = "directionA_Halt" 
        """
        NOTE: An actual interrupt will trigger this field's value to change (e.g., limit switch), on both the rising edge and falling edge
        - For a pull-up resistor interrupt, LOW -> PREVENT MOTION IN DIRECTION A, HIGH -> ALLOW MOTION IN DIRECTION A
        """
        DIR_B_HALT = "directionB_Halt"
        """
        NOTE: An actual interrupt will trigger this field's value to change (e.g., limit switch), on both the rising edge and falling edge
        - For a pull-up resistor interrupt, LOW -> PREVENT MOTION IN DIRECTION B, HIGH -> ALLOW MOTION IN DIRECTION B
        """
        
    def __init__(self, stepperMotor, dirA_LimitSwitch, dirB_LimitSwitch):
        
    