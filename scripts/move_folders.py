import sys
import numpy as np
import os
import shutil


def main():
    directory_path = sys.argv[1]
    save_diff_imp_path = sys.argv[2]
    save_same_imp_path = sys.argv[3]
    error_txt = sys.argv[4]
    folder_count = 0
    for root, _, files in os.walk(directory_path): 
        try:
            original_files = [file for file in files if (file.lower().endswith('.png') and (not file.lower().endswith('_cropped.png')) and (not file.lower().endswith('_mmap.png')) and (not file.lower().endswith('_overlapped.png')) and (not file.lower().endswith('_15.png')) and (not file.lower().endswith('_30.png')) and (not file.lower().endswith('_55.png')))]
            if len(original_files) == 2:
                img_1_o = original_files[0]
                img_2_o = original_files[1]
                
                I1 = str(img_1_o).split('_')[0]
                I2 = str(img_2_o).split('_')[0]

                if (I1 != I2):              
                    destination_folder = os.path.join(save_diff_imp_path, os.path.basename(root))
                    if os.path.exists(destination_folder):
                        shutil.rmtree(destination_folder)
                    shutil.copytree(root, destination_folder)

                if (I1 == I2):              
                    destination_folder = os.path.join(save_same_imp_path, os.path.basename(root))
                    if os.path.exists(destination_folder):
                        shutil.rmtree(destination_folder)
                    shutil.copytree(root, destination_folder)
                
                folder_count = folder_count + 1
                print('Folder_count: ', folder_count)
            else:
                continue
        except Exception as e:
            with open(error_txt, 'a') as file:
                file.write('\n' + 'Image set - ' + str(os.path.basename(root)))
            print('Error in copying image -' + str(os.path.basename(root)) + str(e))
            continue

if __name__ == '__main__':
    main()
