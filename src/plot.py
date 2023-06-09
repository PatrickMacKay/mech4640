import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
import os

class plotter:
    def __init__(self):
        self.plotdir = self.create_plot_dir()

    def create_plot_dir(self):
        dirname = os.getcwd()
        dirname = os.path.join(dirname, "plots/")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname

    def list_print(self, s):
        print(" - ", s)

    # Plotting requires four vectors of the same length.
    def plot_results(
            self,
            time_vector,
            pos_x,
            pos_y,
            theta,
            x_setpoint,
            y_setpoint,
            l_vel,
            r_vel,
            set_l_vel,
            set_r_vel
        ):

        print("Plotting ", len(pos_x), "samples (%.2f seconds)" % time_vector[-1], " in directory ", self.plotdir)

        # x over time
        plt.figure()
        plt.plot(time_vector, pos_x, label = 'x')
        plt.title("x position vs time")
        plt.title("x position vs time")
        plt.xlabel("time (s)")
        plt.ylabel("x position (m)")
        plt.savefig(self.plotdir + "/x vs time.png")
        plt.show()
        self.list_print("x vs time")

        # y over time
        plt.figure()
        plt.plot(time_vector, pos_y, label = 'y')
        plt.title("y position vs time")
        plt.xlabel("time (s)")
        plt.ylabel("position (m)")
        plt.savefig(self.plotdir + "/y vs time.png")
        plt.show()
        self.list_print("y vs time")

        # theta over time
        plt.figure()
        plt.plot(time_vector, theta, label = 'theta')
        plt.title("theta vs time")
        plt.xlabel("time (s)")
        plt.ylabel("theta (rad)")
        plt.savefig(self.plotdir + "/theta vs time.png")
        plt.show()
        self.list_print("theta vs time")

        # velocity over time
        plt.figure()
        plt.plot(time_vector, l_vel, label = 'l_vel')
        plt.plot(time_vector, r_vel, label = 'r_vel')
        plt.legend()
        plt.title("velocity vs time")
        plt.xlabel("time (s)")
        plt.ylabel("velocity (m/s)")
        plt.savefig(self.plotdir + "/v vs time.png")
        plt.show()
        self.list_print("v vs time")

        # set velocity over time
        plt.figure()
        plt.plot(time_vector, set_l_vel, label = 'l_vel')
        plt.plot(time_vector, set_r_vel, label = 'r_vel')
        plt.legend()
        plt.title("set velocity vs time")
        plt.xlabel("time (s)")
        plt.ylabel("velocity (m/s)")
        plt.savefig(self.plotdir + "/set v over time.png")
        plt.show()
        self.list_print("set v vs time")

        # xy plot
        plt.figure()
        plt.plot(pos_x, pos_y, '*')
        plt.title("xy plot")
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.savefig(self.plotdir + "/xy plot.png")
        plt.show()
        self.list_print("xy plot")

        # setpoint plot
        plt.figure()
        plt.plot(time_vector, x_setpoint, label="x setpoint")
        plt.plot(time_vector, y_setpoint, label="y setpoint")
        plt.legend()
        plt.title("setpoint over time")
        plt.xlabel("time (s)")
        plt.ylabel("setpoint value (m)")
        plt.savefig(self.plotdir + "/setpoint plot.png")
        plt.show()
        self.list_print("setpoint vs time")

        # 3d plot (x, y, z=time)
        plt.figure()
        ax = plt.axes(projection = '3d')
        ax.plot3D(pos_x, pos_y, time_vector)
        ax.set_xlabel("x position (m)")
        ax.set_ylabel("y position (m)")
        ax.set_zlabel("time")
        plt.savefig(self.plotdir + "/3D plot.png")
        plt.show()
        self.list_print("3D plot (x, y, z=time)")