#!/usr/bin/python

import io
import sys
import fcntl
import time
import copy
import string
from AtlasI2C import (
	 AtlasI2C
)
import re
import matplotlib.pyplot as plt

def print_devices(device_list, device):
    for i in device_list:
        if(i == device):
            print("--> " + i.get_device_info())
        else:
            print(" - " + i.get_device_info())
    #print("")
    
def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        try:
            moduletype = response.split(",")[1] 
            response = device.query("name,?").split(",")[1]
        except IndexError:
            print(">> WARNING: device at I2C address " + str(i) + " has not been identified as an EZO device, and will not be queried") 
            continue
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list 
       
def print_help_text():
    print('''
>> Atlas Scientific I2C sample code
>> Any commands entered are passed to the default target device via I2C except:
  - Help
      brings up this menu
  - List 
      lists the available I2C circuits.
      the --> indicates the target device that will receive individual commands
  - xxx:[command]
      sends the command to the device at I2C address xxx 
      and sets future communications to that address
      Ex: "102:status" will send the command status to address 102
  - all:[command]
      sends the command to all devices
  - Poll[,x.xx]
      command continuously polls all devices
      the optional argument [,x.xx] lets you set a polling time
      where x.xx is greater than the minimum %0.2f second timeout.
      by default it will poll every %0.2f seconds
>> Pressing ctrl-c will stop the polling
    ''' % (AtlasI2C.LONG_TIMEOUT, AtlasI2C.LONG_TIMEOUT))
       
def main():
    
    print_help_text()
    
    device_list = get_devices()
        
    device = device_list[0]
    
    response = send_and_read_message(device, "R")
    
    print(extractPHNumber(response))
    
    generateGraph(device, 10)
    
    
    # print_devices(device_list, device)
    
    # real_raw_input = vars(__builtins__).get('raw_input', input)
    
    # while True:
    
    #     user_cmd = real_raw_input(">> Enter command: ")
        
    #     # show all the available devices
    #     if user_cmd.upper().strip().startswith("LIST"):
    #         print_devices(device_list, device)
            
    #     # print the help text 
    #     elif user_cmd.upper().startswith("HELP"):
    #         print_help_text()
            
    #     # continuous polling command automatically polls the board
    #     elif user_cmd.upper().strip().startswith("POLL"):
    #         cmd_list = user_cmd.split(',')
    #         if len(cmd_list) > 1:
    #             delaytime = float(cmd_list[1])
    #         else:
    #             delaytime = device.long_timeout

    #         # check for polling time being too short, change it to the minimum timeout if too short
    #         if delaytime < device.long_timeout:
    #             print("Polling time is shorter than timeout, setting polling time to %0.2f" % device.long_timeout)
    #             delaytime = device.long_timeout
    #         try:
    #             while True:
    #                 print("-------press ctrl-c to stop the polling")
    #                 for dev in device_list:
    #                     dev.write("R")
    #                 time.sleep(delaytime)
    #                 for dev in device_list:
    #                     print(dev.read())
                
    #         except KeyboardInterrupt:       # catches the ctrl-c command, which breaks the loop above
    #             print("Continuous polling stopped")
    #             print_devices(device_list, device)
                
    #     # send a command to all the available devices
    #     elif user_cmd.upper().strip().startswith("ALL:"):
    #         cmd_list = user_cmd.split(":")
    #         for dev in device_list:
    #             dev.write(cmd_list[1])
                
# Code added myself:

# for specific messages, see page 44 of pH_EZO_Datasheet.pdf
def send_and_read_message(device, message):
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
        
        delaytime = device.long_timeout
        
        # Waiting a small amount of time might be necessary for the device to process the command and prepare a response
        time.sleep(delaytime)  # Adjust the sleep time as needed based on the device's datasheet or trial and error
        
        # Read the response from the device
        response = device.read()
        
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def extractPHNumber(response):
    # Use regular expression to find numbers in the response
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", response)
    # Assuming that the response always follows the same format (which it does), we want to find the second expression that matches the regular expression
    return matches[1] if matches else None

def generateGraph(device,numDataPoints):
    num_samp = 0
    x_values = []
    y_values = []
    while (num_samp < numDataPoints):
        response = float(send_and_read_message(device, "R"))
        pHValue = extractPHNumber(response)
        x_values.append(num_samp+1)
        y_values.append(pHValue)
        num_samp += 1
    
    plt.plot(x_values, y_values)
    
    plt.ylim(0, 10)
        
    plt.xlabel("number sample")
    plt.ylabel("pH Value")
    plt.title("pH Sampling Values")
        
    # showing plot
    plt.show()
    
    

if(__name__ == "__main__"):
    main()