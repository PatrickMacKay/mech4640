import numpy as np
from util.timer import Timer
from motorDriver import velocityController
from util.PIDController import PIDController

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class PoistionController:
    wheel_base_width = 0.095

    def __init__(self, p = 1, i = 1, d = 1):
        self.p = p
        self.i = i
        self.d = d

        self.k_omega = 0.3
        self.k_vel = 0.1

        self.vel_limit = 0.2 # m/s
        self.angvel_limit = 0.1 # rad/s

        # initialize velocity controller
        self.vc = velocityController()

        self.v_R = 0
        self.v_L = 0
        self.xmeasure = 0
        self.ymeasure = 0
        self.thmeasure = 0

        self.time_array = []
        self.x_array = []
        self.y_array = []
        self.th_array = []

    def set_new_waypoint(self, xtarget = 0, ytarget = 0, thtarget = 0):
        self.xtarget = xtarget
        self.ytarget = ytarget
        self.thtarget = thtarget

    def update_pose(self, dt):
        # get updates from velocity controller
        l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc = self.vc.update()
        # add current calculation to array for plotting
        self.time_array.append(self.dt + self.time_array[-1]) # -1 returns the last element
        self.x_array.append(self.xmeasure)
        self.y_array.append(self.ymeasure)
        self.th_array.append(self.thmeasure)
        # calculate position delta based on encoder values
        th_delta = (r_vel - l_vel) / self.wheel_base_width * dt
        x_delta = 0.5*(r_vel + l_vel) * np.cos(self.thmeasure) * dt
        y_delta = 0.5*(r_vel + l_vel) * np.sin(self.thmeasure) * dt
        #update measured position
        self.thmeasure = self.thmeasure + th_delta
        self.thmeasure = self.normalize_theta(self.thmeasure)
        self.xmeasure = self.xmeasure + x_delta
        self.ymeasure = self.ymeasure + y_delta


    def update_vel(self, dt):
        # based on current and target position, update velocity
        vel = self.k_vel * np.sqrt(np.square(self.xtarget-self.xmeasure)+np.square(self.ytarget-self.ymeasure))
        vel = clamp(vel, 0, self.vel_limit)
        th_to_xytarget = np.arctan2(self.ytarget - self.ymeasure, self.xtarget - self.xmeasure)

        # print("th measured", self.thmeasure)
        ang_vel = self.k_omega * self.angdiff(th_to_xytarget, self.thmeasure)
        ang_vel = clamp(ang_vel, -self.angvel_limit, self.angvel_limit)
        print("angular vel ", ang_vel)
        # print("linear vel: ", vel)

        # calculate R & L wheel velocities based
        v_R = vel + (ang_vel * self.wheel_base_width / 2)
        v_L = vel - (ang_vel * self.wheel_base_width / 2)

        #print("Velocities: ", v_L, ", ", v_R)
        self.v_L = v_L
        self.v_R = v_R

        self.vc.moveVel(v_L, v_R)

    def update(self, dt):
        self.update_pose(dt)
        self.update_vel(dt)
    
    def update_turning(self, dt):
        self.update_pose(dt)
        self.turn_to_th_target(dt)

    def turn_to_th_target(self, dt):
        # print("th measured", self.thmeasure)
        ang_vel = self.k_omega * self.th_to_target()
        ang_vel = clamp(ang_vel, -self.angvel_limit, self.angvel_limit)
        print("angular vel ", ang_vel)
        # print("linear vel: ", vel)

        # calculate R & L wheel velocities based
        v_R = (ang_vel * self.wheel_base_width / 2)
        v_L = -(ang_vel * self.wheel_base_width / 2)

        self.vc.moveVel(v_L, v_R)
    
    def vel_stop(self):
        self.vc.moveVel(0, 0)

    def dist_to_target(self):
        return np.sqrt((self.xtarget - self.xmeasure)**2 + (self.ytarget - self.ymeasure)**2)
    
    def dist_to_target_x(self):
        return (self.xtarget - self.xmeasure)
    
    def dist_to_target_y(self):
        return (self.ytarget - self.ymeasure)
    
    def return_plot(self):
        return self.xmeasure, self.ymeasure
    
    def th_to_target(self):
        return self.angdiff(self.thtarget, self.thmeasure)

    # not sure this is actually needed
    def normalize_theta(self, theta):
        while theta > np.pi:
            theta -= 2*np.pi
        while theta < -np.pi:
            theta += 2*np.pi
        return theta


    def angdiff(self, th1, th2):
        # changing input values to degrees
        th1 = np.degrees(th1)
        th2 = np.degrees(th2)
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
        diff_rad = np.radians(diff)

        return diff_rad
