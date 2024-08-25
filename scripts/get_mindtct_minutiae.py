import sys
import os
import traceback

def get_minutiae_file(img_1, img_2):
    pass    

def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            img1_cropped_path = ''
            img2_cropped_path = ''
            #img1_minutiae_save_path = ''
            #img2_minutiae_save_path = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if file.lower().endswith('_cropped.jpg'):
                    count += 1
                    if count == 1:
                        img1_cropped_path = os.path.join(root, file)
                    if count == 2:
                        img2_cropped_path = os.path.join(root, file)

            if img1_cropped_path and img2_cropped_path:
                # TODO: to replace the below code with the actual function
                pass
                #img1_minutiae_save_path = root + '/' + str(
                    #os.path.splitext(os.path.basename(img1_cropped_path))[0]) + '_minutiae.txt'
                #get_verifinger_minutiae(img1_cropped_path, img1_minutiae_save_path)

                #img2_minutiae_save_path = root + '/' + str(
                    #os.path.splitext(os.path.basename(img2_cropped_path))[0]) + '_minutiae.txt'
                #get_verifinger_minutiae(img2_cropped_path, img2_minutiae_save_path)

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print(
            'Error -' + os.path.basename(img1_cropped_path) + ',' + os.path.basename(img2_cropped_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
