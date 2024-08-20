import os
import subprocess
import sys
import traceback
import warnings

import cv2
import numpy as np

import alignment.arch_alignment as a_arch
import alignment.loop_alignment as a_loop
import alignment.whorl_alignment as a_whorl

from alignment.transform import translate, rotate
from alignment.centering import get_center_of_image
from alignment.orientation import calculate_angles
from alignment.fi_alignment_config import get_loop_list_angles_rel_img

warnings.filterwarnings("ignore")


def get_updated_imgs(img1, img2, loop_difference_x):
    x_abs_diff = np.abs(loop_difference_x) - 100

    if loop_difference_x < 0:
        img1_updated = translate(img1, x_abs_diff, 0)
        img2_updated = translate(img2, -x_abs_diff, 0)
    elif loop_difference_x > 0:
        img1_updated = translate(img1, -x_abs_diff, 0)
        img2_updated = translate(img2, x_abs_diff, 0)
    else:
        img1_updated = img1
        img2_updated = img2

    return img1_updated, img2_updated


# Return only overlapped image
def get_overlapped_image(image1, image2):
    """
    Get overlapped image of two fingerprint images
    Args:
        image1: The first fingerprint image
        image2: The second fingerprint image

    Returns:
        The overlapped image of the two fingerprint images
    """
    gray_img_1 = image1

    # Inverting the image
    gray_img_1 = 255 - gray_img_1

    # Thresholding the image
    gray_img_1[gray_img_1 > 100] = 255
    gray_img_1[gray_img_1 <= 100] = 0

    # Morphological closing
    kernel = np.ones((30, 30), np.uint8)
    closing = cv2.morphologyEx(gray_img_1, cv2.MORPH_CLOSE, kernel)

    maskImage = cv2.cvtColor(closing, cv2.COLOR_GRAY2RGB)

    rgb_img_2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2RGB)
    rgb_img_2 = ~rgb_img_2
    cropped_overlapped_image2 = cv2.bitwise_and(rgb_img_2, maskImage)
    cropped_overlapped_image2 = ~cropped_overlapped_image2

    return cropped_overlapped_image2


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    image_type = sys.argv[2]
    block_size = 16
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            img1_path = ''
            img2_path = ''
            txt_data = ''
            count = 0
            for file in files:
                # Check if the file is an image
                file_l = file.lower()
                if ((file_l.endswith('.png')) and (not file_l.endswith('_cropped.png')
                                                   and (not file_l.endswith('_overlapped.png')))):
                    count += 1
                    if count == 1:
                        img1_path = os.path.join(root, file)
                    if count == 2:
                        img2_path = os.path.join(root, file)

            if img1_path and img2_path:
                img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
                img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

                # Getting the center of the second image
                img2_h_center, img2_w_center = img2.shape[1] // 2, img2.shape[0] // 2

                if image_type in ['loop', 'whorl']:

                    # Get core points of a fingerprint images
                    loop_list_img1, angles_img1, rel_img1 = get_loop_list_angles_rel_img(img1, block_size)
                    loop_list_img2, angles_img2, rel_img2 = get_loop_list_angles_rel_img(img2, block_size)

                    loop_difference_x = loop_list_img1[0][0][1] - loop_list_img2[0][0][1]

                    if np.abs(loop_difference_x) > 100:
                        img1, img2 = get_updated_imgs(img1, img2, loop_difference_x)
                        loop_list_img1, angles_img1, rel_img1 = get_loop_list_angles_rel_img(img1, block_size)
                        loop_list_img2, angles_img2, rel_img2 = get_loop_list_angles_rel_img(img2, block_size)

                    # translate values
                    tx = loop_list_img1[0][0][1] - loop_list_img2[0][0][1]
                    ty = loop_list_img1[0][0][0] - loop_list_img2[0][0][0]

                elif image_type == 'arch':

                    # Get center of a fingerprint image
                    img1_blob_center_x, img1_blob_center_y = get_center_of_image(img1)
                    img2_blob_center_x, img2_blob_center_y = get_center_of_image(img2)

                    smooth_angles_img1, angles_img1, rel_img1 = calculate_angles(img1, block_size, smooth=True)

                    # translate values
                    tx = img1_blob_center_x - img2_blob_center_x
                    ty = img1_blob_center_y - img2_blob_center_y

                # Get similarity score dataframe
                if image_type == 'loop':
                    transformed_img2, similarity_score_df = a_loop.get_loop_fi_sim_score_df(block_size, img2,
                                                                                            angles_img1, rel_img1, tx,
                                                                                            ty, loop_list_img1)

                if image_type == 'whorl':
                    transformed_img2, similarity_score_df = a_whorl.get_whorl_fi_sim_score_df(block_size, img2,
                                                                                              angles_img1, rel_img1, tx,
                                                                                              ty, loop_list_img1)

                if image_type == 'arch':
                    transformed_img2, similarity_score_df = a_arch.get_arch_fi_sim_score_df(block_size, img2,
                                                                                            img1_blob_center_x,
                                                                                            img1_blob_center_y,
                                                                                            angles_img1, rel_img1, tx,
                                                                                            ty)
                # Find out the highest similarity score
                max_sim_score = similarity_score_df[
                    similarity_score_df['similarity_score'] == similarity_score_df['similarity_score'].max()]

                # Apply the translation and rotation values on the transformed image2
                img2_t = translate(transformed_img2, int(max_sim_score['tx']),
                                                     int(max_sim_score['ty']))
                img2_t_r = rotate(img2_t, int(max_sim_score['rotation_angle']),
                                                 (img2_w_center, img2_h_center))

                # Find core points of the new image and write core points of both image1 and image2 to a text file
                file_path = root + '/' + str(os.path.basename(root)) + '_core_sim_score.txt'

                if image_type == 'loop' or image_type == 'whorl':
                    loop_list_img2_t_r, _, _ = get_loop_list_angles_rel_img(img2_t_r, block_size)
                    txt_data = 'loop_list: ' + str(os.path.basename(img1_path)) + ' - ' + str(
                        loop_list_img1) + '\n' + 'loop_list: ' + str(os.path.basename(img2_path)) + ' - ' + str(
                        loop_list_img2_t_r) + '\n' + 'max_sim_score - ' + str(max_sim_score)

                elif image_type == 'arch':
                    txt_data = 'max_sim_score - ' + str(max_sim_score)

                with open(file_path, 'w') as file:
                    file.write(txt_data)

                # Save the overlapped image
                overlapped_img = cv2.addWeighted(img1, 0.5, img2_t_r, 0.5, 0.0)
                cv2.imwrite(root + '/img_overlapped.png', overlapped_img)

                # Save cropped image1 and image2 and increase its resolution to 500ppi
                img1_transformed_cropped = get_overlapped_image(img2_t_r, img1)
                img2_transformed_cropped = get_overlapped_image(img1, img2_t_r)
                cv2.imwrite(root + '/' + str(os.path.splitext(os.path.basename(img1_path))[0]) + '_cropped.png',
                            img1_transformed_cropped)
                cv2.imwrite(root + '/' + str(os.path.splitext(os.path.basename(img2_path))[0]) + '_cropped.png',
                            img2_transformed_cropped)

                img1_save_path = root + '/' + str(os.path.splitext(os.path.basename(img1_path))[0]) + '_cropped.png'
                img2_save_path = root + '/' + str(os.path.splitext(os.path.basename(img2_path))[0]) + '_cropped.png'

                subprocess.call(
                    ["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img1_save_path, "-units",
                     "PixelsPerInch", "-density", "500", img1_save_path], shell=True)
                subprocess.call(
                    ["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img2_save_path, "-units",
                     "PixelsPerInch", "-density", "500", img2_save_path], shell=True)

                # subprocess.call(["convert", img1_save_path, "-units", "PixelsPerInch", "-density", "500",
                # img1_save_path]) subprocess.call(["convert", img2_save_path, "-units", "PixelsPerInch", "-density",
                # "500", img2_save_path])

            # print("Folder:", os.path.basename(root))
            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + os.path.basename(img1_path) + ',' + os.path.basename(img2_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
