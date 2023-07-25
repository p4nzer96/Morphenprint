import cv2
import numpy as np
import fi_orientation
import similarity
import translation
import rotation
import fi_alignment_config
import traceback
import pandas as pd


def get_loop_good_rotation_translation_config(img_t, block_size, img2_w_center, img2_h_center, loop_list_img1, angles_img1, rel_img1):
    sim_score_loop_df = pd.DataFrame()
    for angle in np.arange(-50, 51, 1):
        try:
            img2_t_r = rotation.rotate_image(img_t, angle, (img2_w_center, img2_h_center))
            img2_t_r_loop_list, _, _ = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r, block_size)
            img2_t_r_t = translation.translate_image(img2_t_r, loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0])
            _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, block_size)
            similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
            sim_score_loop_df = sim_score_loop_df.append({'rotation_angle': angle, 'tx': loop_list_img1[0][0][1] - img2_t_r_loop_list[0][0][1], 'ty': loop_list_img1[0][0][0] - img2_t_r_loop_list[0][0][0], 'similarity_score': similarity_score}, ignore_index=True)
        except:
            continue

    return sim_score_loop_df


def get_best_loop_fi_alignment_config(img2, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center):
    sim_score_loop_df_final = pd.DataFrame()
    for value in np.arange(-5, 6, 1):
        img2_t = translation.translate_image(img2, value, value)
        for angle in np.arange(-5, 6, 1):
            try:
                img2_t_r = rotation.rotate_image(img2_t, angle, (img2_w_center, img2_h_center))
                _, angles_img2_t_r, rel_img2_t_r = fi_orientation.calculate_angles(img2_t_r, block_size, smoth=True)
                similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_loop_df_final = sim_score_loop_df_final.append({'rotation_angle': angle, 'tx': value, 'ty': value, 'similarity_score': similarity_score}, ignore_index=True)
            except:
                continue

    return sim_score_loop_df_final


def get_loop_fi_sim_score_df(block_size, img2, angles_img1, rel_img1, tx_loop, ty_loop, loop_list_img1):
    img2_t_r_t = img2
    sim_score_loop_df_final = pd.DataFrame()
    try:
        img2_h_center, img2_w_center = img2.shape[0]/2, img2.shape[1]/2

        img2_t = translation.translate_image(img2, tx_loop, ty_loop)
        sim_score_loop_df = get_loop_good_rotation_translation_config(img2_t, block_size, img2_w_center, img2_h_center, loop_list_img1, angles_img1, rel_img1)
        max_loop_sim_score = sim_score_loop_df[sim_score_loop_df['similarity_score'] == sim_score_loop_df['similarity_score'].max()]
        img2_t_r = rotation.rotate_image(img2_t, int(max_loop_sim_score['rotation_angle']), (img2_w_center, img2_h_center))
        img2_t_r_t = translation.translate_image(img2_t_r, int(max_loop_sim_score['tx']), int(max_loop_sim_score['ty']))

        sim_score_loop_df_final = get_best_loop_fi_alignment_config(img2_t_r_t, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center)
    except Exception as e:
        print('Error in loop alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_loop_df_final
