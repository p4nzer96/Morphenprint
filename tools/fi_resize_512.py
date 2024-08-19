import os
import subprocess
from tqdm import tqdm
import traceback
import sys
from pathlib import Path


def resize_img_to_512_512(input_directory, output_directory):
    """
    Resize the images to 512x512

    Args:
        input_directory: Input directory containing the images
        output_directory: Output directory to store resized images
    """
    input_directory = Path(input_directory) if not isinstance(input_directory, Path) else input_directory
    output_directory = Path(output_directory) if not isinstance(output_directory, Path) else output_directory

    for file in tqdm(input_directory.iterdir()):
        try:
            if file.endswith(".tif"):
                file_path = file.resolve()
                file_name = file_path.stem + ".png"
                file_path_new = os.path.join(output_directory, file_name)
                subprocess.call(["convert", file_path, "-gravity", "center", "-background", "white", "-extent",
                                 "640x640", "-units", "PixelsPerInch", "-density", "500", file_path_new], shell=True)
                subprocess.call(["convert", file_path_new, "-gravity", "center", "-background", "white", "-extent",
                                 "512x512", "-units", "PixelsPerInch", "-density", "500", file_path_new], shell=True)

        except Exception:
            print('Error in resizing')
            traceback.print_exc()


def main():
    # Getting command-line arguments
    input_directory_arg = sys.argv[1]
    output_directory_arg = sys.argv[2]
    resize_img_to_512_512(input_directory_arg, output_directory_arg)


if __name__ == '__main__':
    main()
