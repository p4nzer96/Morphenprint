import os
import subprocess
from tqdm import tqdm
import traceback
import sys

class Resize:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
    
    def resize_img_to_512_512(self):
        for file in tqdm(os.listdir(self.input_directory)):
            try:
                if file.endswith(".tif"):
                    file_path = os.path.join(self.input_directory, file)
                    file_name = os.path.basename(file_path)
                    file_name = file_name.split('.')[0]
                    file_name = file_name + '.png'
                    file_path_new = os.path.join(self.output_directory, file_name)
                    subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", file_path, "-gravity", "center", "-background", "white", "-extent", "640x640", "-units", "PixelsPerInch", "-density", "500", file_path_new], shell=True)
                    subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", file_path_new, "-gravity", "center", "-background", "white", "-extent", "512x512", "-units", "PixelsPerInch", "-density", "500", file_path_new], shell=True)
            except Exception as e: 
                print('Error in resizing')
                traceback.print_exc()

# Getting command-line arguments
input_directory_arg = sys.argv[1]
output_directory_arg = sys.argv[2]      

# Creating an instance of the Resize class
resize = Resize(input_directory_arg, output_directory_arg)

resize.resize_img_to_512_512()