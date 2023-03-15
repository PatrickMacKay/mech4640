import numpy as np
import timer
from mech4640.src.motorDriver import velocityController
from motorDriver import velocityController

vc = velocityController()

class PoistionController:
    wheel_base_width = 0.095
    ticksPerRevolution = vc.ticksPerRevolution
    distPerTick = vc.distPerTick

    def __init__(self, p = 1, i = 1, d = 1, xtarget = 0, ytarget = 0, thtarget = 0):
        self.p = p
        self.i = i
        self.d = d

        self.xtarget = xtarget
        self.ytarget = ytarget
        self.thtarget = thtarget

        self.xmeasure = 0
        self.ymeasure = 0
        self.thmeasure = 0
        self.x_array = []
        self.y_array = []
        self.th_array = []

    def update_pose(self, dt):
        # get updates from velocity controller
        l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc = vc.update()
        # add current calculation to array for plotting
        self.x_array.append(self.xmeasure)
        self.y_array.append(self.ymeasure)
        self.th_array.append(self.thmeasure)
        # calculate position delta based on encoder values
        th_delta = (r_vel - l_vel) / self.wheel_base_width * dt
        x_delta = 0.5*(r_vel + l_vel) * np.cos(self.thmeasure) * dt
        y_delta = 0.5*(r_vel + l_vel) * np.sin(self.thmeasure) * dt
        #update measured position
        self.thmeasure = self.thmeasure + th_delta
        self.xmeasure = self.xmeasure + x_delta
        self.ymeasure = self.ymeasure + y_delta


    def update_vel(self):
        # based on current and target position, update velocity
        


