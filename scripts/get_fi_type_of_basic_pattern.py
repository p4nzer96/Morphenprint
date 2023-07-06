import orientation
import segmentation
from singularities import Singularities
from basic_pattern import BasicPattern
import sys
import os
import cv2
from tqdm import tqdm
import traceback
import shutil

class BasicPatternType:
    def __init__(self, input_directory, output_whorl_directory_arg, output_loop_directory_arg, output_arch_directory_arg):
        self.input_directory = input_directory
        self.output_whorl_directory_arg = output_whorl_directory_arg
        self.output_loop_directory_arg = output_loop_directory_arg
        self.output_arch_directory_arg = output_arch_directory_arg
        self.block_size = 16

    def get_type_of_basic_pattern(self):
        for file in tqdm(os.listdir(self.input_directory)):
            try:
                if file.endswith(".png"):
                    file_path = self.input_directory + '/' + file
                    img = cv2.imread(file_path, 0)
                    angles_img = orientation.calculate_angles(img, self.block_size, smoth=True)
                    _, _, mask = segmentation.create_segmented_and_variance_images(img, self.block_size, 0.2)
                    singularities = Singularities(img, angles_img, 1, self.block_size, mask)
                    _, _, loop_list, delta_list, whorl_list = singularities.calculate_singularities()
                    basic_pattern = BasicPattern(loop_list, delta_list, whorl_list)
                    img_type = basic_pattern.get_type_of_basic_pattern()
                    src = os.path.join(self.input_directory, file)
                    if (img_type == 'whorl'):
                        dst = os.path.join(self.output_whorl_directory_arg, file)
                    elif (img_type == 'loop'):
                        dst = os.path.join(self.output_loop_directory_arg, file)
                    elif (img_type == 'arch'):
                        dst = os.path.join(self.output_arch_directory_arg, file)    
                    else:
                        continue  
                    shutil.copy(src, dst)    
   
            except Exception as e: 
                print('Error in getting fingerprints basic pattern')
                traceback.print_exc()

input_directory_arg = sys.argv[1]
output_whorl_directory_arg = sys.argv[2]
output_loop_directory_arg = sys.argv[3]
output_arch_directory_arg = sys.argv[4]

# Creating an instance of the Resize class
basicPatternType = BasicPatternType(input_directory_arg, output_whorl_directory_arg, output_loop_directory_arg, output_arch_directory_arg)

basicPatternType.get_type_of_basic_pattern()


