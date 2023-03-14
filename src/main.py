from util.timer import Timer
import json


# Entry point
if __name__ == "__main__":
    init_timer = Timer()
    print("Program Starting")
    # Import controller config
    
    # Print initialization time
    print("Initialization completed in %1.2f seconds" %init_timer.elapsed())