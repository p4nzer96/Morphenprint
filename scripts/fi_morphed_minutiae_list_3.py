import cv2
import numpy as np
import sys
import os
import traceback
import fi_orientation
import translation
import rotation
import subprocess

import alignment.utils
from alignment import fi_alignment_config
import fi_alignment.loop_alignment as a_loop
import fi_alignment.arch_alignment as a_arch
import fi_alignment.whorl_alignment as a_whorl

import warnings

warnings.filterwarnings("ignore")


def get_updated_imgs(img1, img2, loop_difference_x):
    x_abs_diff = np.abs(loop_difference_x) - 100

    if loop_difference_x < 0:
        img1_updated = translation.translate_image(img1, x_abs_diff, 0)
        img2_updated = translation.translate_image(img2, -x_abs_diff, 0)
    elif loop_difference_x > 0:
        img1_updated = translation.translate_image(img1, -x_abs_diff, 0)
        img2_updated = translation.translate_image(img2, x_abs_diff, 0)
    else:
        img1_updated = img1
        img2_updated = img2

    return img1_updated, img2_updated


# Return only overlapped image
def get_overlapped_image(image1, image2):

    # Threshold the image
    gray_img_1 = 255 - image1
    cv2.threshold(gray_img_1, 100, 255, cv2.THRESH_BINARY)

    kernel = np.ones((30, 30), np.uint8)
    closing = cv2.morphologyEx(gray_img_1, cv2.MORPH_CLOSE, kernel)
    maskImage = cv2.cvtColor(closing, cv2.COLOR_GRAY2RGB)

    rgb_img_2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2RGB)
    rgb_img_2 = ~rgb_img_2
    cropped_overlapped_image2 = cv2.bitwise_and(rgb_img_2, maskImage)
    cropped_overlapped_image2 = ~cropped_overlapped_image2

    return cropped_overlapped_image2


def save_transformed_images(img1, img2, img1_path, img2_path, root, image_type, block_size):
    img2_h_center, img2_w_center = img2.shape[1] / 2, img2.shape[0] / 2
    txt_data = ''
    if image_type == 'loop' or image_type == 'whorl':
        # Get core points of a fingerprint images
        loop_list_img1, angles_img1, rel_img1 = fi_alignment_config.get_loop_list_angles_rel_img(img1, block_size)
        loop_list_img2, angles_img2, rel_img2 = fi_alignment_config.get_loop_list_angles_rel_img(img2, block_size)

        loop_difference_x = loop_list_img1[0][0][1] - loop_list_img2[0][0][1]

        if np.abs(loop_difference_x) > 100:
            img1, img2 = get_updated_imgs(img1, img2, loop_difference_x)
            loop_list_img1, angles_img1, rel_img1 = fi_alignment_config.get_loop_list_angles_rel_img(img1, block_size)
            loop_list_img2, angles_img2, rel_img2 = fi_alignment_config.get_loop_list_angles_rel_img(img2, block_size)

        # translate values
        tx = loop_list_img1[0][0][1] - loop_list_img2[0][0][1]
        ty = loop_list_img1[0][0][0] - loop_list_img2[0][0][0]


    elif image_type == 'arch':
        # Get center of a fingerprint image
        img1_blob_center_x, img1_blob_center_y = alignment.utils.get_center_of_image(img1)
        img2_blob_center_x, img2_blob_center_y = alignment.utils.get_center_of_image(img2)

        smooth_angles_img1, angles_img1, rel_img1 = fi_orientation.calculate_angles(img1, block_size, smoth=True)

        # translate values
        tx = img1_blob_center_x - img2_blob_center_x
        ty = img1_blob_center_y - img2_blob_center_y

        # Get similarity score dataframe
    if image_type == 'loop':
        transformed_img2, similarity_score_df = a_loop.get_loop_fi_sim_score_df(block_size, img2, angles_img1, rel_img1,
                                                                                tx, ty, loop_list_img1)

    if image_type == 'whorl':
        transformed_img2, similarity_score_df = a_whorl.get_whorl_fi_sim_score_df(block_size, img2, angles_img1,
                                                                                  rel_img1, tx, ty, loop_list_img1)

    if image_type == 'arch':
        transformed_img2, similarity_score_df = a_arch.get_arch_fi_sim_score_df(block_size, img2, angles_img1, rel_img1,
                                                                                tx, ty)

    # Find out the highest similarity score
    max_sim_score = similarity_score_df[
        similarity_score_df['similarity_score'] == similarity_score_df['similarity_score'].max()]

    # Apply the translation and rotation values on the transformed image2
    img2_t = translation.translate_image(transformed_img2, int(max_sim_score['tx']), int(max_sim_score['ty']))
    img2_t_r = rotation.rotate_image(img2_t, int(max_sim_score['rotation_angle']), (img2_w_center, img2_h_center))

    # Find core points of the new image and write core points of both image1 and image2 to a text file
    file_path = root + '/' + str(os.path.basename(root)) + '_core_sim_score.txt'

    if image_type == 'loop' or image_type == 'whorl':
        loop_list_img2_t_r, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, block_size)
        txt_data = '\n' + 'loop_list: ' + str(os.path.basename(img1_path)) + ' - ' + str(
            loop_list_img1) + '\n' + 'loop_list: ' + str(os.path.basename(img2_path)) + ' - ' + str(
            loop_list_img2_t_r) + '\n' + 'max_sim_score - ' + str(max_sim_score)

    elif image_type == 'arch':
        txt_data = 'max_sim_score - ' + str(max_sim_score)

    with open(file_path, 'a') as file:
        file.write(txt_data)

    return img2_t_r


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
            img3_path = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith('.png')) and (
                        not file.lower().endswith('_cropped.png') and (not file.lower().endswith('_overlapped.png'))):
                    count = count + 1
                    if count == 1:
                        img1_path = os.path.join(root, file)
                    if count == 2:
                        img2_path = os.path.join(root, file)
                    if count == 3:
                        img3_path = os.path.join(root, file)

            if (img1_path and img2_path and img3_path):
                img1 = cv2.imread(img1_path, 0)
                img2 = cv2.imread(img2_path, 0)
                img3 = cv2.imread(img3_path, 0)
                img2_t_r = save_transformed_images(img1, img2, img1_path, img2_path, root, image_type, block_size)
                img3_t_r = save_transformed_images(img1, img3, img1_path, img3_path, root, image_type, block_size)

                overlapped_img_1_2 = cv2.addWeighted(img1, 0.5, img2_t_r, 0.5, 0.0)
                overlapped_img_1_2_3 = cv2.addWeighted(overlapped_img_1_2, 0.5, img3_t_r, 0.5, 0.0)
                cv2.imwrite(root + '/img_overlapped.png', overlapped_img_1_2_3)

                # Save cropped image1 and image2 and increase its resolution to 500ppi
                img1_transformed_cropped_1 = cv2.cvtColor(get_overlapped_image(img2_t_r, img1), cv2.COLOR_BGR2GRAY)
                img2_transformed_cropped_1 = cv2.cvtColor(get_overlapped_image(img1, img2_t_r), cv2.COLOR_BGR2GRAY)

                img1_transformed_cropped_f = get_overlapped_image(img3_t_r, img1_transformed_cropped_1)
                img2_transformed_cropped_f = get_overlapped_image(img3_t_r, img2_transformed_cropped_1)
                img3_transformed_cropped_f = get_overlapped_image(img1_transformed_cropped_1, img3_t_r)

                cv2.imwrite(root + '/' + str(os.path.splitext(os.path.basename(img1_path))[0]) + '_cropped.png',
                            img1_transformed_cropped_f)
                cv2.imwrite(root + '/' + str(os.path.splitext(os.path.basename(img2_path))[0]) + '_cropped.png',
                            img2_transformed_cropped_f)
                cv2.imwrite(root + '/' + str(os.path.splitext(os.path.basename(img3_path))[0]) + '_cropped.png',
                            img3_transformed_cropped_f)

                img1_save_path = root + '/' + str(os.path.splitext(os.path.basename(img1_path))[0]) + '_cropped.png'
                img2_save_path = root + '/' + str(os.path.splitext(os.path.basename(img2_path))[0]) + '_cropped.png'
                img3_save_path = root + '/' + str(os.path.splitext(os.path.basename(img3_path))[0]) + '_cropped.png'

                subprocess.call(
                    ["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img1_save_path, "-units",
                     "PixelsPerInch", "-density", "500", img1_save_path], shell=True)
                subprocess.call(
                    ["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img2_save_path, "-units",
                     "PixelsPerInch", "-density", "500", img2_save_path], shell=True)
                subprocess.call(
                    ["C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe", "convert", img3_save_path, "-units",
                     "PixelsPerInch", "-density", "500", img3_save_path], shell=True)

            # print("Folder:", os.path.basename(root))
            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + os.path.basename(root) + os.path.basename(img1_path) + ',' + os.path.basename(
            img2_path) + ',' + os.path.basename(img3_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
