import traceback

import numpy as np
import pandas as pd

from transform import rotate, translate
from alignment.orientation import calculate_angles
from alignment.similarity import calculate_similarity

def get_best_arch_align(img2, W, angles_img1, rel_img1):
    """
    Get the best arch fingerprint alignment configuration
    Args: 
        img2: The second fingerprint image
        W: The block size
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image

    Returns:
        sim_score_arch_df: The similarity score dataframe
    """

    # Initialize the variables
    start_t, end_t, t_step = -5, 5, 1  # The translation values
    start_angle, end_angle, angle_step = -30, 30, 1  # The rotation angles
    sim_score_arch_df = pd.DataFrame()

    # Get the center of the images
    img2_center = img2.shape[1] // 2, img2.shape[0] // 2
    # Loop through the translation values
    for value in np.arange(start_t, end_t + 1, t_step):
        img2_t = translate(img2, value, value)
        # Loop through the rotation angles
        for angle in np.arange(start_angle, end_angle + 1, angle_step):
            try:
                # Rotate the image
                img2_t_r = rotate(img2_t, angle, img2_center)
                # Calculate the angles and reliability of the rotated image
                _, angles_img2_t_r, rel_img2_t_r = calculate_angles(img2_t_r, W, smooth=True)
                # Calculate the similarity score
                similarity_score = calculate_similarity(angles_img1, angles_img2_t_r, rel_img1, rel_img2_t_r)
                # Append the similarity score to the dataframe
                sim_score_arch_df = sim_score_arch_df.append({'rotation_angle': angle,
                                                              'tx': value,
                                                              'ty': value,
                                                              'similarity_score': similarity_score},
                                                             ignore_index=True)
            except Exception:
                continue

    return sim_score_arch_df


def get_arch_fi_sim_score_df(img2, W, angles_img1, rel_img1, tx_arch, ty_arch):
    """
    Get the similarity score dataframe for arch alignment

    Args:
        img2: The second fingerprint image
        W: The block size
        angles_img1: The angles image of the first fingerprint image
        rel_img1: The reliability image of the first fingerprint image
        tx_arch: The translation in x direction
        ty_arch: The translation in y direction

    Returns:
        img2_t: The aligned fingerprint image
        sim_score_arch_df: The similarity score dataframe
    """
    try:

        # Translate the image
        img2_t = translate(img2, tx_arch, ty_arch)

        # Get the best alignment configuration
        sim_score_arch_df = get_best_arch_align(img2_t, W, angles_img1, rel_img1)
    
    except Exception as e:
        print('Error in arch alignment -' + str(e))
        traceback.print_exc()

    return img2_t, sim_score_arch_df