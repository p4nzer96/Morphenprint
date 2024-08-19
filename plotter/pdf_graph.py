import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys
import numpy as np


def get_data(directory_path):
    with open(directory_path, 'r') as file:
        lines = file.readlines()

    # Remove the first and last lines
    lines = lines[1:-1]

    # Initialize a list to store the values
    values = []

    # Loop through the remaining lines
    for line in lines:
        # Split the line based on semicolon and get the second part
        parts = line.split(';')
        if len(parts) > 1:
            value = parts[1].strip()
            values.append(float(value))

    return np.array(values, dtype=np.float64)


def main():
    # Sample data (replace these with your own data)
    directory_path_org_1 = sys.argv[1]
    directory_path_org_2 = sys.argv[2]
    directory_path_org_3 = sys.argv[3]
    directory_path_res_15 = sys.argv[4]
    directory_path_res_30 = sys.argv[5]
    directory_path_res_55 = sys.argv[6]

    org_1 = get_data(directory_path_org_1)
    org_2 = get_data(directory_path_org_2)
    org_3 = get_data(directory_path_org_3)

    res_15 = get_data(directory_path_res_15)
    res_30 = get_data(directory_path_res_30)
    res_55 = get_data(directory_path_res_55)

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Create KDE plots for both datasets
    kde1 = gaussian_kde(org_1)
    kde2 = gaussian_kde(org_2)
    kde3 = gaussian_kde(org_3)
    kde4 = gaussian_kde(res_15)
    kde5 = gaussian_kde(res_30)
    kde6 = gaussian_kde(res_55)

    # Calculate the range for x values
    x_values = np.linspace(0, 100, 1000)

    # Plot KDE curves
    ax.plot(x_values, kde1(x_values), label='$F_1$', color='#0e4b81')
    ax.plot(x_values, kde2(x_values), label='$F_2$', color='#7a258d')
    ax.plot(x_values, kde3(x_values), label='$F_3$', color='#1c74a6')
    ax.plot(x_values, kde4(x_values), label='$F_{morph15}$', color='orange')
    ax.plot(x_values, kde5(x_values), label='$F_{morph30}$', color='green')
    ax.plot(x_values, kde6(x_values), label='$F_{morph55}$', color='red')

    # Set Y-axis ticks
    y_ticks = np.arange(0, 0.07, 0.01)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks, fontsize=20)
    x_ticks = np.arange(0, 110, 20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticks, fontsize=20)

    # Add labels and title
    ax.set_xlabel('NFIQ2 Scores', fontsize=25)
    ax.set_ylabel('Density', fontsize=25)

    # Add a legend
    ax.legend(prop={'size': 22.5})

    # Show the graph
    plt.show()


if __name__ == '__main__':
    main()
