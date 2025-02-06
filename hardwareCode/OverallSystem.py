import threading
import queue
import time
import GPIO_Utility
import RPi.GPIO as GPIO
from pH_AndEC_Subsystem import pH_AndEC_Subsystem
from AtlasI2C_SensorAndPumps import AtlasI2C_SensorAndPumps
from MenuManagementSystem import MenuManagementSystem
from MenuManagementSystemTestCases import greet_user, add_numbers
from ConsoleProgram import ConsoleProgram
from Status import Status
from hardwareCode.PeristalticPump import PeristalticPump
from AtlasI2C_Sensor import AtlasI2C_Sensor
from FileOutputManagementSystem import FileOutputManagementSystem

def find_all_status_objects_with_alias(obj, recurse_classes, visited=None):
   """
   Recursively find all sub-objects of type Status within an object and retrieve their alias values.
   Only recurses into objects that are instances of the specified classes.

   :param obj: The object to search within.
   :param recurse_classes: A list or tuple of classes that are allowed for recursion.
   :param visited: A set to track visited objects and avoid infinite recursion.
   :return: A dictionary where the keys are Status objects and the values are their corresponding alias values.
   """
   if visited is None:
      visited = set()

   # Avoid revisiting objects
   if id(obj) in visited or obj is None:
      return {}
   visited.add(id(obj))

   found_dict = {}

   # If the object is a Status object, add it to the results
   if isinstance(obj, Status):
      try:
         alias_value = obj.getStatusFieldTupleValue("alias")
      except AttributeError:
         alias_value = None
      found_dict[obj] = alias_value
      return found_dict  # No need to recurse further into a Status object
   elif isinstance(obj, recurse_classes): # Only recurse into objects of allowed classes
      if hasattr(obj, '__dict__'):  # Objects with __dict__ contain attributes
         for attr_name, attr_value in vars(obj).items():
               if attr_value is None:  # Skip None values
                  print(f"Skipping None attribute: {attr_name}")
                  continue

               if not attr_name.startswith('__'):  # Skip magic methods/attributes
                  # Debug message for current recursion
                  print(f"Recursing into object: {obj}")
                  print("Located attribute: " + attr_name)
                  found_dict.update(find_all_status_objects_with_alias(attr_value, recurse_classes, visited))
   # Handle lists, tuples, and sets
   elif isinstance(obj, (list, tuple, set)):
      for item in obj:
         # Recursively process each element in the collection
         found_dict.update(find_all_status_objects_with_alias(item, recurse_classes, visited))

   return found_dict

class OverallSystem:
   """
   This class will bring everything together
   
   Current Components Supported:
   - User Interface Components:
      - console
   - Hydroponics System Components:
      - pH subsystem
   """
   def __init__(self, phAndEC_Subsystem=None, menuManagementSystem=None, phSubsystem=None, ecSubsystem=None, consoleProgram=None):
      
      self.status = Status(topLevel=True, debugModeOn=False)
      self.status.addStatusFieldTuple("alias", "overallSystem")
      self.status.addStatusFieldTuple("phSubsystem", phSubsystem.status)
      
      # store menu management system object
      self.menuManagementSystem = menuManagementSystem
      # won't always have a console program but will store if it does have
      self.consoleProgram = consoleProgram
      
      # pH and EC subsystems
      self.phAndEC_Subsystem = phAndEC_Subsystem # overall subsystem
      self.phSubsystem = phSubsystem # pH subsystem
      self.ecSubsystem = ecSubsystem # EC subsystem
      
      # status objects
      self.statusObjectsDict = find_all_status_objects_with_alias(self, (OverallSystem, AtlasI2C_Sensor, PeristalticPump, AtlasI2C_SensorAndPumps)) # this will keep track of all the status objects for easier accessing
      
   def get_status_string_by_alias(self, alias):
    """
    Finds the Status object in the dictionary corresponding to the given alias.

    :param found_dict: A dictionary where keys are Status objects and values are their aliases.
    :param alias: The alias value to search for.
    :return: The Status object corresponding to the given alias.
    :raises ValueError: If no Status object is found with the given alias.
    """
    for status_obj, alias_value in self.statusObjectsDict.items():
        if alias_value == alias:
            status_obj.updateStatusDict()
            status_obj.updateStatusString(True)
            return status_obj.statusString
    raise ValueError(f"No Status object found with alias '{alias}'.")
      
   def print_status_string_by_alias(self, alias):
      print(self.get_status_string_by_alias(alias))
      
   def print_dict_keys(self):
      """
      Prints all the keys of a dictionary.

      :param dictionary: The dictionary whose keys are to be printed.
      """
      if not isinstance(self.statusObjectsDict, dict):
         print("Provided input is not a dictionary.")
         return

      print("Values in the dictionary:")
      for value in self.statusObjectsDict.values():
         print(value)
      

if __name__ == "__main__":
   
   # Set mode of GPIO
   GPIO_Utility.setModeBCM()
   
   # pump variables for reference
   pH_UpPin = 22
   pH_DownPin = 23
   baseA_Pin = 20
   baseB_Pin = 21
   
   # INITIALIZATION OF PH SUBSYSTEM
   phPumpsList = []
   phPumpsList.append(PeristalticPump(pH_DownPin, "phDown", False, False))
   phPumpsList.append(PeristalticPump(pH_UpPin, "phUp", False, False))
   
   phFileOutputManagementSystem = FileOutputManagementSystem(fileName="AtlasI2C_SensorAndPumps.log", includeTimeStamp=True)
   
   phSensor = AtlasI2C_Sensor(AtlasI2C_Sensor.PH_SENSOR_KEY_WORD, debugMode=True, contPollThreadIndependent=False, isOutermostEntity=False, generateMatPlotLibImages=True, alias="phSensor", fileOutputManagementSystem=phFileOutputManagementSystem)
   
   phSubsystem = AtlasI2C_SensorAndPumps(alias="phSubsystem", sensor=phSensor, pumpsList=phPumpsList, debugMode=True, isOutermostEntity=True)
   
   
   # INITIALIZATION OF MENU
   # Create an instance of MenuManagementSystem with a 2-second processing interval
   menu_system = MenuManagementSystem()
   # Add options to the menu system
   
   # INITIALIZATION OF CONSOLE PROGRAM
   consoleProgram = ConsoleProgram(menu_system)
   
   # INITIALIZATION OF OVERALL SYSTEM
   overallSystem = OverallSystem(menuManagementSystem=menu_system, consoleProgram=consoleProgram, phSubsystem=phSubsystem)
   
   # overallSystem.status.updateStatusDict()
   # overallSystem.status.updateStatusString(True)
   overallSystem.phSubsystem.status.updateStatusDict()
   overallSystem.phSubsystem.status.updateStatusString(True)
   
   overallSystem.menuManagementSystem.add_option("add numbers", add_numbers)
   overallSystem.menuManagementSystem.add_option("greet person", greet_user)
   overallSystem.menuManagementSystem.add_option("get status", overallSystem.print_status_string_by_alias)
   overallSystem.menuManagementSystem.add_option("print status aliases", overallSystem.print_dict_keys)

   # Start the menu system's queue processing in a separate thread
   menu_system.start_processing()
   
   # Start the console program to send commands to menu system
   consoleProgram.start()
   
   consoleProgram.wait_until_exit()

   print("Console program has fully exited, but menu processing continues.")
   menu_system.stop_processing()
   print("Menu processing has stopped.")
   
   
   