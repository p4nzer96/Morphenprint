import matplotlib.pyplot as plt
import sys
import traceback
import numpy as np
from matplotlib.lines import Line2D


def get_x_y_coordinates(directory_path):
    X = []
    Y = []
    with open(directory_path,"rt") as txtfile:
        output = txtfile.read()
    lines = output.split('\n')
    lines = [line for line in lines if line.strip() != '']
    for index, line in enumerate(lines):
        try:
            if len(line) > 0 and line[0] == '{':
                X_F1_matching_score = float(line[line.find("Morph_Img1_score=") + len("Morph_Img1_score=") : line.find(", Morph_Img2_score=")])
                Y_F2_matching_score = float(line[line.find("Morph_Img2_score=") + len("Morph_Img2_score=") : line.find("}")])

                if (X_F1_matching_score and Y_F2_matching_score):
                    X.append(X_F1_matching_score)
                    Y.append(Y_F2_matching_score)                
                    print('Line -', index)
                else: 
                    continue

                
        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()
            continue
    
    return X, Y


def main():
    directory_path = sys.argv[1]
    x, y = get_x_y_coordinates(directory_path)
    x_double_identity = []
    y_double_identity = []
    x_virtual_identity = []
    y_virtual_identity = []

    # Create a scatterplot
    plt.scatter(x, y, color='orange', marker='o', s=10)

    for i in range(len(x)):
        if x[i] > 36 and y[i] > 36:
            x_double_identity.append(x[i])
            y_double_identity.append(y[i])
        if x[i] < 36 and y[i] < 36:
            x_virtual_identity.append(x[i])
            y_virtual_identity.append(y[i])
    
    plt.scatter(x_double_identity, y_double_identity, color='green', marker='o', s=10)
    plt.scatter(x_virtual_identity, y_virtual_identity, color='red', marker='o', s=10)

    # Draw vertical line at x = 36, 48, 60
    plt.axvline(x=36, color='#a1045a', linestyle='--')
    plt.axvline(x=48, color='#710193', linestyle='--')
    plt.axvline(x=60, color='#311432', linestyle='--')

    # Draw horizontal line at y = 36, 48, 60
    plt.axhline(y=36, color='#a1045a', linestyle='--')
    plt.axhline(y=48, color='#710193', linestyle='--')
    plt.axhline(y=60, color='#311432', linestyle='--')

    # Create a custom legend with only one entry for each label
    custom_legend = [
        plt.Line2D([0], [0], marker='o', color='w', label='Double-Identity FPs', markersize=5, markerfacecolor='green'),
        plt.Line2D([0], [0], marker='o', color='w', label='Virtual-Identity FPs', markersize=5, markerfacecolor='red'),
        plt.Line2D([0], [0], marker='o', color='w', label='Partial-Identity FPs', markersize=5, markerfacecolor='orange'),
        Line2D([0], [0], color='#a1045a', linestyle='--', label='Decision Threshold 1'),
        Line2D([0], [0], color='#710193', linestyle='--', label='Decision Threshold 2'),
        Line2D([0], [0], color='#311432', linestyle='--', label='Decision Threshold 3')
    ]
    
    # Determine the x and y axis limits
    x_min, x_max = 0, 210
    y_min, y_max = 0, 210

    # Specify the interval (10 units in this case)
    interval = 20

    # Calculate the minimum and maximum tick values based on the interval and data range
    x_tick_min = (x_min // interval) * interval
    x_tick_max = ((x_max // interval) + 1) * interval
    y_tick_min = (y_min // interval) * interval
    y_tick_max = ((y_max // interval) + 1) * interval

    # Create custom tick values for the x and y axes
    x_ticks = np.arange(x_tick_min, x_tick_max + interval, interval)
    y_ticks = np.arange(y_tick_min, y_tick_max + interval, interval)

    # Set the custom tick values, including 0
    plt.xticks(x_ticks, fontsize=20)
    plt.yticks(y_ticks, fontsize=20)



    # Adding labels and title
    plt.xlabel('$F_1$ Matching Score', fontsize=25)
    plt.ylabel('$F_2$ Matching Score', fontsize=25)

    # Adding the custom legend
    plt.legend(handles=custom_legend, fontsize=20)

    # Display the plot
    plt.show()

if __name__ == '__main__':
    main()
