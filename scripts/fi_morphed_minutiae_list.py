import cv2
import numpy as np
import pandas as pd
import math
import sys
import os
import traceback
import fi_orientation
import fi_segmentation
import fi_singularity

import warnings
warnings.filterwarnings("ignore")


def main():
  directory_path = sys.argv[1]
  block_size = 16
  img1_path = ''
  img2_path = ''
  try:
    for root, _, files in os.walk(directory_path):
      for index, file in enumerate(files):
        # Check if the file is an image
        if file.lower().endswith(('.png')):
          if (index == 0):
            img1_path = os.path.join(root, file)
          if (index == 1): 
            img2_path = os.path.join(root, file)

      if (img1_path and img2_path):
        img1 = cv2.imread(img1_path, 0)
        img2 = cv2.imread(img2_path, 0)
        img1_h, img1_w = img1.shape[1], img1.shape[0]
        img2_h, img2_w = img2.shape[1], img2.shape[0]
        img1_h_center, img1_w_center = img1.shape[1]/2, img1.shape[0]/2
        img2_h_center, img2_w_center = img2.shape[1]/2, img2.shape[0]/2
        smooth_angles_img1, angles_img1, rel_img1 = fi_orientation.calculate_angles(img1, block_size, smoth=True)
        smooth_angles_img2, angles_img2, rel_img2 = fi_orientation.calculate_angles(img2, block_size, smoth=True)

        seg_img1, norm_img1, mask1 = fi_segmentation.create_segmented_and_variance_images(img1, block_size, 0.2)
        seg_img2, norm_img2, mask2 = fi_segmentation.create_segmented_and_variance_images(img2, block_size, 0.2)

        result_img_1, loop_1d_1,  loop_list_1, delta_list_1, whorl_list_1 = fi_singularity.calculate_singularities(img1, smooth_angles_img1, 1, block_size, mask1)
        result_img_2, loop_1d_2, loop_list_2, delta_list_2, whorl_list_2 = fi_singularity.calculate_singularities(img2, smooth_angles_img2, 1, block_size, mask2)

        # cv2.imshow('Img1',result_img_1)
        # cv2.imshow('Img2', result_img_2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
      
      print("Folder:", os.path.basename(root))
  
  except Exception as e:
     print('Error -' + str(e))
     traceback.print_exc()

if __name__ == '__main__':
    main()