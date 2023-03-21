import sys
import os
sys.path.insert(0,os.getcwd())
sys.path.append('../lib')
from dagu_wheels_driver import DaguWheelsDriver
import pigpio

# This object uses the dagu_wheel_controller module to move the motors of the duckiebot's servo.

class VelocityController:
    pi = pigpio.pi()
    left_encoder_pin = 18
    right_encoder_pin = 19

    wheels = DaguWheelsDriver()
