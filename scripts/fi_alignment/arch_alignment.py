import numpy as np
import fi_orientation
import fi_center
import fi_alignment_config
import similarity
import translation
import rotation
import pandas as pd
import traceback


def get_arch_good_rotation_translation_config(img_t, block_size, img2_w_center, img2_h_center, img1_blob_center_x, img1_blob_center_y, angles_img1, rel_img1):
  sim_score_arch_df = pd.DataFrame()
  for angle in np.arange(-50, 51, 1):
    try:
      img2_t_r = rotation.rotate_image(img_t, angle, (img2_w_center, img2_h_center))
      img2_t_r_blob_center_x, img2_t_r_blob_center_y = fi_center.get_center_of_image(img2_t_r)
      img2_t_r_t = translation.translate_image(img2_t_r, img1_blob_center_x - img2_t_r_blob_center_x, img1_blob_center_y - img2_t_r_blob_center_y)
      _, angles_img2_t_r_t, rel_img2_t_r_t = fi_alignment_config.get_loop_list_angles_rel_img(img2_t_r_t, block_size)
      similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r_t, rel_img1, rel_img2_t_r_t)
      sim_score_arch_df = sim_score_arch_df.append({'rotation_angle': angle, 'tx': img1_blob_center_x - img2_t_r_blob_center_x, 'ty': img1_blob_center_y - img2_t_r_blob_center_y, 'similarity_score': similarity_score}, ignore_index=True)
    except:
      continue

  return sim_score_arch_df
                                      
def get_best_arch_fi_alignment_config(img2, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center):
    sim_score_arch_df_final = pd.DataFrame()
    for value in np.arange(-5, 6, 1):
        img2_t = translation.translate_image(img2, value, value)
        for angle in np.arange(-5, 6, 1):
            try:
                img2_t_r = rotation.rotate_image(img2_t, angle, (img2_w_center, img2_h_center))
                _, angles_img2_t_r, rel_img2_t_r = fi_orientation.calculate_angles(img2_t_r, block_size, smoth=True)
                similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                sim_score_arch_df_final = sim_score_arch_df_final.append({'rotation_angle': angle, 'tx': value, 'ty': value, 'similarity_score': similarity_score}, ignore_index=True)
            except:
                continue

    return sim_score_arch_df_final


def get_arch_fi_sim_score_df(block_size, img2, img1_blob_center_x, img1_blob_center_y, angles_img1, rel_img1, tx_arch, ty_arch):
    img2_t_r_t = img2
    sim_score_arch_df_final = pd.DataFrame()
    try:
        img2_h_center, img2_w_center = img2.shape[0]/2, img2.shape[1]/2

        img2_t = translation.translate_image(img2, tx_arch, ty_arch)
        sim_score_arch_df = get_arch_good_rotation_translation_config(img2_t, block_size, img2_w_center, img2_h_center, img1_blob_center_x, img1_blob_center_y, angles_img1, rel_img1)
        max_arch_sim_score = sim_score_arch_df[sim_score_arch_df['similarity_score'] == sim_score_arch_df['similarity_score'].max()]
        img2_t_r = rotation.rotate_image(img2_t, int(max_arch_sim_score['rotation_angle']), (img2_w_center, img2_h_center))
        img2_t_r_t = translation.translate_image(img2_t_r, int(max_arch_sim_score['tx']), int(max_arch_sim_score['ty']))
        
        sim_score_arch_df_final = get_best_arch_fi_alignment_config(img2_t_r_t, block_size, angles_img1, rel_img1, img2_w_center, img2_h_center)
    except Exception as e:
        print('Error in arch alignment -' + str(e))
        traceback.print_exc()

    return img2_t_r_t, sim_score_arch_df_final
