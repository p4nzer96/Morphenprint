import fi_orientation
import fi_segmentation
import fi_singularity

def get_loop_list_angles_rel_img(img, block_size):
    smooth_angles_img, angles_img, rel_img = fi_orientation.calculate_angles(img, block_size, smoth=True)
    _, _, mask = fi_segmentation.create_segmented_and_variance_images(img, block_size, 0.2)
    _, _, loop_list, _, _ = fi_singularity.calculate_singularities(img, smooth_angles_img, 1, block_size, mask)

    return loop_list, angles_img, rel_img