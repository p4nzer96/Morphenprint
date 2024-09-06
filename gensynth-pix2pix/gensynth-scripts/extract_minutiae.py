import os
import subprocess
import sys


def extract_minutiae(img_path, txt_path_output):
    """ Extract minutiae from the image and save text files.

    :param img_path: Path to the image.
    :param txt_path_output: Path to the text file.
    :return: True if minutiae extraction is successful, False otherwise.
    """
    try:
        str_lines = subprocess.check_output( ['VerifingerMinutiae', img_path] )
        str_lines = str_lines.decode()
        with open(txt_path_output, 'w') as file:
            file.write(str_lines)
        return True
    except subprocess.CalledProcessError:
        print("cannot extract minutiae: " + img_path)
        return False


def main():

    if ( len(sys.argv) < 3 ):
        print('Usage: python '+sys.argv[0]+ ' <input_dir> <output_dir>')
        print('\tinput_dir: this folder should contain the fingerprint images')
        print('\toutput_dir: padded images will be stored in this folder')
        sys.exit(0)
    
    # Parse the command line arguments
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the list of files in the input directory
    files = os.listdir(input_dir)
    num_files = len(files)

    # Iterate over the files
    for idx, file in enumerate(files):
        # Check if the file is of image type
        if file.endswith('.png'):
            print('['+str(idx+1)+'/'+ str(num_files)+']: ' + file)
            inp_file_path = os.path.join(input_dir, file)
            base_name = file.split('.')[0]
            txt_file_name = base_name + '.txt'
            out_file_path = os.path.join(output_dir, txt_file_name)

            extract_minutiae(inp_file_path, out_file_path)


if __name__ == '__main__':
    main()