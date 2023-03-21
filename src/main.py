import json
import os
import math
import time

from util.timer import Timer
from plot import plot_results
from position_Controller import PoistionController

CTRL_PARAMS = "config/ctrl_params.json"
#MOTOR_PARAMS = "config/motor_params.json"

#WAYPOINTS_FILE = "config/waypoints.json"
WAYPOINTS_FILE = "config/one_waypoint.json"

# Entry point
if __name__ == "__main__":
    init_timer = Timer()
    print("Program Starting")

    #####################
    # Initialize Config #
    #####################

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

    # Initialize position controller

    # Print initialization time
    print("Initialization completed in %1.2f seconds" %init_timer.elapsed())

    #################
    # Run Waypoints #
    #################

    for wp in waypoints:
        x_setpoint = wp["pos"][0]
        y_setpoint = wp["pos"][1]
        theta_setpoint = math.radians(wp["yaw"])

        # Keep asking the position controller if we're there yet.
        pc = PoistionController(
            1, # p,
            1, # i,
            1, # d
            x_setpoint,
            y_setpoint,
            theta_setpoint
        )

        timer = Timer()

        while pc.dist_to_target() > 0.1:
            # Move it
            pc.update(timer.elapsed())
            print("Current position: ", pc.xmeasure, ", ", pc.ymeasure)
            timer.reset()
            time.sleep(0.2)

        # If there is a pause, wait for the specified period.
        if "pause" in wp:
            time.sleep(wp["pause"])
        # Iterate through all waypoints
    
    ########
    # Plot #
    ########

    # Now that the journey is complete. Plot the odemetry velocities and positions.
    import numpy as np
    pos_x = [ 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 
         0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

    pos_y = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
         1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0 ]

    time_vector = np.arange(0, len(pos_x), 1)

    plot_results(time_vector, pos_x, pos_y)


    # Complete!
    print("Program finished successfully")
