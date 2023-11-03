import sys
import numpy as np
import os
import shutil


def main():
    directory_path = sys.argv[1]
    error_txt = sys.argv[2]
    folder_count = 0
    for root, _, files in os.walk(directory_path): 
        try:
            files_mm = [file for file in files if (file.lower().endswith('_mm.txt'))]
            files_15 = [file for file in files if (file.lower().endswith('_15.png'))]
            files_30 = [file for file in files if (file.lower().endswith('_30.png'))]
            files_55 = [file for file in files if (file.lower().endswith('_55.png'))]
            files_mm_name = str(files_mm[0]).split('_mm', 1)[0]
            print(files_mm_name)
            if len(files_15) > 1:
                for file in files_15:
                    try:
                        if (files_mm_name != str(file).split('_mm', 1)[0]):
                            print(str(file).split('_mm', 1)[0])
                            file_to_remove = os.path.join(root, file)
                            if os.path.exists(file_to_remove):
                                os.remove(file_to_remove)
                    except:
                        continue

            if len(files_30) > 1:
                for file in files_30:
                    try:
                        if (files_mm_name != str(file).split('_mm', 1)[0]):
                            print(str(file).split('_mm', 1)[0])
                            file_to_remove = os.path.join(root, file)
                            if os.path.exists(file_to_remove):
                                os.remove(file_to_remove)
                    except:
                        continue

            if len(files_55) > 1:
                for file in files_55:
                    try:
                        if (files_mm_name != str(file).split('_mm', 1)[0]):
                            print(str(file).split('_mm', 1)[0])
                            file_to_remove = os.path.join(root, file)
                            if os.path.exists(file_to_remove):
                                os.remove(file_to_remove)
                    except:
                        continue

            folder_count = folder_count + 1
            print('Folder_count: ', folder_count)
        
        except Exception as e:
            with open(error_txt, 'a') as file:
                file.write('\n' + 'Image set - ' + str(os.path.basename(root)))
            print('Error in copying image -' + str(os.path.basename(root)) + str(e))
            continue

if __name__ == '__main__':
    main()
