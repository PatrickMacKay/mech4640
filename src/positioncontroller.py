import numpy as np
from util.timer import Timer
from motorDriver import velocityController
from util.PIDController import PIDController

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class PositionController:
    wheel_base_width = 0.095
    motor_updates_per_cycle = 10
    update_counter = 0
    sampleCheck = 5

    def __init__(self, vel_params, ang_vel_params):

        # Initialize PID Controllers with parameters (p, i, d, lim)
        self.vel_pid = PIDController(
            vel_params["p_gain"],
            vel_params["i_gain"],
            vel_params["d_gain"],
            vel_params["limit"]
        )
        self.vel_pid.setpoint = 0
        self.angvel_pid = PIDController(
            ang_vel_params["p_gain"],
            ang_vel_params["i_gain"],
            ang_vel_params["d_gain"],
            ang_vel_params["limit"]
        )
        self.angvel_pid.setpoint = 0

        # Initialize velocity controller
        self.vc = velocityController()

        # Wheel Velocities
        self.v_R = 0
        self.v_L = 0

        # Current position measurement
        self.xmeasure = 0
        self.ymeasure = 0
        self.thmeasure = 0

        # Cumulative values
        self.elapsed_time = 0
        self.time_array = []
        self.x_array = []
        self.y_array = []
        self.th_array = []
        self.x_setpoint_array = []
        self.y_setpoint_array = []
        self.v_l_array = []
        self.v_r_array = []
        self.set_v_l_array = []
        self.set_v_r_array = []

    def set_new_waypoint(self, xtarget = 0, ytarget = 0, thtarget = 0):
        self.xtarget = xtarget
        self.ytarget = ytarget
        self.thtarget = thtarget

    def update_pose(self, dt):
        # Update velocity controller
        l_sig, r_sig, l_time, r_time, l_vel, r_vel, l_enc, r_enc = self.vc.update()

        # Add to cumulative arrays
        self.elapsed_time += dt
        self.time_array.append(self.elapsed_time)
        self.x_array.append(self.xmeasure)
        self.y_array.append(self.ymeasure)
        self.th_array.append(self.thmeasure)
        self.x_setpoint_array.append(self.xtarget)
        self.y_setpoint_array.append(self.ytarget)
        self.v_l_array.append(l_vel)
        self.v_r_array.append(r_vel)
        self.set_v_l_array.append(self.v_L)
        self.set_v_r_array.append(self.v_R)

        # Calculate position delta based on encoder values
        th_delta = (r_vel - l_vel) / self.wheel_base_width * dt
        self.thmeasure = self.thmeasure + th_delta
        self.thmeasure = self.normalize_theta(self.thmeasure)

        x_delta = 0.5*(r_vel + l_vel) * np.cos(self.thmeasure) * dt
        y_delta = 0.5*(r_vel + l_vel) * np.sin(self.thmeasure) * dt

        # Update current measured positions
        self.xmeasure = self.xmeasure + x_delta
        self.ymeasure = self.ymeasure + y_delta

        print("    Current pose: x = %.3f" %self.xmeasure, " y = %.3f" %self.ymeasure, " th = %.2f" %self.thmeasure, end="\r")


    def update_vel(self, dt):

        # Calculate error for vel and angvel and set as setpoint.
        # Update PID controllers with measurements
        self.vel_pid.state = np.sqrt(np.square(self.xtarget-self.xmeasure)+np.square(self.ytarget-self.ymeasure))

        ang_diff = np.arctan2(self.ytarget - self.ymeasure, self.xtarget - self.xmeasure) - self.thmeasure
        self.angvel_pid.state = self.normalize_theta(ang_diff)

        self.vel_pid.update(dt)
        self.angvel_pid.update(dt)

        vel = self.vel_pid.output
        ang_vel = self.angvel_pid.output

        # Assign velocities with direction of angvel
        v_R = vel + (ang_vel * self.wheel_base_width / 2)
        v_L = vel - (ang_vel * self.wheel_base_width / 2)

        # Do not write unless the velocities are different
        #if self.v_L != v_L or self.v_R != v_R:
        #    self.vc.moveVelCheck(v_L, v_R, self.sampleCheck)
        #    self.v_L = v_L
        #    self.v_R = v_R
        self.vc.moveVelCheck(v_L, v_R, self.sampleCheck)

    def update(self, dt):
        self.update_pose(dt)
        self.update_counter += 1

        if self.update_counter >= self.motor_updates_per_cycle:
            self.update_counter = 0
            self.update_vel(dt)
    
    def update_turning(self, dt):
        self.update_pose(dt)
        self.update_counter += 1

        if self.update_counter >= self.motor_updates_per_cycle:
            self.update_counter = 0
            self.turn_to_th_target(dt)

    def turn_to_th_target(self, dt):
        # Update PID controller
        self.angvel_pid.state = self.th_to_target()
        self.angvel_pid.update(dt)
        ang_vel = self.angvel_pid.output

        # calculate R & L wheel velocities based
        v_R = (ang_vel * self.wheel_base_width / 2)
        v_L = -(ang_vel * self.wheel_base_width / 2)

        self.vc.moveVelCheck(v_L, v_R, self.sampleCheck)
    
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
        diff = self.thtarget - self.thmeasure
        return self.normalize_theta(diff)
    
    def th_outside_margin(self, margin):
        diff = self.th_to_target()
        return diff > margin or diff < -margin

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
