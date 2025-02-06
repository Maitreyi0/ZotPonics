import queue
from datetime import datetime

class FileOutputManagementSystem:
    def __init__(self, fileName, includeTimeStamp):
        self.queue = queue.Queue()
        self.fileName = fileName
        self.includeTimeStamp = includeTimeStamp

    def addItem(self, item):
        """Add an item to the queue."""
        self.queue.put(item)

    def massWriteQueueToFile(self):
        """Write all items in the queue to a file with timestamps prepended."""
        with open(self.fileName, 'w') as file:  # Open file in write mode
            while not self.queue.empty():
                item = self.queue.get()
                if self.includeTimeStamp == True:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"{timestamp} - {item}\n")
                else:
                    file.write(f"{item}\n")

    # METHODS NOT IN USE
    # def getItem(self):
    #     """Get an item from the queue."""
    #     if not self.queue.empty():
    #         return self.queue.get()
    #     else:
    #         return None

    # def clearQueue(self):
    #     """Clear all items in the queue."""
    #     while not self.queue.empty():
    #         self.queue.get()

    # def getAllItems(self):
    #     """Get all items from the queue as a list (and clear the queue)."""
    #     items = []
    #     while not self.queue.empty():
    #         items.append(self.queue.get())
    #     return items

    # def isEmpty(self):
    #     """Check if the queue is empty."""
    #     return self.queue.empty()
    
if __name__ == "__main__":
    fileOutputManagementSystem = FileOutputManagementSystem(fileName="FileOutputManagementSystem.log", includeTimeStamp=False)
    fileOutputManagementSystem.addItem("Test Item 0")
    fileOutputManagementSystem.addItem("Test Item 1")
    fileOutputManagementSystem.massWriteQueueToFile()