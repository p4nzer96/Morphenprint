import numpy as np
from scripts import similarity
import traceback
import pandas as pd

from transform import rotate
from transform import translate
from alignment import orientation

def get_best_arch_fi_alignment_config(img2, block_size, angles_img1, rel_img1, sim_score_arch_df):
    """
    Get the best arch fingerprint alignment configuration
    Args: 
        img2: The second fingerprint image
        block_size: The block size
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image

    Returns:
        sim_score_arch_df: The similarity score dataframe
    """

    # Get the center of the images
    img2_h_center, img2_w_center = img2.shape[1] // 2, img2.shape[0] // 2
    # Loop through the translation values
    for value in np.arange(-5, 6, 1):
        img2_t = translate(img2, value, value)
        # Loop through the rotation angles
        for angle in np.arange(-30, 31, 1):
            try:
                # Rotate the image
                img2_t_r = rotate(img2_t, angle, (img2_w_center, img2_h_center))
                # Calculate the angles and reliability of the rotated image
                _, angles_img2_t_r, rel_img2_t_r = orientation.calculate_angles(img2_t_r, block_size, smooth=True)
                # Calculate the similarity score
                similarity_score = similarity.calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                # Append the similarity score to the dataframe
                sim_score_arch_df = sim_score_arch_df.append({'rotation_angle': angle,
                                                              'tx': value,
                                                              'ty': value,
                                                              'similarity_score': similarity_score},
                                                             ignore_index=True)
            except Exception:
                continue

    return sim_score_arch_df


def get_arch_fi_sim_score_df(block_size, img2, angles_img1, rel_img1, tx_arch, ty_arch):
    """
    Get the similarity score dataframe for arch alignment

    Args:
        block_size: The block size
        img2: The second fingerprint image
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image
        tx_arch: The translation in x direction
        ty_arch: The translation in y direction

    Returns:
        img2_t: The aligned fingerprint image
        sim_score_arch_df: The similarity score dataframe
    """
    try:
        sim_score_arch_df = pd.DataFrame()

        # Translate the image
        img2_t = translate(img2, tx_arch, ty_arch)

        # Get the best alignment configuration
        sim_score_arch_df = get_best_arch_fi_alignment_config(img2_t, block_size, angles_img1, rel_img1, sim_score_arch_df)
    
    except Exception as e:
        print('Error in arch alignment -' + str(e))
        traceback.print_exc()

    return img2_t, sim_score_arch_df