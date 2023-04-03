import picamera
import os
from datetime import datetime
import time


class CameraTime:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (2592, 1944)
        self.camera.annotate_background = picamera.Color('black')

    def capture_image(self):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{current_time}.jpg"
        directory = "pictures"

        if not os.path.exists(directory):
            os.makedirs(directory)

        self.camera.start_preview()
<<<<<<< HEAD
        self.camera.annotate_text = ""
=======
        self.camera.annotate_text = datetime.now().strftime(" %a, %d, %b, %Y, %H:%M:%S.%f")
>>>>>>> 8f7684f5b4674468addfc300b2c2194641a70b4a
        self.camera.capture(os.path.join(directory, filename))
        self.camera.stop_preview()
        print(f"Picture saved as {filename} in directory {directory}")

    def __del__(self):
        self.camera.close()

if __name__ == "__main__":
<<<<<<< HEAD
    camera = Camera()
=======
    camera = CameraTime()
>>>>>>> 8f7684f5b4674468addfc300b2c2194641a70b4a
    camera.capture_image()
