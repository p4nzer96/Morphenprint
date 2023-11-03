import matplotlib.pyplot as plt
import sys
import traceback
import numpy as np


def get_x_y_coordinates(directory_path):
    X = list(range(0, 121, 20))
    Y_m = []
    Y_a = []
    with open(directory_path,"rt") as txtfile:
        output = txtfile.read()
    lines = output.split('\n')
    lines = [line for line in lines if line.strip() != '']
    for value in X:
            y_m_count = 0
            y_a_count = 0
            for index, line in enumerate(lines):
                try:
                    if len(line) > 0 and line[0] == '{':
                        X_F1_matching_score = float(line[line.find("Morph_Img1_score=") + len("Morph_Img1_score=") : line.find(", Morph_Img2_score=")])
                        #Y_F2_matching_score = float(line[line.find("Morph_Img2_score=") + len("Morph_Img2_score=") : line.find("}")])
                        Y_F2_matching_score = float(line[line.find("Morph_Img2_score=") + len("Morph_Img2_score=") : line.find(", Morph_Img3_score=")])
                        Z_F2_matching_score = float(line[line.find("Morph_Img3_score=") + len("Morph_Img3_score=") : line.find("}")])

                        if (X_F1_matching_score > value and Y_F2_matching_score > value and Z_F2_matching_score > value):
                        #if (X_F1_matching_score > value and Y_F2_matching_score > value):
                            y_m_count = y_m_count + 1
                        
                        if (X_F1_matching_score < value and Y_F2_matching_score < value and Z_F2_matching_score < value):
                        #if (X_F1_matching_score < value and Y_F2_matching_score < value):
                            y_a_count = y_a_count + 1
                                  
                except Exception as e:
                    print('Error -' + str(e))
                    traceback.print_exc() 

            Y_m.append(y_m_count / len(lines))   
            Y_a.append(y_a_count / len(lines))    

    return X, Y_m, Y_a


def main():
    directory_path = sys.argv[1]
    x, y_m, y_a = get_x_y_coordinates(directory_path)
    # Create a line graph
    
    #plt.plot(x, y_m, color='green', label='Double-Identity FPs')
    plt.plot(x, y_m, color='green', label='Triple-Identity FPs')
    plt.plot(x, y_a, color='red', label='Virtual-Identity FPs')

    # Add labels and title
    plt.xlabel('Decision Threshold', fontsize=16)
    plt.ylabel('Relative number of Fingerprints', fontsize=16)
    
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    # Show the legend
    plt.legend(prop={'size': 13})

    # Show the graph
    plt.show()


if __name__ == '__main__':
    main()
