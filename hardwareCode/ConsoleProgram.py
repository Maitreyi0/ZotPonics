import threading
import time
from MenuManagementSystem import MenuManagementSystem

class ConsoleProgram:
    def __init__(self, menu_system):
        """
        Initializes the ConsoleProgram with an existing MenuManagementSystem object.
        :param menu_system: An instance of MenuManagementSystem.
        """
        self.menu_system = menu_system
        self.running = False
        self.thread = None

    def add_option(self, key, func):
        """
        Adds a key-value pair to the menu system's options dictionary.
        """
        self.menu_system.add_option(key, func)

    def terminate_console_program(self):
        """
        Terminates the console interaction thread without affecting the menu processing thread.
        """
        print("Terminating console interaction thread...")
        self.running = False

    def user_interact(self):
        """
        Runs the user interaction loop that waits for user input
        and enqueues commands for processing.
        """
        self.running = True
        print("Console Program started. Type the corresponding number to select an option.")

        while self.running:
            self.print_numbered_menu()

            try:
                user_input = input("Enter command number: ").strip()

                if not user_input.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue

                command_number = int(user_input)

                if command_number == len(self.menu_system.options) + 1:  # Terminate console program option
                    self.terminate_console_program()
                    break
                elif 1 <= command_number <= len(self.menu_system.options):
                    # Get the option key for the selected command
                    option_key = list(self.menu_system.options.keys())[command_number - 1]
                    option = self.menu_system.options[option_key]

                    # Get argument names for the selected command
                    arg_names = option['arg_names']
                    num_args = option['num_args']

                    # If arguments are required, prompt the user for them
                    args = []
                    if num_args > 0:
                        print(f"Command '{option_key}' requires {num_args} arguments: {', '.join(arg_names)}")
                        print("Type 'return' at any time to go back to the main menu.")
                        for arg_name in arg_names:
                            arg_value = input(f"Enter value for '{arg_name}': ").strip()
                            if arg_value.lower() == "return":
                                print("Returning to main menu...")
                                break
                            args.append(arg_value)

                        # If the user typed 'return', skip command execution
                        if len(args) < num_args:
                            continue

                    # Enqueue the command with the collected arguments
                    self.menu_system.enqueue_command(option_key, *args)

                else:
                    print("Invalid number. Please try again.")

            except (KeyboardInterrupt, EOFError):
                print("\nExiting due to interruption.")
                self.terminate_console_program()
                break

    def print_numbered_menu(self):
        """
        Prints the menu options with numbers.
        """
        print("\nAvailable Commands:")
        for i, key in enumerate(self.menu_system.options, start=1):
            print(f" {i}. {key}")
        print(f" {len(self.menu_system.options) + 1}. terminate console program")

    def start(self):
        """
        Starts the user interaction loop in a separate thread.
        """
        self.thread = threading.Thread(target=self.user_interact, daemon=True)
        self.thread.start()

    def wait_until_exit(self):
        """
        Waits until the console interaction thread exits.
        """
        if self.thread is not None:
            self.thread.join()
        
# Define some example functions (not part of class)
def hello():
    print("Hello, world!")

def greet_user():
    name = input("Enter your name: ")
    print(f"Hello, {name}!")

def current_time():
    print(f"Current time: {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    menu_system = MenuManagementSystem()
    # Add options to the menu system
    menu_system.add_option("hello", hello)
    menu_system.add_option("greet", greet_user)
    menu_system.add_option("time", current_time)
    # Start the menu system's queue processing in a separate thread
    menu_system.start_processing()
    # Create an instance of ConsoleProgram using the existing MenuManagementSystem
    program = ConsoleProgram(menu_system)
    # Start the console program in a separate thread
    program.start()
    # Wait until the console interaction exits
    program.wait_until_exit()

    print("Console program has fully exited, but menu processing continues.")

    # We stop the menu system thread separately afterwards because the menu management does not control this thread, the overall system will control this thread
    menu_system.stop_processing()
    print("Menu processing has stopped.")