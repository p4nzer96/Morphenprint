import sys
import os
import shutil
import traceback

def main():
    # parse command line parameters
    input_directory_path = sys.argv[1]
    output_directory_path = sys.argv[2]
    epochs = sys.argv[3]
    data_txt_path = sys.argv[4]
    
    try:
        folder_count = 0
        all_files = os.listdir(input_directory_path)
        fake_png_files = [file for file in all_files if file.endswith('_fake.png')]
        for fake_file in fake_png_files:
            fake_file_path = os.path.join(input_directory_path, fake_file)
            for root, _, files in os.walk(output_directory_path):
                count = 0
                morphed_minutiae_list_name = ''
                for file in files:
                    # Check if the file is an image
                    if (file.lower().endswith('_mm.txt')):
                        count = count + 1
                        if (count == 1):
                            morphed_minutiae_list_name = file
            
                if (morphed_minutiae_list_name != '' and fake_file_path):
                    try:
                        morphed_minutiae_list_file_name = str(morphed_minutiae_list_name).split('_mm', 1)[0]
                        fake_file_name = str(os.path.splitext(os.path.basename(fake_file_path))[0])
                        fake_file_name_part = fake_file_name.split('_mm', 1)[0]

                        if (morphed_minutiae_list_file_name == fake_file_name_part):
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