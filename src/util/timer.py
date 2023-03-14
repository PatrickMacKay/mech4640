import time

# This is a timer class that reduces code complexity when writing timers.
class Timer:
    init_time = time.time()

    def elapsed(self):
        return time.time() - self.init_time

    def reset(self):
        self.init_time = time.time()