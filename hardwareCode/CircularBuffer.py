import threading

# exception classes
# NOTE: This exception class is no longer needed so commented out
# class MostRecentAlreadyAccessedException(Exception):
#     """
#     Thrown by get_unique_latest_values
#     This exception is thrown when trying to access a latest value that has already been accessed
#     """
#     pass

class EmptyBufferException(Exception):
    """
    This exception is thrown when trying to access values of an empty buffer
    """
    pass
    
# Overview:
# - This class will be used to store the readings of sensors
# - We use a circular buffer data structure in order to put a limit on the amount of RAM taken up by the sensor readings (we don't want the amount of data to grow infinitely)
class CircularBuffer:
    def __init__(self, size):
        self.size = size # maximum number of elements that can exist in the CB
        self.buffer = [None] * size # the array that stores the elements
        
        # this will always point to the index that is next to be inserted into (does not point to the latest element)
        # NOTE: The latest value is always in the index one before the value of index (don't just decrement, have to map via modulo before we arrive at the actual index)
        self.currentIndex = 0
        self.currentSize = 0 # initially 0 since no elements
        
        # flag used to determine whether the most recent value has been accessed yet or not
        self.mostRecentValueAccessed = True # this is set to True initially to account for how program was written. This has to be true in order for the cont poll thread to get the very first value

    def add(self, value):
        self.buffer[self.currentIndex] = value # insert value into the CB
        self.currentIndex = (self.currentIndex + 1) % self.size # calculate the next index
        
        # the most recent value is new so reset the mostRecentValueAccessed flag
        # if already false, no need to reset the flag
        if(self.mostRecentValueAccessed == True):
            self.mostRecentValueAccessed = False
            
        # also update the latest value attribute
        
        # only increase the value of currentSize when less than the maximum size, once it is the maximum size, it doesn't become any bigger
        if(self.currentSize < self.size):
            self.currentSize = self.currentSize + 1

    def getCB_Values(self):
        """
        This will return the elements of the CB in order. Make sure the thread is locked before using this method. We thread lock to avoid tampering while we access the CB.
        """
        values = [None] * self.currentSize
        valuesIndex = self.currentSize - 1
        CB_Index = (self.currentIndex - 1) % self.size # here, CB_Index will initially point to the latest element
        for i in range(0, self.currentSize):
            values[valuesIndex] = self.buffer[CB_Index]
            
            valuesIndex = valuesIndex - 1 # update value of valuesIndex
            CB_Index = (CB_Index - 1) % self.size # update value of CB_Index
        
        return values
    
    def get_latest_value(self, bypassAccessedFlag):
        """
        Gets the latest value in the buffer
        
        bypassAccessedFlag is used in order to avoid raising the mostRecentValueAccessed flag (kind of like accessing the latest value via a backdoor). This is done in order to avoid affecting the functionality of the conditional thread
        
        Raises:
            EmptyBufferException: Thrown when buffer is empty
        """
        # NOTE: if we have self.index = -1 and we do % self.size, 
        # it will give us the very last index
        if self.currentSize > 0:
            latestValue = self.buffer[(self.currentIndex - 1) % self.size]
            if(self.mostRecentValueAccessed == False and bypassAccessedFlag == False):
                self.mostRecentValueAccessed = True # just tells whether it has been accessed already
            return latestValue
        else:
            raise EmptyBufferException # if currentSize = 0, means that there is no value in the buffer and therefore no latest value

if __name__ == "__main__":
    circularBuffer = CircularBuffer(50)
    for i in range(0, 10):
        print("adding " + str(i) + " to the buffer")
        circularBuffer.add(i)
    values = circularBuffer.getCB_Values()
    print(str(values))