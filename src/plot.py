import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
import os

class LivePlotter:

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.plot = self.ax.scatter([], [])
        plt.draw()

    def update(self, x_pos, y_pos):
        self.plot = self.ax.scatter(x_pos, y_pos)
        self.fig.canvas.draw()
        plt.pause(0.05)

class plotter:
    def __init__(self):
        self.plotdir = self.create_plot_dir()

    def create_plot_dir(self):
        dirname = os.getcwd(__file__)
        dirname = os.path.join(dirname, "util/plots/")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname


    # Plotting requires three vectors of the same length.
    def plot_results(self, time_vec, x_pos, y_pos):
        # Plot some stuff
        print("Plotting results")
        self.finished_plots(time_vec, x_pos, y_pos)

    def finished_plots(self, time_vector, pos_x, pos_y):

        print("Plotting {} samples", len(pos_x))

        velocities = np.ones(len(pos_x)) 
        for i in range(0, len(velocities)):
            velocities[i] = velocities[i] + np.random.normal(-0.1, 0.1)

        # x over time
        # fig1 = plt.figure()
        plt.plot(time_vector, pos_x, label = 'x')
        plt.plot(time_vector, pos_x, label = 'x')
        plt.title("x position vs time")
        plt.xlabel("time")
        plt.ylabel("x position")
        plt.savefig(self.plotdir + "/x vs time.png")
        plt.show()

        # y over time
        fig2 = plt.figure()
        plt.plot(time_vector, pos_y, label = 'y')
        plt.plot(time_vector, pos_y, label = 'y')
        plt.title("y position vs time")
        plt.xlabel("time")
        plt.ylabel("position")
        plt.savefig(self.plotdir + "/y vs time.png")
        plt.show()


        # velocity over time
        fig3 = plt.figure()
        plt.plot(time_vector, velocities, label = 'velocities')
        plt.plot(time_vector, velocities, label = 'velocities')
        plt.title("velocity vs time")
        plt.xlabel("time")
        plt.ylabel("velocity")
        plt.savefig(self.plotdir + "/v vs time.png")
        plt.show()

        fig = plt.figure()
        ax = plt.axes(projection = '3d')
        ax.plot3D(pos_x, pos_y, time_vector)
        ax.set_xlabel("x position")
        ax.set_ylabel("y position")
        ax.set_zlabel("time")
        plt.savefig(self.plotdir + "/3D plot.png")
        plt.show()