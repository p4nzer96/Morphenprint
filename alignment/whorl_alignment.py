import numpy as np
import pandas as pd
import fi_alignment_config
import traceback

from alignment.similarity import calculate_similarity
from alignment.orientation import calculate_angles
from alignment.utils import split_list_into_halves
from transform import translate, rotate


def get_first_second_part_of_loop_list(loop_list, W):
    
    # Get the first and second part of the loop list
    loop_fh, loop_sh = [], []
    
    try:
        if len(loop_list) == 3:
            if len(loop_list[0]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[0])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                loop_fh.append(loop_list[0])
            
            if len(loop_list[1]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[1])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                if np.abs(loop_list[0][0][0] - loop_list[1][0][0]) == W:
                    loop_fh.append(loop_list[1])
                elif np.abs(loop_list[1][0][0] - loop_list[2][0][0]) == W:
                    loop_sh.append(loop_list[1])
            
            if len(loop_list[2]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[2])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                loop_sh.append(loop_list[2])

    
        if len(loop_list) == 2:
            if len(loop_list[0]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[0])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                loop_fh.append(loop_list[0])
            
            if len(loop_list[1]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[1])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                loop_sh.append(loop_list[1])

    
        if len(loop_list) == 1:
            if len(loop_list[0]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[0])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)

    except Exception as e:
        print('Error in fetching first and second part of loop list -' + str(e))
        traceback.print_exc()

    return loop_fh, loop_sh

def get_good_whorl_align(img_t, loop_difference_x, W, img2_center, angles_img1, rel_img1, loop_list_img1):
    sim_score_whorl_df = pd.DataFrame()
    if loop_difference_x < 0:
        angle_value_from = -50
        angle_value_to = 1
    elif loop_difference_x > 0:
        angle_value_from = 0
        angle_value_to = 51
    else:
        angle_value_from = 0
        angle_value_to = 1

    for angle in np.arange(angle_value_from, angle_value_to, 1):
        try:
            img2_t_r = rotate(img_t, angle, img2_center)
            img2_t_r_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, W)
            img2_t_r_t = translate(img2_t_r, loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0])
            _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, W)
            similarity_score = calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
            sim_score_whorl_df = sim_score_whorl_df.append({'rotation_angle': angle, 
                                                            'tx': loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], 
                                                            'ty': loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0], 
                                                            'similarity_score': similarity_score}, 
                                                            ignore_index=True)
        except Exception:
            continue

    return sim_score_whorl_df

def get_best_whorl_align(img2, W, img2_center, angles_img1, rel_img1):

    # Initialize the variables
    start_t, end_t, t_step = -5, 5, 1  # The translation values
    start_angle, end_angle, angle_step = -5, 5, 1  # The rotation angles

    # Initialize the similarity score dataframe
    sim_score_whorl_df_final = pd.DataFrame()

    # Loop through the translation values
    for value in np.arange(start_t, end_t + 1, t_step):
        # Translate the image
        img2_t = translate(img2, value, value)
        # Loop through the rotation angles
        for angle in np.arange(start_angle, end_angle, angle_step):
            try:
                # Rotate the image
                img2_t_r = rotate(img2_t, angle, img2_center)
                # Calculate the angles and reliability of the rotated image
                _, angles_img2_t_r, rel_img2_t_r = calculate_angles(img2_t_r, W, smooth=True)
                # Calculate the similarity score
                similarity_score = calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_whorl_df_final = sim_score_whorl_df_final.append({'rotation_angle': angle,
                                                                            'tx': value,
                                                                            'ty': value,
                                                                            'similarity_score': similarity_score},
                    ignore_index=True)
            except Exception:
                continue   

    return sim_score_whorl_df_final

def get_whorl_sim_score_df(W, img2, angles_img1, rel_img1, tx_whorl, ty_whorl, loop_list_img1):
    """
    Get the similarity score dataframe for whorl alignment

    Args:
        W: The block size
        img2: The second fingerprint image
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image
        tx_whorl: The translation in x direction
        ty_whorl: The translation in y direction
        loop_list_img1: The loop list of the first fingerprint image

    Returns:
        img2_t_r_t: The aligned fingerprint image
        sim_score_whorl_df_final: The similarity score dataframe
    """

    # Initialize the variables
    img2_t_r_t = img2  # The aligned fingerprint image
    sim_score_whorl_df_final = pd.DataFrame()  # The similarity score dataframe
    try:

        # Get the center of the second fingerprint image
        img2_center = (img2.shape[1] // 2, img2.shape[0] // 2)

        # Translate the second fingerprint image
        img2_t = translate(img2, tx_whorl, ty_whorl)  # The translated fingerprint image
        img2_t_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t, W)  # The loop list of the translated fingerprint image

        if len(loop_list_img1) == 4 and len(img2_t_loop_list) == 4:
           loop_difference_x = loop_list_img1[2][0][1] - img2_t_loop_list[2][0][1]
        else:
            if len(loop_list_img1) < 4:
                l1_fh, l1_sh = get_first_second_part_of_loop_list(loop_list_img1, W)
                l1_value = l1_sh[0][0][1]
            else:
                l1_value = loop_list_img1[2][0][1]
            
            if len(img2_t_loop_list) < 4:
                l2_fh, l2_sh = get_first_second_part_of_loop_list(img2_t_loop_list, W)
                l2_value = l2_sh[0][0][1]
            else:
                l2_value = img2_t_loop_list[2][0][1]

            loop_difference_x = l1_value - l2_value

        sim_score_whorl_df = get_good_whorl_align(img2_t, loop_difference_x, W, img2_center, angles_img1, rel_img1, loop_list_img1)
        max_whorl_sim_score = sim_score_whorl_df[sim_score_whorl_df['similarity_score'] == sim_score_whorl_df['similarity_score'].max()]

        img2_t_r = rotate(img2_t, int(max_whorl_sim_score['rotation_angle']), img2_center)
        img2_t_r_t = translate(img2_t_r, int(max_whorl_sim_score['tx']), int(max_whorl_sim_score['ty']))

        sim_score_whorl_df_final = get_best_whorl_align(img2_t_r_t, W, img2_center, angles_img1, rel_img1)

    except Exception as e:
        print('Error in whorl alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_whorl_df_final
