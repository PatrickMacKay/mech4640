import picamera
from datetime import datetime
import time
camera = picamera.PiCamera()
camera.resolution = (2592,1944)
camera.annotate_background = picamera.Color('black')

for c in range(0,25):
    countDown = 3
    camera.start_preview()
    input("press enter to continue")
    camera.annotate_test = ""
    camera.capture("CalibrationPicyure{0:02d}.jpg".format(c))
camera.stop_preview()
camera.close()