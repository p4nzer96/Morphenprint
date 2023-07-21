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
import translation
import rotation
import subprocess
import fi_alignment.loop_alignment as a_loop


import warnings
warnings.filterwarnings("ignore")


def get_overlapped_image(image1, image2):
  gray_img_1 = image1

  gray_img_1 = 255 - gray_img_1
  gray_img_1[gray_img_1 > 100] = 255
  gray_img_1[gray_img_1 <= 100] = 0

  kernel = np.ones((30, 30), np.uint8)
  closing = cv2.morphologyEx(gray_img_1, cv2.MORPH_CLOSE, kernel)
  maskImage = cv2.cvtColor(closing, cv2.COLOR_GRAY2RGB)

  rgb_img_2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2RGB)
  rgb_img_2 = ~rgb_img_2
  cropped_overlapped_image2 = cv2.bitwise_and(rgb_img_2, maskImage)
  cropped_overlapped_image2 = ~cropped_overlapped_image2

  return cropped_overlapped_image2


def main():
    directory_path = sys.argv[1]
    image_type = sys.argv[2]
    block_size = 16
    try:
        for root, _, files in os.walk(directory_path):
            img1_path = ''
            img2_path = ''
            txt_data = ''
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
                img1_h_center, img1_w_center = img1.shape[1]/2, img1.shape[0]/2
                img2_h_center, img2_w_center = img2.shape[1]/2, img2.shape[0]/2
                smooth_angles_img1, angles_img1, rel_img1 = fi_orientation.calculate_angles(
                    img1, block_size, smoth=True)
                smooth_angles_img2, angles_img2, rel_img2 = fi_orientation.calculate_angles(
                    img2, block_size, smoth=True)

                _, _, mask1 = fi_segmentation.create_segmented_and_variance_images(
                    img1, block_size, 0.2)
                _, _, mask2 = fi_segmentation.create_segmented_and_variance_images(
                    img2, block_size, 0.2)

                _, loop_1d_1,  loop_list_1, _, _ = fi_singularity.calculate_singularities(
                    img1, smooth_angles_img1, 1, block_size, mask1)
                _, loop_1d_2, loop_list_2, _, _ = fi_singularity.calculate_singularities(
                    img2, smooth_angles_img2, 1, block_size, mask2)

                tx = loop_list_1[0][0][1] - loop_list_2[0][0][1]
                ty = loop_list_1[0][0][0] - loop_list_2[0][0][0]

                if image_type == 'loop':
                    translated_img2, similarity_score_df = a_loop.get_loop_fi_sim_score_df(
                        block_size, img1, img2, angles_img1, rel_img1, tx, ty)

                # if image_type == 'whorl':
                #   similarity_score_df = a_loop.get_loop_fi_sim_score_df(block_size, img1, img2, angles_img1, rel_img1, tx, ty)

                # if image_type == 'arch':
                #   similarity_score_df = a_loop.get_loop_fi_sim_score_df(block_size, img1, img2, angles_img1, rel_img1, tx, ty)

                max_sim_score = similarity_score_df[similarity_score_df[
                    'similarity_score'] == similarity_score_df['similarity_score'].max()]
                print(max_sim_score)

                file_path = root + '/' + str(os.path.basename(root)) + '_core_sim_score.txt' 
                txt_data = 'loop_list_1 - ' + str(loop_list_1) + '\n' + 'loop_list_2 - ' + str(loop_list_2) + '\n' + 'max_sim_score - ' + str(max_sim_score)
                with open(file_path, 'w') as file:
                    file.write(txt_data)

                img2_t = translation.translate_image(translated_img2, int(
                    max_sim_score['tx']), int(max_sim_score['ty']))
                img2_t_r = rotation.rotate_image(img2_t, int(
                    max_sim_score['rotation_angle']), (img2_w_center, img2_h_center))

                overlapped_img = cv2.addWeighted(img1, 0.5, img2_t_r, 0.5, 0.0)
                cv2.imwrite(root + '/img_overlapped.png', overlapped_img)

                img1_transformed_cropped = get_overlapped_image(img2_t_r, img1)
                img2_transformed_cropped = get_overlapped_image(img1, img2_t_r)
                cv2.imwrite(root + '/' + str(os.path.basename(img1_path)) + '_cropped.png', img1_transformed_cropped)
                cv2.imwrite(root + '/' + str(os.path.basename(img2_path)) + '_cropped.png', img2_transformed_cropped)

                img1_save_path = root + '/' + str(os.path.basename(img1_path)) + '_cropped.png'
                img2_save_path = root + '/' + str(os.path.basename(img2_path)) + '_cropped.png'

                subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img1_save_path, "-density", "500", img1_save_path], shell=True)
                subprocess.call(["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img2_save_path, "-density", "500",  img2_save_path], shell=True)

            print("Folder:", os.path.basename(root))

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
