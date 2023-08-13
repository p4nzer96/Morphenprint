import sys
import os
import shutil
import traceback

def main():
    # parse command line parameters
    input_directory_path = sys.argv[1]
    output_directory_path = sys.argv[2]
    method = sys.argv[3]
    epochs = sys.argv[4]
    data_txt_path = sys.argv[5]
    
    morphed_minutiae_map_path = ''
    if method == 'pointingMinutiae':
        end_path_str = '_pm_mmap.png'
    elif method == 'directedMinutiae':
        end_path_str = '_dm_mmap.png'
    else:
        end_path_str = '_pm_mmap.png'
    try:
        folder_count = 0
        all_files = os.listdir(input_directory_path)
        fake_png_files = [file for file in all_files if file.endswith('_fake.png')]
        for fake_file in fake_png_files:
            fake_file_path = os.path.join(input_directory_path, fake_file)
            for root, _, files in os.walk(output_directory_path):
                count = 0
                morphed_minutiae_map_path = ''
                for file in files:
                    # Check if the file is an image
                    if (file.lower().endswith(end_path_str)):
                        count = count + 1
                        if (count == 1):
                            morphed_minutiae_map_path = os.path.join(root, file)
            
                if (morphed_minutiae_map_path != '' and fake_file_path):
                    try:
                        morphed_minutiae_map_file_name = str(os.path.splitext(os.path.basename(morphed_minutiae_map_path))[0])
                        fake_file_name = str(os.path.splitext(os.path.basename(fake_file_path))[0])

                        if (morphed_minutiae_map_file_name in fake_file_name):
                            fake_file_end_str = ''
                            if (epochs == '15'):
                                fake_file_end_str = '_15.png'
                            elif (epochs == '30'):
                                fake_file_end_str = '_30.png'
                            elif (epochs == '55'):
                                fake_file_end_str = '_55.png'
                                
                            fake_file_name_new = fake_file_name + fake_file_end_str
                            destination_path = os.path.join(root, fake_file_name_new)
                            shutil.copy(fake_file_path, destination_path)
                            folder_count = folder_count + 1
                            print('Folder count - ' + str(folder_count))
                            break
                        else:
                            continue

                    except Exception as e:
                        with open(data_txt_path, 'a') as file:
                            file.write('\n' + 'Fake file - ' + str(os.path.basename(root)))
                        print('Error in copying image -' + str(os.path.basename(fake_file_path)) + str(e))
                        continue
                else:
                    continue

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()