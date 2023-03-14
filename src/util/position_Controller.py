import numpy as np
from timer import timer #needs to be adjusted for whatever james filename is


class PoistionController:
    def __init__(self, p = 1, i = 1, d = 1, xtarget = 0, ytarget = y):
        self.p = p
        self.i = i
        self.d = d

        self.xtarget = xtarget
        self.ytarget = ytarget

        self.xmeasure = 0
        self.ymeasure = 0





