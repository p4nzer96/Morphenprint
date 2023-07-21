import os
import sys
import base64
import json
import requests
from subprocess import check_output


def get_verifinger_minutiae(img_path):
    """ Get the minutiae from Verifinger.
    :param img_path: Path to the image.
    :return: The minutiae.
    """
    
    try:
        # get the response
        str_lines = check_output( ['VerifingerMinutiae', img_path] )

        # parse the response
        lines = str_lines.split(b'\n');

        # If needed save the minutiae to text files
        with open('results.txt', 'w') as file:
            for line in lines:
                file.write(f"{line}\n")
        
        
        # minutiaelist=list()
        # for line in lines:
        #     if len(line) > 0 and line[0] == '{':
        #         X = line[line.find("X=") + len("X=") : line.find(", Y")]
        #         Y = line[line.find("Y=") + len("Y=") : line.find(", T")]
        #         Type = line[line.find("Type=") + len("Type=") : line.find(", A")]
        #         Angle = line[line.find("Angle=") + len("Angle=") : line.find("\xc2\xb0,")]
        #         Quality = line[line.find("Quality=") + len("Quality=") : line.find("%,")]
        #         Curvature = line[line.find("Curvature=") + len("Curvature=") : line.find(", G")]
        #         G = line[line.find("G=") + len("G=") : line.find("}")]
        #         minutiae = {'X': X, 'Y': Y, 'Type': Type, 'Angle': Angle, 'Quality': Quality, 'Curvature': Curvature, 'G': G }
        #         print(minutiae)
    except:
        print("Couldn't execute the fingerprints: " + img_path)


def main():
    if (len(sys.argv) < 2):
        print('Usage: python '+sys.argv[0]+ ' <img_path>')
        print('\img_path: This is the path to the image.')
        sys.exit(0)
    
    # parse command line parameters
    img_path = sys.argv[1]

    get_verifinger_minutiae(img_path)


if __name__ == '__main__':
    main()