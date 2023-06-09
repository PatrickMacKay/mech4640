from util.timer import Timer

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

# This class manages a PID controller using a 
class PIDController:

    # Proportional gain
    p_gain = 0

    # Integral gain
    i_gain = 0

    # Derivative gain
    d_gain = 0

    # Maximum output of controller
    limit = 1

    # Real-time values
    setpoint = 0
    state = 0
    prevErr = 0
    output = 0

    # Constructor accepts controller gains and a limit.
    def __init__(self, p, i, d, limit):
        self.p_gain = p
        self.i_gain = i
        self.d_gain = d
        self.limit = limit
    
    def update(self, dt):

        # Calculate error
        err = self.state - self.setpoint

        P = self.p_gain * err
        I = self.i_gain * err * dt
        D = self.d_gain * (err - self.prevErr) / dt

        self.output = clamp(P + I + D, -self.limit, self.limit)
        self.prevErr = err


        
