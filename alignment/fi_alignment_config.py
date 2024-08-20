from alignment import orientation
import segmentator
import tools.data_preprocessing.singularity_extractor as singularity_extractor


def get_loop_list_angles_rel_img(img, W):
    """
    Get loop list, angles and reliability image of a fingerprint image
    Args:
        img: The fingerprint image
        W: The block size

    Returns:
        loop_list: The loop list of the fingerprint image
        angles_img: The angles image of the fingerprint image
        rel_img: The reliability image of the fingerprint image
    """
    smooth_angles_img, angles_img, rel_img = orientation.calculate_angles(img, W, smooth=True)
    _, _, mask = segmentator.create_segmented_and_variance_images(img, W, 0.2)
    _, _, loop_list, _, _ = singularity_extractor.calculate_singularities(img, smooth_angles_img, 1, W, mask)

    return loop_list, angles_img, rel_img
