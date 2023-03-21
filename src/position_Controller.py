import numpy as np
from util.timer import Timer
from motorDriver import velocityController
from util.PIDController import PIDController

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class PoistionController:
    wheel_base_width = 0.095

    def __init__(self, p = 1, i = 1, d = 1, xtarget = 0, ytarget = 0, thtarget = 0):
        self.p = p
        self.i = i
        self.d = d

        self.k_omega = 80

        self.vel_limit = 0.1 # m/s
        self.angvel_limit = 20 # m/s
        self.xtarget = xtarget
        self.ytarget = ytarget
        self.thtarget = thtarget

        # initialize velocity controller
        self.vc = velocityController()

        # set PID values
        self.PIDvel = PIDController(p, i, d, 1)
        self.PIDth = PIDController(p, i, d, 1)
        self.PIDvel.setpoint = np.sqrt(np.square(self.xtarget)+np.square(self.ytarget))
        self.PIDth.setpoint = self.ytarget

        self.v_R = 0
        self.v_L = 0
        self.ang_vel = 0
        self.xmeasure = 0
        self.ymeasure = 0
        self.thmeasure = 0
        self.x_array = []
        self.y_array = []
        self.th_array = []

    def update_pose(self, dt):
        # get updates from velocity controller
        l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc = self.vc.update()
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


    def update_vel(self, dt):
        # based on current and target position, update velocity
        #self.PIDx.state = self.xmeasure
        #self.PIDy.state = self.ymeasure
        vel = np.sqrt(np.square(self.xtarget-self.xmeasure)+np.square(self.ytarget-self.ymeasure))
        #vel = max(vel, self.vel_limit)
        vel = clamp(vel, 0, self.vel_limit)
        th_to_target = np.arctan2(self.ytarget - self.ymeasure, self.xtarget - self.xmeasure)
        # print("th measured", self.thmeasure)
        ang_vel = self.k_omega * self.angdiff(th_to_target, self.thmeasure)
        ang_vel = clamp(ang_vel, 0, self.angvel_limit)
        print("angular vel ", ang_vel)

        self.ang_vel = ang_vel

        # calculate R & L wheel velocities based
        v_R = vel + ang_vel * self.wheel_base_width / 2
        v_L = vel - ang_vel * self.wheel_base_width / 2

        #print("Velocities: ", v_L, ", ", v_R)
        self.v_L = v_L
        self.v_R = v_R

        self.vc.moveVel(v_L, v_R)

    def update(self, dt):
        self.update_pose(dt)
        self.update_vel(dt)
    
    def dist_to_target(self):
        return np.sqrt((self.xtarget - self.xmeasure)**2 + (self.ytarget - self.ymeasure)**2)
    
    def dist_to_target_x(self):
        return (self.xtarget - self.xmeasure)
    
    def dist_to_target_y(self):
        return (self.ytarget - self.ymeasure)
    
    def return_plot(self):
        return self.xmeasure, self.ymeasure

    def angdiff(self, th1, th2):
        # taking the difference
        diff = th1 - th2

        # checking if result is greater than 360 and reducing to within 1 rotation
        if abs(diff) > 360:
            r = diff // 360
            diff = diff - r * 360

        # if difference is negative, change to postive rotation to make next step easier
        if diff < 0:
            diff = 360 + diff

        # checking if answer is within range pi or -pi
        if 0 < diff < 180:
            pass
        elif 180 < diff < 360:
            diff = -(360-diff)

        # transform to radians for answer
        diff_rad = diff * np.pi/180

        return diff_rad
