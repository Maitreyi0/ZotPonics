import subprocess
import datetime
import os
from Status import Status

class PiCamera:
    
    class FieldKeys(Status.FieldKeys):
        NotImplemented
    
    def __init__(self, output_directory="captured_images", width=640, height=480, quality=50):
        """
        Initialize the camera with optimized settings for faster capture.
        """
        self.output_directory = output_directory
        self.width = width
        self.height = height
        self.quality = quality
        os.makedirs(self.output_directory, exist_ok=True)

    def capture_image(self, filename=None):
        """
        Captures an image with reduced quality for faster processing.
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"image_{timestamp}.jpg"

        image_path = os.path.join(self.output_directory, filename)

        try:
            subprocess.run([
                "libcamera-jpeg",
                "-o", image_path,
                "--width", str(self.width),
                "--height", str(self.height),
                "--quality", str(self.quality),
                "--shutter", "5000",
                "--denoise", "off",
                "--nopreview",
                "--sharpness", "0"
            ], check=True)

            print(f"Fast image captured: {image_path}")
            return image_path
        except subprocess.CalledProcessError as e:
            print(f"Error capturing image: {e}")
            return None

# Example usage
if __name__ == "__main__":
    piCamera = PiCamera()
    piCamera.capture_image("test.jpg")  # Capture an image quickly