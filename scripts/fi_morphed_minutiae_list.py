import warnings

import cv2
import numpy as np

from alignment.utils import get_center_of_image
from alignment.transform import translate, rotate
from alignment.orientation import calculate_angles
from alignment.arch_alignment import get_arch_sim_score_df
from alignment.loop_alignment import get_loop_sim_score_df
from alignment.whorl_alignment import get_whorl_sim_score_df
from alignment.fi_alignment_config import get_loop_list_angles_rel_img

warnings.filterwarnings("ignore")


def get_updated_imgs(img1, img2, loop_difference_x):
    """
    Update the images based on the loop difference in x-axis

    Args:
        img1: The first fingerprint image
        img2: The second fingerprint image
        loop_difference_x: The difference in x-axis of the loop singularity

    Returns:
        The updated images
    """
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
    gray_img_1 = cv2.threshold(gray_img_1, 100, 255, cv2.THRESH_BINARY)[1]

    # Morphological closing
    kernel = np.ones((30, 30), np.uint8)
    closing = cv2.morphologyEx(gray_img_1, cv2.MORPH_CLOSE, kernel)

    maskImage = cv2.cvtColor(closing, cv2.COLOR_GRAY2RGB)

    rgb_img_2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2RGB)
    rgb_img_2 = ~rgb_img_2
    cropped_overlapped_image2 = cv2.bitwise_and(rgb_img_2, maskImage)
    cropped_overlapped_image2 = ~cropped_overlapped_image2

    return cropped_overlapped_image2


def align_images(combinations, W, overlapped_path):

    for i, (img1_path, img2_path, img_type) in enumerate(combinations):
        try:

            # Read the images
            img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

            # Get the center of the second image
            img_center_2 = (img2.shape[0] // 2, img2.shape[1] // 2)

            # Loop and whorl have at least one loop singularity
            if img_type in ["loop", "whorl"]:

                # Getting the loop lists

                loop_list_1, angles_1, rel_1 = get_loop_list_angles_rel_img(img1, W)
                loop_list_2, _, _ = get_loop_list_angles_rel_img(img2, W)

                # Get the difference in x-axis of the loop singularity (first point of the first loop singularity)
                # Name: l{n. loop}{n. point}_{x or y}{1 or 2}

                l11_x1, l11_x2 = loop_list_1[0][0][1], loop_list_2[0][0][1]
                l11_y1, l11_y2 = loop_list_1[0][0][0], loop_list_2[0][0][0]

                # Get the difference in x-axis of the loop singularity
                loop_diff_x = l11_x1 - l11_x2
                
                # Update the images if the difference in x-axis is greater than 100
                if np.abs(loop_diff_x) > 100:

                    img1, img2 = get_updated_imgs(img1, img2, loop_diff_x)
                    loop_list_1, angles_1, rel_1 = get_loop_list_angles_rel_img(img1, W)
                    loop_list_2, _, _ = get_loop_list_angles_rel_img(img2, W)

                tx = l11_x1 - l11_x2
                ty = l11_y1 - l11_y2

            # Arch has no loop singularity
            elif img_type == "arch":

                # Get center of a fingerprint image
                blob_center_x_1, blob_center_y_1 = get_center_of_image(img1)
                blob_center_x_2, blob_center_y_2 = get_center_of_image(img2)

                smooth_angles_img1, angles_1, rel_1 = calculate_angles(
                    img1, W, smooth=True
                )

                # translate values
                tx = blob_center_x_1 - blob_center_x_2
                ty = blob_center_y_1 - blob_center_y_2

            # Checking the image type

            if img_type == "loop":
                transformed_img2, similarity_score_df = get_loop_sim_score_df(
                    W, img2, angles_1, rel_1, tx, ty, loop_list_1
                )

            elif img_type == "whorl":
                transformed_img2, similarity_score_df = get_whorl_sim_score_df(
                    W, img2, angles_1, rel_1, tx, ty, loop_list_1
                )

            elif img_type == "arch":
                transformed_img2, similarity_score_df = get_arch_sim_score_df(
                    W, img2, angles_1, rel_1, tx, ty
                )
            
            else:
                raise ValueError(f"Invalid image type: {img_type}")

            max_sim_score = similarity_score_df[
                    similarity_score_df['similarity_score'] == similarity_score_df['similarity_score'].max()]

            # Apply the translation and rotation values on the transformed image2
            img2_t = translate(transformed_img2, int(max_sim_score['tx']), int(max_sim_score['ty']))
            img2_t_r = rotate(img2_t, int(max_sim_score['rotation_angle']), img_center_2)

            # Find out the highest similarity score
            max_sim_score = similarity_score_df[
                similarity_score_df['similarity_score'] == similarity_score_df['similarity_score'].max()]

            # Apply the translation and rotation values on the transformed image2
            img2_t = translate(transformed_img2, int(max_sim_score['tx']), int(max_sim_score['ty']))
            img2_t_r = rotate(img2_t, int(max_sim_score['rotation_angle']), img_center_2)

            # Save the overlapped image
            overlapped_img = cv2.addWeighted(img1, 0.5, img2_t_r, 0.5, 0.0)
            cv2.imwrite(overlapped_path / f"{i}_overlapped.png", overlapped_img)

            img1_transformed_cropped = get_overlapped_image(img2_t_r, img1)
            img2_transformed_cropped = get_overlapped_image(img1, img2_t_r)

            img1_save_path = overlapped_path / f"{i}_1_cropped.png"
            img2_save_path = overlapped_path / f"{i}_2_cropped.png"

            cv2.imwrite(img1_save_path, img1_transformed_cropped)
            cv2.imwrite(img2_save_path, img2_transformed_cropped)

            # TODO:  Convert the images to 500 dpi
        except Exception:
            continue
        
