import sys
import os
import traceback
from subprocess import check_output


def get_verifinger_minutiae(img_path, minutiae_save_path):
    try:
        # get the response
        out_lines = check_output(['VerifingerMinutiae', img_path])
        lines = out_lines.split(b'\n')

        # Save minutiae in bytes to a text file
        with open(minutiae_save_path, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(f"{line}\n")

        # variables
        modified_lines = []
        extracted_lines = []
        start_index = 0
        end_index = 0

        # Read from saved minutiae file and extract only minutia points
        with open(minutiae_save_path, 'r') as file:
            for index, line in enumerate(file, 1):
                try:
                    if line.startswith('b'):
                        line = line[1:]
                        line = line.replace("'", "")
                        if line.startswith('#minutiae'):
                            start_index = index
                        if line.startswith('deltasCount'):
                            end_index = index
                    modified_lines.append(line)
                except Exception:
                    continue

        if start_index != 0 and end_index != 0:
            extracted_lines = modified_lines[start_index: end_index - 1]

        with open(minutiae_save_path, 'w') as file:
            file.writelines(extracted_lines)

    except Exception as e:
        print('Error in fetching verfinger minutiae -' + str(e))
        traceback.print_exc()


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            img1_cropped_path = ''
            img2_cropped_path = ''
            img3_cropped_path = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if file.lower().endswith('_cropped.png'):
                    count = count + 1
                    if count == 1:
                        img1_cropped_path = os.path.join(root, file)
                    if count == 2:
                        img2_cropped_path = os.path.join(root, file)
                    if count == 3:
                        img3_cropped_path = os.path.join(root, file)

            if img1_cropped_path and img2_cropped_path and img3_cropped_path:
                img1_minutiae_save_path = root + '/' + str(
                    os.path.splitext(os.path.basename(img1_cropped_path))[0]) + '_minutiae.txt'
                get_verifinger_minutiae(img1_cropped_path, img1_minutiae_save_path)

                img2_minutiae_save_path = root + '/' + str(
                    os.path.splitext(os.path.basename(img2_cropped_path))[0]) + '_minutiae.txt'
                get_verifinger_minutiae(img2_cropped_path, img2_minutiae_save_path)

                img3_minutiae_save_path = root + '/' + str(
                    os.path.splitext(os.path.basename(img3_cropped_path))[0]) + '_minutiae.txt'
                get_verifinger_minutiae(img3_cropped_path, img3_minutiae_save_path)

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + os.path.basename(img1_cropped_path) + ',' + os.path.basename(
            img2_cropped_path) + ',' + os.path.basename(img3_cropped_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
