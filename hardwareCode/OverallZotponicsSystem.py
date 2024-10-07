class OverallZotPonicsSystem:
    """
    This class will bring everything together
    
    Current Components Supported:
    - GUI Components:
       - Manual Adjustment Window
    - Hydroponics System Components:
       - pH and EC subsystem
       
    Additional Notes:
    - The gui components, hydroponics system components, and server components will not directly interact with each other. It will be the overall system object that communicates directly with these three different groups directly
    
    """
    def __init__(self, )