import sys
import os
import shutil
import traceback

def main():
    # parse command line parameters
    input_directory_path = sys.argv[1]
    output_directory_path = sys.argv[2]
    method = sys.argv[3]
    
    morphed_minutiae_map_path = ''
    if method == 'pointingMinutiae':
        end_path_str = '_pm_mmap.png'
    elif method == 'directedMinutiae':
        end_path_str = '_dm_mmap.png'
    else:
        end_path_str = '_pm_mmap.png'
    try:
        folder_count = 0
        for root, _, files in os.walk(input_directory_path):
            count = 0
            morphed_minutiae_map_path = ''
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith(end_path_str)):
                    count = count + 1
                    if (count == 1):
                        morphed_minutiae_map_path = os.path.join(root, file)
            
            # create minutiae maps.
            if (morphed_minutiae_map_path != ''):
                try:
                    shutil.copy(morphed_minutiae_map_path, output_directory_path)
                    folder_count = folder_count + 1
                    print('Folder count - ' + str(folder_count))
                except Exception as e:
                    print('Error in copying image -' + str(e))
                    continue
            else:
                continue

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()