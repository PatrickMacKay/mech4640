import sys # Setting up PATH, will move to Path.py
import os
sys.path.insert(0,os.getcwd())  #sys.path.insert(0,'/home/pi/Documents/Code') # Explicit
sys.path.append('../lib') 	# This allows the system path to look in the 'libraries' directory co-located with this script.
from dagu_wheels_driver import DaguWheelsDriver  # Need path in order to call dagu_wheels_driver
import time
import math as m
import numpy as np
#pigpio handles counting the encoder turns
#You =must= use "sudo pigpiod" in terminal before running this code to start the pigio daemon
import pigpio

################################################
#This code was updated 24th March, 2022

#Changelog:
#Adjusted max/min intergral stored.
#Drop stored integral when speed = 0 
################################################

class velocityController:
    # Relate pigpio interface to pi
    __pi = pigpio.pi()
    __left_encoder_pin = 18       # Left Encoder GPIO pin
    __right_encoder_pin = 19      # Right Encoder GPIO pin
    __wheels = DaguWheelsDriver() # Contains the functions for wheel commands
    wheel_radius = 0.0318       # Wheel radius (m)
    ticksPerRevolution = 2*135  # 2* from EITHER_EDGE of ticks
    distPerTick = m.pi*2*wheel_radius/ticksPerRevolution #Distance Per Tick (m)

    # Set default variables
    leftSig = 0             #left control signal  (-1 to 1)
    rightSig = 0            #right control signal (-1 to 1)
    leftTVel = 0            #left target velocity 
    rightTVel = 0           #right target velocity 
    defaultSampleCheck = 5  #Default number of previous points are considered when calculating velocity
    sampleCheck = 5         #Current number of previous points considered when calculating velocity
    storeSize = 10          #Number of previous point stored. Must be one larger than any sampleCheck
    store_l = np.zeros((2, storeSize)) #storage matrix for time and encoder values for left side.
    store_r = np.zeros((2, storeSize)) #storage matrix for time and encoder values for right side
    __sign_l = 1            #Used to keep track of sign (-/+) of current and previous target velocities
    __sign_r = 1            #Used to keep track of sign (-/+) of current and previous target velocities
    startTime = 0           #Start time intialized with 
    __prev_L_err = 0
    __prev_R_err = 0
    integ_l = 0
    integ_r = 0

    #PID values
    __P = 1.8   #Proportional 
    __I = 1.0    #Integral
    __D = 0.4    #Derivative

    #Initializes the class
    def __init__(self):
        #Set the start time
        self.startTime=time.time()
        for i in range(0,self.storeSize):
            self.store_l[0,i] = self.startTime - i*0.1
            self.store_r[0,i] = self.startTime - i*0.1
        
        #Check if correct pins used, and setup the callback function using the pigpio demon for monitoring
        if self.__left_encoder_pin != 18 or self.__right_encoder_pin != 19:
            print("Output pins may be incorrect.")
        self.cb_left = self.__pi.callback(self.__left_encoder_pin, pigpio.EITHER_EDGE)
        self.cb_right = self.__pi.callback(self.__right_encoder_pin, pigpio.EITHER_EDGE)

    #printMotor() - this function prints the PWM signal and TargetVel signal currently being used.
    def returnSigTarVel(self):
        return self.leftSig, self.rightSig, self.leftTVel, self.rightTVel

    #returnTally - returns the current tally from the encoders
    def returnTally(self):
        return self.cb_left.tally(), self.cb_right.tally()

    #dumpStorage - clears old encoders values of the left encoder from storage by assigning the most 
    #              recent values to all. Used when motors shift direction.
    def dumpLStorage(self):
        for i in range(1, self.storeSize):
            self.store_l[1, i] = self.store_l[1, 0]-i*0.1
        self.leftSig = 0
        self.integ_l = 0

    #dumpRStorage - clears old encoder values of the right encoder from storage by assigning the most 
    #               recent values to all.
    def dumpRStorage(self):
        for i in range(1, self.storeSize):
            self.store_r[1, i] = self.store_r[1, 0]-i*0.1
        self.rightSig = 0
        self.integ_r = 0

    #update() - updates the motor PWM signal for current iteration. Velocity will not update without this function
    def update(self):

        #Check to see if target velocity differs in sign from previous target velocity.
        if m.copysign(1,self.leftTVel) != self.__sign_l and self.leftTVel != 0:
            self.dumpLStorage()
            self.__sign_l = -1 * self.__sign_l
        if m.copysign(1,self.rightTVel) != self.__sign_r and self.rightTVel != 0:
            self.dumpRStorage()
            self.__sign_r = -1 * self.__sign_r

        #Shift elements of array one
        for i in range(self.storeSize - 1, 0, -1):
            self.store_l[0, i] = self.store_l[0, i - 1]
            self.store_l[1, i] = self.store_l[1, i - 1]
            self.store_r[0, i] = self.store_r[0, i - 1]
            self.store_r[1, i] = self.store_r[1, i - 1]

        #Record measurements of encoders at current time
        self.store_l[0, 0] = time.time()
        self.store_l[1, 0] = self.cb_left.tally()
        self.store_r[0, 0] = time.time()
        self.store_r[1, 0] = self.cb_right.tally()

        #Calculate the current velocity based on average of last samplecheck-1 velocities.
        vel_l= 0
        vel_r = 0
        for i in range(0,self.sampleCheck-1):
            vel_l = vel_l + self.distPerTick*(self.store_l[1, i] - self.store_l[1, i + 1]) / (self.store_l[0, i] - self.store_l[0, i + 1])
            vel_r = vel_r + self.distPerTick*(self.store_r[1, i] - self.store_r[1, i + 1]) / (self.store_r[0, i] - self.store_r[0, i + 1])
        vel_l = vel_l / self.sampleCheck
        vel_r = vel_r / self.sampleCheck

        #Calculate error
        err_l = self.leftTVel - self.__sign_l * vel_l
        err_r = self.rightTVel - self.__sign_r * vel_r

        #I goes here (not implmented)
        self.integ_l = max(min(0.5, self.integ_l + 0.75*(err_l+self.__prev_L_err)*(self.store_l[0,0]-self.store_l[0,self.sampleCheck-1])),-0.75)
        self.integ_r = max(min(0.5, self.integ_r + 0.75*(err_r+self.__prev_R_err)*(self.store_r[0,0]-self.store_r[0,self.sampleCheck-1])),-0.75)
        
        #D goes here (not implmented)
        deriv_l = (err_l - self.__prev_L_err) / (self.store_l[0,0]-self.store_l[0,self.sampleCheck-1])
        deriv_r = (err_r - self.__prev_R_err) / (self.store_r[0,0]-self.store_r[0,self.sampleCheck-1])

        self.__prev_R_err = err_r
        self.__prev_L_err = err_l

        #Calculate signals for motor control
        self.leftSig = max(min(0.5*self.__sign_l+0.5, self.__P * err_l + self.__I * self.integ_l + self.__D * deriv_l), 0.5*self.__sign_l-0.5)
        self.rightSig = max(min(0.5*self.__sign_r+0.5, self.__P * err_r + self.__I * self.integ_r + self.__D * deriv_r), 0.5*self.__sign_r-0.5)
        if(self.leftTVel==0):
            self.leftSig=0
            self.integ_l=0
        if(self.rightTVel==0):
            self.rightSig=0
            self.integ_r=0
        return self.leftSig, self.rightSig, self.store_l[0, 0]-self.store_l[0,1], self.store_r[0, 0]-self.store_r[0,1], self.__sign_l * vel_l, self.__sign_r * vel_r, self.store_l[1, 0], self.store_r[1, 0]

    #setVel - sets target velocity of motor based on last 5 recorded samples (see setVelRate)
    def setTarVel(self, targetVelLeft, targetVelRight):
        self.setTarVelCheck(targetVelLeft, targetVelRight, self.defaultSampleCheck)

    #setVelCheck - sets target velocity of motor based on defined sample check
    def setTarVelCheck(self, targetVelLeft, targetVelRight, sampleCheck):
        self.sampleCheck = int(sampleCheck)
        self.rightTVel = targetVelRight
        self.leftTVel = targetVelLeft

    #move - sets target velocity and updates signal for default sample check
    def moveVel(self, targetVelLeft, targetVelRight):
        return self.moveVelCheck(targetVelLeft, targetVelRight, self.defaultSampleCheck)

    #moveCheck() - sets target velocity and updates signal for defined sample check
    def moveVelCheck(self, targetVelLeft, targetVelRight, sampleCheck):
        self.setTarVelCheck(targetVelLeft, targetVelRight, sampleCheck)
        l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc = self.update()
        self.movePWM(l_sig, r_sig)
        return l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc
    
    #movePWM() - moves duckieBot according to PWM signal.
    def movePWM(self, leftSig, rightSig):
        self.__wheels.set_wheels_speed(leftSig, rightSig)

    #setAngVel - sets angular velocity of motor based on default sample check.
    def setAngVel(self, angVLeft, angVRight):
        return self.setTarVel(angVLeft*self.wheel_radius, angVRight*self.wheel_radius)

    #Resets the stored integral.
    def resetI(self):
        self.integ_l=0
        self.integ_r=0

    



