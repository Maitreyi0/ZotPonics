import matplotlib.pyplot as plt
import os

class PlotImagesManager:
    def __init__(self, directory: str):
        """
        Initializes the PHPlotManager with a directory for saving images.

        Args:
        directory (str): The directory where images will be saved.
        """
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)  # create the directory if it doesn't exist, if it does exist, do nothing
        self.currentIndex = self.getLatestIndex()

    def getLatestIndex(self):
        """
        Gets the index of the latest image in the directory, based on modification time.

        Returns:
        int: The current image index (0-99).
        """
        existingFiles = [f for f in os.listdir(self.directory) 
                         if f.startswith("image") and f.endswith(".png")]

        if not existingFiles:
            return 0

        # Sort files by modification time
        existingFiles.sort(key=lambda f: os.path.getmtime(os.path.join(self.directory, f)))

        latestFile = existingFiles[-1]  # Get the most recently modified file
        latestIndex = int(latestFile.replace('image', '').replace('.png', ''))
        return (latestIndex + 1) % 100

    def plotAndSave(self, PH_Values):
        """
        Plots pH values and saves the image to the directory, replacing old images if needed.

        Args:
        PH_Values (list): A list of pH values to plot.
        """
        # Ensure the index is between 0 and 99
        self.currentIndex = self.currentIndex % 100

        # Define the filename
        filename = f"image{self.currentIndex}.png"
        savePath = os.path.join(self.directory, filename)

        # Plot the pH values
        xRange = list(range(min(len(PH_Values), 100)))
        plt.figure(figsize=(10, 6))
        plt.plot(xRange, PH_Values[:100], marker='o', linestyle='-', label='pH Values')
        plt.xlabel('Sample (i-th)')
        plt.ylabel('pH Level')
        plt.title('pH Values over Samples')
        plt.xlim(0, 99)
        plt.ylim(0, 14)
        plt.grid(True)
        plt.legend(loc='upper right')

        # Save the plot
        plt.tight_layout()
        plt.savefig(savePath)
        plt.close()

        print(f"Plot saved as {filename} in {self.directory}")

        # Update the current index
        self.currentIndex = (self.currentIndex + 1) % 100

    # this method is key for integrating with the back end
    # The back
    def getLatestImagePath(self):
        """
        Returns the filepath of the most recent image.

        Returns:
        str: The filepath of the most recent image.
        """
        latestIndex = (self.currentIndex - 1) % 100
        filename = f"image{latestIndex}.png"
        return os.path.join(self.directory, filename)

if __name__ == "__main__":
    # Example usage
    phManager = PlotImagesManager('ph_images')
    phValues = [7.0, 6.8, 7.2, 7.4, 6.9, 7.1] + [7.0] * 94

    # # Save new pH plots and manage the image directory
    # for _ in range(105):  # Create more than 100 plots to test replacement
    #     phManager.plotAndSave(phValues)

    # Get the most recent image
    latestImage = phManager.getLatestImagePath()
    print(f"Most recent image: {latestImage}")