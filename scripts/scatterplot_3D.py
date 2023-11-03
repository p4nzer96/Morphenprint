import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import traceback
import numpy as np


def get_x_y_coordinates(directory_path):
    X = []
    Y = []
    Z = []
    with open(directory_path,"rt") as txtfile:
        output = txtfile.read()
    lines = output.split('\n')
    lines = [line for line in lines if line.strip() != '']
    for index, line in enumerate(lines):
        try:
            if len(line) > 0 and line[0] == '{':
                X_F1_matching_score = float(line[line.find("Morph_Img1_score=") + len("Morph_Img1_score=") : line.find(", Morph_Img2_score=")])
                Y_F2_matching_score = float(line[line.find("Morph_Img2_score=") + len("Morph_Img2_score=") : line.find(", Morph_Img3_score=")])
                Z_F3_matching_score = float(line[line.find("Morph_Img3_score=") + len("Morph_Img3_score=") : line.find("}")])

                if (X_F1_matching_score and Y_F2_matching_score and Z_F3_matching_score):
                    X.append(X_F1_matching_score)
                    Y.append(Y_F2_matching_score)    
                    Z.append(Z_F3_matching_score)             
                    print('Line -', index)
                else: 
                    continue

                
        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()
            continue
    
    return X, Y, Z

# def on_move(event, fig, ax):
#     ax.view_init(elev=ax.elev, azim=ax.azim)
#     fig.canvas.draw_idle()
#     print(f"Elevation: {ax.elev}, Azimuth: {ax.azim}")

def main():
    directory_path = sys.argv[1]
    x, y, z = get_x_y_coordinates(directory_path)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create the orange scatter plot and include a label
    ax.scatter(x, y, z, color='orange', marker='o', s=10)

    above_36_points = []
    below_36_points = []

    for i in range(len(x)):
        if x[i] > 36 and y[i] > 36 and z[i] > 36:
            if x[i] > 60 and y[i] > 60 and z[i] > 60:
                above_36_points.append(ax.scatter(x[i], y[i], z[i], color='green', marker='D', s=60)) 
                
            elif x[i] > 48 and y[i] > 48 and z[i] > 48:
                above_36_points.append(ax.scatter(x[i], y[i], z[i], color='green', marker='s', s=40)) 
                
            else:
                above_36_points.append(ax.scatter(x[i], y[i], z[i], color='green', marker='o', s=20)) 

        if x[i] < 36 and y[i] < 36 and z[i] < 36:
            below_36_points.append(ax.scatter(x[i], y[i], z[i], color='red', marker='o', s=15)) 

    # Determine the x, y, and z axis limits
    x_min, x_max = 0, 140
    y_min, y_max = 0, 140
    z_min, z_max = 0, 140

    # Specify the interval (10 units in this case)
    interval = 20

    # Calculate the minimum and maximum tick values based on the interval and data range
    x_tick_min = (x_min // interval) * interval
    x_tick_max = ((x_max // interval) + 1) * interval
    y_tick_min = (y_min // interval) * interval
    y_tick_max = ((y_max // interval) + 1) * interval
    z_tick_min = (z_min // interval) * interval
    z_tick_max = ((z_max // interval) + 1) * interval

    # Create custom tick values for the x, y, and z axes
    x_ticks = np.arange(x_tick_min, x_tick_max + interval, interval)
    y_ticks = np.arange(y_tick_min, y_tick_max + interval, interval)
    z_ticks = np.arange(z_tick_min, z_tick_max + interval, interval)

    # Set the custom tick values for each axis
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_zticks(z_ticks)

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='z', labelsize=12)

    # Adding labels and title
    ax.set_xlabel('$F_1$ Matching Score', fontsize=14)
    ax.set_ylabel('$F_2$ Matching Score', fontsize=14)
    ax.set_zlabel('$F_3$ Matching Score', fontsize=14)

    ax.view_init(azim=45, elev=45)

    # Create a custom legend with labels
    custom_legend = [
        ax.scatter([], [], color='green', marker='D', s=10, label='Triple-Identity FPs > DT3'),
        ax.scatter([], [], color='green', marker='s', s=10, label='DT3 > Triple-Identity FPs > DT2'),
        ax.scatter([], [], color='green', marker='o', s=10, label='DT2 > Triple-Identity FPs > DT1'),
        ax.scatter([], [], color='red', marker='o', s=10, label='Virtual-Identity FPs'),
        ax.scatter([], [], color='orange', marker='o', s=10, label='Partial-Identity FPs')
    ]
    
    # Add the custom legend to the plot
    ax.legend(handles=custom_legend, fontsize=13)


    ax.view_init(29, 237)
    # Display the plot
    # Connect the motion_notify_event to the mouse motion function
    #fig.canvas.mpl_connect('motion_notify_event', lambda event: on_move(event, fig, ax))
    plt.show()

if __name__ == '__main__':
    main()