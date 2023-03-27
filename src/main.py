import matplotlib.pyplot as plt
import json
import os
import math
import time
import signal

from util.timer import Timer
from plot import plot_results, LivePlotter
from positioncontroller import PositionController

CTRL_PARAMS = "config/ctrl_params.json"
#MOTOR_PARAMS = "config/motor_params.json"

WAYPOINTS_FILE = "config/waypoints.json"

# Entry point
if __name__ == "__main__":
    init_timer = Timer()
    print("Program Starting")

    #####################
    # Initialize Config #
    #####################

    # intializing signal interupt handler
    def signal_handler(*args):
        pc.vel_stop()
        plot_results(pc.time_array, pc.x_array, pc.y_array)

    signal.signal(signal.SIGINT, signal_handler)

    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname, "../")

    cp_path = os.path.join(dirname, CTRL_PARAMS)
    #mp_path = os.path.join(dirname, MOTOR_PARAMS)
    wp_path = os.path.join(dirname, WAYPOINTS_FILE)

    with open(cp_path) as cp_file:
        cp_json = json.loads(cp_file.read())
    #with open(mp_path) as mp_file:
    #    mp_json = json.loads(mp_file.read())
    with open(wp_path) as wp_file:
        waypoints = json.loads(wp_file.read())

    # Initialize Live Plot
    live_plt = LivePlotter()

    # Print initialization time
    print("Initialization completed in %1.2f seconds" %init_timer.elapsed())

    #################
    # Run Waypoints #
    #################

    # Initialize position controller with config params
    pc = PositionController(cp_json["vel"], cp_json["ang_vel"])

    # Iterate through each waypoint
    for wp in waypoints:
        print("Moving to waypoint ", wp)
        x_setpoint = wp["pos"][0]
        y_setpoint = wp["pos"][1]
        theta_setpoint = math.radians(wp["yaw"])
        pc.set_new_waypoint(x_setpoint, y_setpoint, theta_setpoint)
        
        timer = Timer()

        # Keep asking the position controller if we're there yet.
        while pc.dist_to_target() > 0.1:
            # Move it
            pc.update(timer.elapsed())
            timer.reset()

            # Update plot
            live_plt.update(pc.x_array, pc.y_array)

        # stop wheels after moving
        pc.vel_stop()

        # turn to target theta direction
        timer.reset()
        print("TURNING TO TH TARGET", pc.th_to_target() * 57.29, " degrees")

        while pc.th_outside_margin(0.05):
            pc.update_turning(timer.elapsed())
            timer.reset()

        print("WAYPOINT REACHED")

        # If there is a pause, wait for the specified period.
        if "pause" in wp:
            time.sleep(wp["pause"])
    
    ########
    # Plot #
    ########

    # Now that the journey is complete. Plot the odemetry velocities and positions.
    import numpy as np
    pos_x = [ 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 
         0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

    pos_y = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
         1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0 ]
    
    (plot_x, plot_y) = pc.return_plot()

    time_vector = np.arange(0, len(pos_x), 1)

    plot_results(time_vector, pos_x, pos_y)


    # Complete!
    print("Program finished successfully")
