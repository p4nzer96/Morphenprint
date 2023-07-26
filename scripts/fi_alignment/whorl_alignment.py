import cv2
import numpy as np
import fi_orientation
import similarity
import translation
import rotation
import pandas as pd
import fi_alignment_config
import traceback


def split_list_into_halves(input_list):
    middle = len(input_list) // 2
    first_half = input_list[:middle + len(input_list) % 2]
    second_half = input_list[middle + len(input_list) % 2:]
    return first_half, second_half

def get_first_second_part_of_loop_list(loop_list):
    loop_fh = []
    loop_sh = []
    try:
        if (len(loop_list) == 3):
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
                if (np.abs(loop_list[0][0][0] - loop_list[1][0][0]) == 16):
                    loop_fh.append(loop_list[1])
                elif (np.abs(loop_list[1][0][0] - loop_list[2][0][0]) == 16):
                    loop_sh.append(loop_list[1])
            
            if len(loop_list[2]) > 2:
                loop_list_fh, loop_list_sh = split_list_into_halves(loop_list[2])
                loop_fh.append(loop_list_fh)
                loop_sh.append(loop_list_sh)
            else:
                loop_sh.append(loop_list[2])

    
        if (len(loop_list) == 2):
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
                loop_sh.append(loop_list[2])

    
        if (len(loop_list) == 1):
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
    if (loop_difference_x < 0):
        angle_value_from = -50
        angle_value_to = 1
    elif (loop_difference_x > 0):
        angle_value_from = 0
        angle_value_to = 51
    else:
        angle_value_from = 0
        angle_value_to = 1

    for angle in np.arange(angle_value_from, angle_value_to, 1):
        try:
            img2_t_r = rotation.rotate_image(img_t, angle, (img2_w_center, img2_h_center))
            img2_t_r_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, block_size)
            img2_t_r_t = translation.translate_image(img2_t_r, loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0])
            _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, block_size)
            similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
            sim_score_whorl_df = sim_score_whorl_df.append({'rotation_angle': angle, 'tx': loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], 'ty': loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0], 'similarity_score': similarity_score}, ignore_index=True)
        except:
            continue

    return sim_score_whorl_df

def get_best_whorl_fi_alignment_config(img2, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center):
    sim_score_whorl_df_final = pd.DataFrame()
    for value in np.arange(-5, 6, 1):
        img2_t = translation.translate_image(img2, value, value)
        for angle in np.arange(-5, 6, 1):
            try:
                img2_t_r = rotation.rotate_image(img2_t, angle, (img2_w_center, img2_h_center))
                _, angles_img2_t_r, rel_img2_t_r = fi_orientation.calculate_angles(img2_t_r, block_size, smoth=True)
                similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_whorl_df_final = sim_score_whorl_df_final.append({'rotation_angle': angle, 'tx': value, 'ty': value, 'similarity_score': similarity_score}, ignore_index=True)
            except:
                continue   

    return sim_score_whorl_df_final

def get_whorl_fi_sim_score_df(block_size, img2, angles_img1, rel_img1, tx_whorl, ty_whorl, loop_list_img1):
    img2_t_r_t = img2
    sim_score_whorl_df_final = pd.DataFrame()
    try:
        img2_h_center, img2_w_center = img2.shape[1]/2, img2.shape[0]/2

        img2_t = translation.translate_image(img2, tx_whorl, ty_whorl)
        img2_t_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t, block_size)

        if (len(loop_list_img1) == 4 and len(img2_t_loop_list) == 4):
           loop_difference_x = loop_list_img1[2][0][1] - img2_t_loop_list[2][0][1]
        else:
            if len(loop_list_img1) < 4:
                l1_fh, l1_sh = get_first_second_part_of_loop_list(loop_list_img1)
                l1_value = l1_sh[0][0][1]
            else:
                l1_value = loop_list_img1[2][0][1]
            
            if len(img2_t_loop_list) < 4:
                l2_fh, l2_sh = get_first_second_part_of_loop_list(img2_t_loop_list)
                l2_value = l2_sh[0][0][1]
            else:
                l2_value = img2_t_loop_list[2][0][1]

            loop_difference_x = l1_value - l2_value

        sim_score_whorl_df = get_good_rotation_translation_config(img2_t, loop_difference_x, block_size, img2_w_center, img2_h_center, angles_img1, rel_img1, loop_list_img1)
        max_whorl_sim_score = sim_score_whorl_df[sim_score_whorl_df['similarity_score']==sim_score_whorl_df['similarity_score'].max()]

        img2_t_r = rotation.rotate_image(img2_t, int(max_whorl_sim_score['rotation_angle']), (img2_w_center, img2_h_center))
        img2_t_r_t = translation.translate_image(img2_t_r, int(max_whorl_sim_score['tx']), int(max_whorl_sim_score['ty']))

        sim_score_whorl_df_final = get_best_whorl_fi_alignment_config(img2_t_r_t, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center)

    except Exception as e:
        print('Error in whorl alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_whorl_df_final
