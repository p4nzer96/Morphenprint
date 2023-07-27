import sys
import os
import traceback
from subprocess import check_output

def get_verifinger_minutiae(img_path, minutiae_save_path_name):
    try:
        # get the response
        lines = check_output(['VerifingerMinutiae', img_path])

        # Save minutiae to a text file
        with open(minutiae_save_path_name, 'w') as file:
            for line in lines:
                file.write(f"{line}\n")

    except Exception as e:
        print('Error in fetching verfinger minutiae -' + str(e))
        traceback.print_exc()


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    for root, _, files in os.walk(directory_path):
        try:   
            img1_cropped_path = ''
            img2_cropped_path = ''
            img1_minutiae_save_name = ''
            img2_minutiae_save_name = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith('_cropped.png')):
                    count = count + 1
                    if (count == 1):
                        img1_cropped_path = os.path.join(root, file)
                    if (count == 2):
                        img2_cropped_path = os.path.join(root, file)
            
            if (img1_cropped_path and img2_cropped_path):
                img1_minutiae_save_name = str(os.path.splitext(os.path.basename(img1_cropped_path))[0]) + '_minutiae.txt'
                get_verifinger_minutiae(img1_cropped_path, img1_minutiae_save_name)

                img2_minutiae_save_name = str(os.path.splitext(os.path.basename(img2_cropped_path))[0]) + '_minutiae.txt'
                get_verifinger_minutiae(img2_cropped_path, img2_minutiae_save_name)
        
        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()


if __name__ == '__main__':
    main()