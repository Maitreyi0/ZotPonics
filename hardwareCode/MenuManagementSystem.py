import threading
from queue import Queue
import MenuManagementSystemTestCases

import inspect

class MenuManagementSystem:
    def __init__(self, max_queue_size=5):
        """
        Initializes the MenuManagementSystem with a maximum queue size.
        :param max_queue_size: Maximum number of commands allowed in the queue.
        """
        self.options = {}  # Dictionary to store command options and metadata
        self.command_queue = Queue(maxsize=max_queue_size)
        self.global_lock = threading.Lock()
        self.command_event = threading.Event()
        self.processing_thread = None
        self.running = False

    def add_option(self, key, func):
        """
        Adds a command to the options dictionary, along with its argument details.
        :param key: String key for the option.
        :param func: Function to be called when the key is entered.
        """
        if not callable(func):
            raise ValueError("The value must be a callable (function).")
        
        # Retrieve argument names and count using inspect.signature
        signature = inspect.signature(func)
        parameters = signature.parameters
        
        arg_names = [name for name in parameters]
        num_args = len(parameters)
        
        # Store all information in the options dictionary under the command key
        self.options[key] = {
            'func': func,
            'arg_names': arg_names,
            'num_args': num_args
        }

    def enqueue_command(self, user_input, *args):
        """
        Adds a user input command to the queue for processing.
        :param user_input: String input to add to the queue.
        :param args: Positional arguments for the function.
        """
        if user_input not in self.options:
            print("Invalid command.")
            return
        
        option = self.options[user_input]

        # Validate argument count
        required_num_args = option['num_args']
        required_arg_names = option['arg_names']

        if len(args) != required_num_args:
            print(f"Error: Command '{user_input}' requires {required_num_args} arguments ({', '.join(required_arg_names)}).")
            return
        
        # Create a command dictionary with the input and args
        command_event = threading.Event()
        command = {
            'input': user_input,
            'args': args,
            'event': command_event,
        }

        if not self.command_queue.full():
            self.command_queue.put(command)
            if args:
                print(f"Command '{user_input}' enqueued with arguments {args}.")
            else:
                print(f"Command '{user_input}' enqueued, does not require arguments")
        else:
            print("Command queue is full. Please wait.")

        self.command_event.clear()
        self.process_queue()
        command_event.wait()

    def process_queue(self):
        """
        Processes a single command in the queue.
        """
        if not self.command_queue.empty():
            command = self.command_queue.get()

            user_input = command['input']
            args = command['args']
            command_event = command['event']

            if user_input in self.options:
                option = self.options[user_input]
                func = option['func']

                try:
                    with self.global_lock:
                        func(*args)
                except Exception as e:
                    print(f"Error executing '{user_input}': {e}")

            command_event.set()
            self.command_event.set()

    def start_processing(self):
        """
        Starts the command processing in a separate thread.
        """
        self.running = True
        self.processing_thread = threading.Thread(target=self._run, daemon=True)
        self.processing_thread.start()

    def _run(self):
        """
        Internal method to run the queue processing at intervals.
        """
        while self.running:
            if not self.command_queue.empty():
                self.process_queue()
            else:
                threading.Event().wait(0.1)

    def stop_processing(self):
        """
        Stops the command processing thread.
        """
        self.running = False
        if self.processing_thread is not None:
            self.processing_thread.join()
            print("Command processing thread has stopped.")
            
    def mass_add_options_to_menu_management_system(self, alias, list_of_methods_to_add_as_options ):
      """
      :param list_of_methods_to_add_as_options: This should be a list of function signatures
      """
      for method_to_add_as_option in list_of_methods_to_add_as_options:
         
         option_name = f"[{alias}]-{method_to_add_as_option.__name__}"
         option_target_function = method_to_add_as_option
         
         self.add_option(option_name, option_target_function)

if __name__ == "__main__":
    MenuManagementSystemTestCases.multi_thread_test_case()