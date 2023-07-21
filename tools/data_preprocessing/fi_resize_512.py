import os
import subprocess
from tqdm import tqdm
import traceback
import sys


def resize_img_to_512_512(input_directory, output_directory):
    for file in tqdm(os.listdir(input_directory)):
        try:
            if file.endswith(".tif"):
                file_path = os.path.join(input_directory, file)
                file_name = os.path.basename(file_path)
                file_name = file_name.split('.')[0]
                file_name = file_name + '.png'
                file_path_new = os.path.join(output_directory, file_name)
                subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", file_path, "-gravity", "center", "-background", "white", "-extent", "640x640", "-units", "PixelsPerInch", "-density", "500",  file_path_new], shell=True)
                subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", file_path_new, "-gravity", "center", "-background", "white", "-extent", "512x512", "-units", "PixelsPerInch", "-density", "500", file_path_new], shell=True)

        except Exception as e:
            print('Error in resizing')
            traceback.print_exc()


def main():
    # Getting command-line arguments
    input_directory_arg = sys.argv[1]
    output_directory_arg = sys.argv[2]
    resize_img_to_512_512(input_directory_arg, output_directory_arg)


if __name__ == '__main__':
    main()
