import matplotlib.pyplot as plt
import json
import os
import math
import time
import signal

from util.timer import Timer
from plot import plotter
from positioncontroller import PositionController
from .cam_capture import CameraTime

CTRL_PARAMS = "config/ctrl_params.json"
WAYPOINTS_FILE = "config/waypoints.json"

# Entry point
if __name__ == "__main__":
    init_timer = Timer()
    print("Program Starting")

    #####################
    # Initialize Config #
    #####################

    # Initialize plotter and signal handler
    plot = plotter()
    def plot_results():
        pc.vel_stop()
        plot.plot_results(
            pc.time_array,
            pc.x_array,
            pc.y_array,
            pc.th_array,
            pc.x_setpoint_array,
            pc.y_setpoint_array,
            pc.v_l_array,
            pc.v_r_array,
            pc.set_v_l_array,
            pc.set_v_r_array
        )
        print("COMPLETE")
        exit(0)
    #initialize the camera 
    cam = CameraTime()

    def signal_handler(*args):
        print("\nSIGINT Interrupt. Stopping robot\n")
        plot_results()
        
    signal.signal(signal.SIGINT, signal_handler)

    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname, "../")

    cp_path = os.path.join(dirname, CTRL_PARAMS)
    wp_path = os.path.join(dirname, WAYPOINTS_FILE)

    with open(cp_path) as cp_file:
        cp_json = json.loads(cp_file.read())
    with open(wp_path) as wp_file:
        waypoints = json.loads(wp_file.read())

    timer = Timer()

    # Initialize position controller with config params
    pc = PositionController(cp_json["vel"], cp_json["ang_vel_forward"], cp_json["ang_vel_turning"])

    # Print initialization time
    print("Initialization completed in %1.2f seconds" %init_timer.elapsed())

    #################
    # Run Waypoints #
    #################

    # Iterate through each waypoint
    for wp in waypoints:
        print("\nMOVING TO WAYPOINT ", wp)
        x_setpoint = wp["pos"][0]
        y_setpoint = wp["pos"][1]
        theta_setpoint = math.radians(wp["yaw"])
        pc.set_new_waypoint(x_setpoint, y_setpoint, theta_setpoint)

        #capture image
        cam.capture_image()

        # Keep asking the position controller if we're there yet.
        timer.reset()
        while pc.dist_to_target() > 0.02:
            # Move it
            pc.update(timer.elapsed())
            timer.reset()
            time.sleep(0.025)

        # stop wheels after moving
        pc.vel_stop()
        #capture image
        cam.capture_image()

        # turn to target theta direction
        print("\nTURNING TO TH TARGET (theta = %.2f" %theta_setpoint, " rads)")

        timer.reset()
        while pc.th_outside_margin(0.1):
            pc.update_turning(timer.elapsed())
            timer.reset()
            time.sleep(0.025)

        print("\nWAYPOINT REACHED")
        pc.vel_stop()

        # If there is a pause, wait for the specified period.
        if "pause" in wp:
            time.sleep(wp["pause"])
    
    ########
    # Plot #
    ########

    # Now that the journey is complete. Plot the odemetry velocities and positions.
    print("\n Waypoints complete. Stopping robot\n")
    plot_results()

    # Complete!
    print("Program finished successfully")
