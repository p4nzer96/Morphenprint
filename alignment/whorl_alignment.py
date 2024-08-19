import numpy as np
import pandas as pd
import fi_alignment_config
import traceback

from scripts import similarity
from alignment import orientation
from transform import translate
from transform import rotate

def split_list_into_halves(input_list):
    """
    Split the input list into two halves

    Args:
        input_list: The input list to be split

    Returns:
        list: The first half of the input list
        list: The second half of the input list
    """
    middle = len(input_list) // 2
    first_half = input_list[:middle + len(input_list) % 2]
    second_half = input_list[middle + len(input_list) % 2:]
    return first_half, second_half

def get_first_second_part_of_loop_list(loop_list, block_size):
    
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
                if np.abs(loop_list[0][0][0] - loop_list[1][0][0]) == block_size:
                    loop_fh.append(loop_list[1])
                elif np.abs(loop_list[1][0][0] - loop_list[2][0][0]) == block_size:
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

def get_good_rotation_translation_config(img_t, loop_difference_x, block_size, img2_w_center, img2_h_center, angles_img1, rel_img1, loop_list_img1):
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
            img2_t_r = rotate(img_t, angle, (img2_w_center, img2_h_center))
            img2_t_r_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, block_size)
            img2_t_r_t = translate(img2_t_r, loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0])
            _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, block_size)
            similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
            sim_score_whorl_df = sim_score_whorl_df.append({'rotation_angle': angle, 
                                                            'tx': loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], 
                                                            'ty': loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0], 
                                                            'similarity_score': similarity_score}, 
                                                            ignore_index=True)
        except Exception:
            continue

    return sim_score_whorl_df

def get_best_whorl_fi_alignment_config(img2, block_size, img2_w_center, img2_h_center, angles_img1, rel_img1):
    sim_score_whorl_df_final = pd.DataFrame()
    for value in np.arange(-5, 6, 1):
        img2_t = translate(img2, value, value)
        for angle in np.arange(-5, 6, 1):
            try:
                img2_t_r = rotate(img2_t, angle, (img2_w_center, img2_h_center))
                _, angles_img2_t_r, rel_img2_t_r = orientation.calculate_angles(img2_t_r, block_size, smooth=True)
                similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_whorl_df_final = sim_score_whorl_df_final.append({'rotation_angle': angle, 'tx': value, 'ty': value, 'similarity_score': similarity_score}, ignore_index=True)
            except Exception:
                continue   

    return sim_score_whorl_df_final

def get_whorl_fi_sim_score_df(block_size, img2, angles_img1, rel_img1, tx_whorl, ty_whorl, loop_list_img1):
    """
    Get the similarity score dataframe for whorl alignment

    Args:
        block_size: The block size
        img2: The second fingerprint image
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image
        tx_whorl: The translation in x direction
        ty_whorl: The translation in y direction

    Returns:
        img2_t_r_t: The aligned fingerprint image
        sim_score_whorl_df_final: The similarity score dataframe
    """

    # Initialize the variables
    img2_t_r_t = img2  # The aligned fingerprint image
    sim_score_whorl_df_final = pd.DataFrame()  # The similarity score dataframe
    try:

        # Get the center of the second fingerprint image
        img2_h_center, img2_w_center = img2.shape[1] // 2, img2.shape[0] // 2

        # Translate the second fingerprint image
        img2_t = translate(img2, tx_whorl, ty_whorl)  # The translated fingerprint image
        img2_t_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t, block_size)  # The loop list of the translated fingerprint image

        if len(loop_list_img1) == 4 and len(img2_t_loop_list) == 4:
           loop_difference_x = loop_list_img1[2][0][1] - img2_t_loop_list[2][0][1]
        else:
            if len(loop_list_img1) < 4:
                l1_fh, l1_sh = get_first_second_part_of_loop_list(loop_list_img1, block_size)
                l1_value = l1_sh[0][0][1]
            else:
                l1_value = loop_list_img1[2][0][1]
            
            if len(img2_t_loop_list) < 4:
                l2_fh, l2_sh = get_first_second_part_of_loop_list(img2_t_loop_list, block_size)
                l2_value = l2_sh[0][0][1]
            else:
                l2_value = img2_t_loop_list[2][0][1]

            loop_difference_x = l1_value - l2_value

        sim_score_whorl_df = get_good_rotation_translation_config(img2_t, loop_difference_x, block_size, img2_w_center, img2_h_center, angles_img1, rel_img1, loop_list_img1)
        max_whorl_sim_score = sim_score_whorl_df[sim_score_whorl_df['similarity_score'] == sim_score_whorl_df['similarity_score'].max()]

        img2_t_r = rotate(img2_t, int(max_whorl_sim_score['rotation_angle']), (img2_w_center, img2_h_center))
        img2_t_r_t = translate(img2_t_r, int(max_whorl_sim_score['tx']), int(max_whorl_sim_score['ty']))

        sim_score_whorl_df_final = get_best_whorl_fi_alignment_config(img2_t_r_t, block_size, img2_w_center, img2_h_center, angles_img1, rel_img1)

    except Exception as e:
        print('Error in whorl alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_whorl_df_final
