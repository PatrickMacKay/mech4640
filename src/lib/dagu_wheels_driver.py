#!/usr/bin/env python3

from math import fabs, floor

from lib import hat_driver
#import hat_driver #/include/hat_driver
from lib.dt_robot_utils import get_robot_configuration # DuckieTown-only code


MotorDirection = hat_driver.MotorDirection
#dagu_debug = False # Old debug variable

class DaguWheelsDriver:
    """Class handling communication with motors.
    """
    LEFT_MOTOR_MIN_PWM = 60  #: Minimum speed for left motor
    LEFT_MOTOR_MAX_PWM = 255  #: Maximum speed for left motor
    RIGHT_MOTOR_MIN_PWM = 60  #: Minimum speed for right motor
    RIGHT_MOTOR_MAX_PWM = 255  #: Maximum speed for right motor
    SPEED_TOLERANCE = 1.e-2  #: Speed tolerance level

    def __init__(self, debug=False):
        rcfg = get_robot_configuration() # DuckieTown-only code
        DTHAT = hat_driver.from_env()
        self.hat = DTHAT()
        self.leftMotor = self.hat.get_motor(1, "left")
        self.rightMotor = self.hat.get_motor(2, "right")
        ## These lines were to test if motor configurations 3 and 4 worked instead of 1 and 2.
        ## Further tests found that configs 1 and 2 work, but these are left in for future reference.
        # self.leftMotor = self.hat.get_motor(3, "left")
        # self.rightMotor = self.hat.get_motor(4, "right")
        # print out some stats
        this = self.__class__.__name__
        self.debug = debug
        if(self.debug):
            print(f"[{this}] Running in configuration `{rcfg.name}`, using driver `{DTHAT.__name__}`") # DuckieTown-only code
            print(f"[{this}] Motor #1: {self.leftMotor}")
            print(f"[{this}] Motor #2: {self.rightMotor}")

        # initialize state
        self.leftSpeed = 0.0
        self.rightSpeed = 0.0
        self._pwm_update()

    def set_wheels_speed(self, left: float, right: float):
        """Sets speed of motors.
        Args:
           left (:obj:`float`): speed for the left wheel, should be between -1 and 1
           right (:obj:`float`): speed for the right wheel, should be between -1 and 1
        """
        self.leftSpeed = left
        self.rightSpeed = right
        self._pwm_update()

    def _pwm_value(self, v, min_pwm, max_pwm):
        """Transforms the requested speed into an int8 number.
            Args:
                v (:obj:`float`): requested speed, should be between -1 and 1.
                min_pwm (:obj:`int8`): minimum speed as int8
                max_pwm (:obj:`int8`): maximum speed as int8
        """
        pwm = 0
        if fabs(v) > self.SPEED_TOLERANCE:
            pwm = int(floor(fabs(v) * (max_pwm - min_pwm) + min_pwm))
            if(self.debug):
                print("PWM:\t"+str(pwm)) # Print pwm on interval 0-255 (before pre-scale up by factor of 16 to 0-4095)
        return min(pwm, max_pwm)

    def _pwm_update(self):
        """Sends commands to the microcontroller.
            Updates the current PWM signals (left and right) according to the
            linear velocities of the motors. The requested speed gets
            tresholded.
        """
        vl = self.leftSpeed
        vr = self.rightSpeed

        pwml = self._pwm_value(vl, self.LEFT_MOTOR_MIN_PWM, self.LEFT_MOTOR_MAX_PWM)
        pwmr = self._pwm_value(vr, self.RIGHT_MOTOR_MIN_PWM, self.RIGHT_MOTOR_MAX_PWM)
        leftMotorMode = MotorDirection.RELEASE
        rightMotorMode = MotorDirection.RELEASE

        if fabs(vl) < self.SPEED_TOLERANCE:
            pwml = 0
        elif vl > 0:
            leftMotorMode = MotorDirection.FORWARD
        elif vl < 0:
            leftMotorMode = MotorDirection.BACKWARD

        if fabs(vr) < self.SPEED_TOLERANCE:
            pwmr = 0
        elif vr > 0:
            rightMotorMode = MotorDirection.FORWARD
        elif vr < 0:
            rightMotorMode = MotorDirection.BACKWARD

        self.leftMotor.set(leftMotorMode, pwml)
        self.rightMotor.set(rightMotorMode, pwmr)

    def __del__(self):
        """Destructor method.
            Releases the motors and deletes tho object.
        """
        self.leftMotor.set(MotorDirection.RELEASE)
        self.rightMotor.set(MotorDirection.RELEASE)
        del self.hat