import re
import time
from enum import Enum

# Won't bother with =, >=, nor <= since = is a very rare edge case
class Relation(Enum):
    GREATER_THAN = 1
    LESS_THAN = 2

# Class for creating measurement objects that contain both a numerical value and units
class Measurement():
    def __init__(self, val, units):
        self.val = val
        self.units = units
        
# this class will hold two pieces of information
# relation
# rightOperand
# NOTE: Left operand will not be a part of this class
class Condition():
    def __init__(self, relation, rightOperand):
        self.relation = relation
        self.rightOperand = rightOperand
    
# NOTE: This is meant for extracting from AtlasI2C device "R" command responses which follows a certain format
def extract_num_val(device_response):
    try:
        # Use regular expression to find numbers in the response
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", device_response)
        # Assuming that the response always follows the same format (which it does), we want to find the second expression that matches the regular expression
        # NOTE: We return the second expression because the first expression is the address number
        return float(matches[1]) if matches else None
    except:
        print("Issue reading value from sensor")
        exit()
        
    
# for the format of specific messages, see page 44 of pH_EZO_Datasheet.pdf
def send_message_and_return_response(device, message):
    """
    Sends a message to an I2C device and reads the response.

    Parameters:
    - device: An instance of the AtlasI2C class.
    - message: The message (command) to send to the device.

    Returns:
    The response from the I2C device as a string.
    """
    try:
        # Send the command/message to the device
        device.write(message)

        command_timeout = device.get_command_timeout(message)
        time.sleep(command_timeout)
        response = device.read()
        
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None