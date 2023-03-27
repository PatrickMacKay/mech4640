import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d

class LivePlotter:
    fig, ax = plt.subplots()
    plot = ax.scatter([], [])

    def update(self, time_vec, x_pos, y_pos):
        self.plot.set_offsets(x_pos, y_pos)
        self.fig.canvas.draw()
        plt.pause(0.05)



# Plotting requires three vectors of the same length.
def plot_results(time_vec, x_pos, y_pos):
    # Plot some stuff
    print("Plotting results")
    finished_plots(time_vec, x_pos, y_pos)

def finished_plots(time_vector, pos_x, pos_y):

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
    plt.show()

    # y over time
    fig2 = plt.figure()
    plt.plot(time_vector, pos_y, label = 'y')
    plt.plot(time_vector, pos_y, label = 'y')
    plt.title("y position vs time")
    plt.xlabel("time")
    plt.ylabel("position")
    plt.show()


    # velocity over time
    fig3 = plt.figure()
    plt.plot(time_vector, velocities, label = 'velocities')
    plt.plot(time_vector, velocities, label = 'velocities')
    plt.title("velocity vs time")
    plt.xlabel("time")
    plt.ylabel("velocity")
    plt.show()

    fig = plt.figure()
    ax = plt.axes(projection = '3d')
    ax.plot3D(pos_x, pos_y, time_vector)
    ax.set_xlabel("x position")
    ax.set_ylabel("y position")
    ax.set_zlabel("time")
    plt.show()