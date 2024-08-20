import traceback
import fi_alignment_config

import numpy as np
import pandas as pd

from alignment.similarity import calculate_similarity
from alignment.orientation import calculate_angles
from transform import rotate
from transform import translate


def get_good_loop_align(img_t, W, img2_center, loop_list_img1, angles_img1, rel_img1):
    """
    Get the good loop fingerprint alignment configuration

    Args:
        img_t: The translated image
        W: The block size
        img2_center: The center of the second fingerprint image
        loop_list_img1: The loop list of the first fingerprint image
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image

    Returns:
        sim_score_loop_df: The similarity score dataframe
    """

    # Initialize the variables
    start_angle, end_angle, angle_step = -50, 50, 1

    sim_score_loop_df = pd.DataFrame()

    # Loop through the angles
    for angle in np.arange(start_angle, end_angle + 1, angle_step):
        try:
            # Rotate the image
            img2_t_r = rotate(img_t, angle, img2_center)
            # Get the loop list, angles and reliability of the rotated image
            img2_t_r_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, W)
            # Translate the image
            img2_t_r_t = translate(img2_t_r, loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1],
                                   loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0])
            # Get the loop list, angles and reliability of the translated image
            _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, W)
            # Calculate the similarity score
            similarity_score = calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
            # Append the similarity score to the dataframe
            sim_score_loop_df = sim_score_loop_df.append({'rotation_angle': angle, 
                                                          'tx': loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], 
                                                          'ty': loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0], 
                                                          'similarity_score': similarity_score},
                                                          ignore_index=True)
        except Exception:
            continue

    return sim_score_loop_df


def get_best_loop_align(img2, W, angles_img1, rel_img1, img2_center):
    """
    Get the best loop fingerprint alignment configuration

    Args:
        img2: The second fingerprint image
        W: The block size
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image
        img2_center: The center of the second fingerprint image

    Returns:
        sim_score_loop_df_final: The similarity score dataframe
    """

    # Initialize the variables
    start_t, end_t, t_step = -5, 5, 1
    start_angle, end_angle, angle_step = -5, 5, 1
    sim_score_loop_df_final = pd.DataFrame()

    # Loop through the translation values
    for value in np.arange(start_t, end_t, t_step):
        # Translate the image
        img2_t = translate(img2, value, value)
        # Loop through the rotation angles
        for angle in np.arange(start_angle, end_angle + 1, angle_step):
            try:
                # Rotate the image
                img2_t_r = rotate(img2_t, angle, img2_center)
                _, angles_img2_t_r, rel_img2_t_r = calculate_angles(img2_t_r, W, smooth=True)
                similarity_score = calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_loop_df_final = sim_score_loop_df_final.append({'rotation_angle': angle,
                                                                          'tx': value,
                                                                          'ty': value,
                                                                          'similarity_score': similarity_score},
                                                                         ignore_index=True)
            except Exception:
                continue

    return sim_score_loop_df_final


def get_loop_fi_sim_score_df(img2, W, angles_img1, rel_img1, tx_loop, ty_loop, loop_list_img1):
    
    img2_t_r_t = img2
    sim_score_loop_df_final = pd.DataFrame()
    try:
        img2_center = (img2.shape[0] // 2, img2.shape[1] // 2)
        img2_t = translate(img2, tx_loop, ty_loop)
        sim_score_loop_df = get_good_loop_align(img2_t, W, img2_center, loop_list_img1, angles_img1, rel_img1)
        max_loop_sim_score = sim_score_loop_df[
            sim_score_loop_df['similarity_score'] == sim_score_loop_df['similarity_score'].max()]
        img2_t_r = rotate(img2_t, int(max_loop_sim_score['rotation_angle']), img2_center)
        img2_t_r_t = translate(img2_t_r, int(max_loop_sim_score['tx']), int(max_loop_sim_score['ty']))

        sim_score_loop_df_final = get_best_loop_align(img2_t_r_t, W, angles_img1, rel_img1, img2_center)
    except Exception as e:
        print('Error in loop alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_loop_df_final
