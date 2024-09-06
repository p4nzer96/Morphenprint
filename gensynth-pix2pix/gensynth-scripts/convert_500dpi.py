import os
import subprocess
import sys
from tqdm import tqdm

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

    # Iterate over the files
    for file in tqdm(files):
        # Check if the file is of image type
        if file.endswith('.png'):
            inp_file_path = os.path.join(input_dir, file)
            out_file_path = os.path.join(output_dir, file)

            subprocess.call(['convert', inp_file_path, '-units', 'PixelsPerInch', '-density', '500', out_file_path])


if __name__ == '__main__':
    main()