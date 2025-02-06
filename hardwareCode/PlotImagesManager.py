import matplotlib.pyplot as plt
import os

class PlotImagesManager:
    def __init__(self, directory: str, maxSize: int = 100):
        """
        Initializes the PlotImagesManager with a directory for saving images
        and sets the maximum list size for plotting.

        Args:
        directory (str): The directory where images will be saved.
        max_size (int): Maximum number of pH values to plot. Default is 100.
        """
        self.directory = directory
        self.maxSize = maxSize
        os.makedirs(self.directory, exist_ok=True)  # create the directory if it doesn't exist
        self.currentIndex = self.getLatestIndex()
        self.valuesListsList = []  # Lists of values will be stored in here

    def getLatestIndex(self):
        """
        Gets the index of the latest image in the directory, based on modification time.

        Returns:
        int: The current image index (0-max_size-1).
        """
        existingFiles = [f for f in os.listdir(self.directory) 
                         if f.startswith("image") and f.endswith(".png")]

        if not existingFiles:
            return 0

        # Sort files by modification time
        existingFiles.sort(key=lambda f: os.path.getmtime(os.path.join(self.directory, f)))

        latestFile = existingFiles[-1]  # Get the most recently modified file
        latestIndex = int(latestFile.replace('image', '').replace('.png', ''))
        return (latestIndex + 1) % self.maxSize

    def saveListOfVals(self, listOfVals
                 ):
        """
        Saves a list of values to the list of lists.

        Args:
        listOfVals (list): The list that we want to save
        """
        if len(listOfVals) > self.maxSize:
            listOfVals = listOfVals[:self.maxSize]  # Truncate if longer than max_size
        self.valuesListsList.append(listOfVals)

    def generateAllPlots(self):
        """
        Generates and saves plots for all saved pH value lists, starting after
        the most recently saved image in the directory.
        """
        # Start plotting from the current index determined by the most recent image
        start_index = self.currentIndex

        for index, listOfVals in enumerate(self.valuesListsList):
            # Define the filename for each plot
            filename = f"image{(start_index + index) % self.maxSize}.png"
            savePath = os.path.join(self.directory, filename)

            # Plot the pH values
            xRange = list(range(len(listOfVals)))
            plt.figure(figsize=(10, 6))
            plt.plot(xRange, listOfVals, marker='o', linestyle='-', label='pH Values')
            plt.xlabel('Sample (i-th)')
            plt.ylabel('pH Level')
            plt.title('pH Values over Samples')
            plt.xlim(0, self.maxSize - 1)
            plt.ylim(0, 14)
            plt.grid(True)
            plt.legend(loc='upper right')

            # Save the plot
            plt.tight_layout()
            plt.savefig(savePath)
            plt.close()

            print(f"Plot saved as {filename} in {self.directory}")

        # Update the current index after generating all plots
        self.currentIndex = (start_index + len(self.valuesListsList)) % self.maxSize

if __name__ == "__main__":
    # Example usage
    max_size = 250  # Set the desired maximum size for plotting
    phManager = PlotImagesManager('phPlotImages', maxSize=max_size)

    # Add some sample lists of pH values
    phManager.saveListOfVals([7.0, 6.8, 7.2, 7.4, 6.9, 7.1] + [7.0] * (max_size - 6))
    phManager.saveListOfVals([6.5, 6.7, 7.3, 7.2, 6.8, 7.4] + [7.1] * (max_size - 6))
    phManager.saveListOfVals([7.2] * max_size)

    # Mass-generate all plots at once
    phManager.generateAllPlots()