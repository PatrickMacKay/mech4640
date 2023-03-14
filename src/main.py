import json
import os

from util.timer import Timer

CTRL_PARAMS = "config/ctrl_params.json"
WAYPOINTS_FILE = "config/waypoints.json"

# Entry point
if __name__ == "__main__":
    init_timer = Timer()
    print("Program Starting")

    # Import controller config
    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname, "../")

    cp_path = os.path.join(dirname, CTRL_PARAMS)
    wp_path = os.path.join(dirname, WAYPOINTS_FILE)
    
    print(dirname)
    
    # Print initialization time
    print("Initialization completed in %1.2f seconds" %init_timer.elapsed())