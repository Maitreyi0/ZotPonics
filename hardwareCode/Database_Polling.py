from MenuManagementSystem import MenuManagementSystem
from MYSQL import (retrieve_most_recent_command, retrieve_most_recent_arguments, retrieve_most_recent_func)
import threading
import time

class DatabasePolling:
    def __init__(self, menu_system=None):
        if menu_system is None:
            print("menu system is not passed in")
            menu_system = MenuManagementSystem()
        self.menu = menu_system
        self.running = False
        self.thread = None
    def request(self):
        command = retrieve_most_recent_command()
        arguments = retrieve_most_recent_arguments()

        self.menu.start_processing()

        if len(arguments) == 1:
            self.menu.enqueue_command(command, arguments[0])
            print("Arguments: 1")
        elif len(arguments) == 2:
            self.menu.enqueue_command(command, arguments[0], arguments[1])
            print("Arguments: 2")
        elif len(arguments) == 3:
            self.menu.enqueue_command(command, arguments[0], arguments[1], arguments[2])
            print("Arguments: 3")
        else:
            self.menu.enqueue_command(command)
            print("Arguments: 0")



        #print("Registered commands:", self.menu.options)

    def poll_requests(self):
        while self.running:
            self.request()
            time.sleep(5)

    def start_polling(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.poll_requests, daemon=True)
            self.thread.start()
            print("DatabasePolling started.")

    def stop_polling(self):
        self.running = False
        self.thread.join()
        print("DatabasePolling stopped.")


