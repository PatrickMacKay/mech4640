import numpy as np
import timer


class PoistionController:
    def __init__(self, p = 1, i = 1, d = 1, xtarget = 0, ytarget = 0):
        self.p = p
        self.i = i
        self.d = d

        self.xtarget = xtarget
        self.ytarget = ytarget

        self.xmeasure = 0
        self.ymeasure = 0
        self.x_array = []
        self.y_array = []

    def update_pose(self):
        # add current calculation to array for plotting
        self.x_array.append(self.xmeasure)
        self.y_array.append(self.ymeasure)
        # calculate position delta based on encoder values
        x_delta
        y_delta
        #update measured position
        self.xmeasure = self.xmeasure + x_delta
        self.ymeasure = self.ymeasure + y_delta






