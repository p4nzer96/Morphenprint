import cv2
import traceback

import pandas as pd
import segmentator
import tools.data_preprocessing.singularity_extractor as singularity_extractor

from tqdm import tqdm
from pathlib import Path
from alignment import orientation


def pattern_separator(input_directory: Path, block_size: int):
    """
    This function separates the fingerprint images into loop, whorl and arch types

    Args:
        input_directory (Path): The directory containing the fingerprint images
        block_size (int): The block size used for the orientation field calculation
    """

    type_list = []
    
    for file in tqdm(input_directory.rglob("*.*")):

        try:
            if file.suffix in [".png", ".jpg"]:
                # Getting the full path of the fingerprint image
                src = file.absolute()
                
                img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)

                # Computing the angles of the fingerprint image
                smooth_angles_img, _, _ = orientation.calculate_angles(img, block_size, smooth=True)
                
                # Getting the ROI mask
                _, _, mask = segmentator.create_segmented_and_variance_images(img, block_size, threshold=0.2)
                
                # Getting the basic pattern of the fingerprint image
                _, _, loop_list, delta_list, whorl_list = singularity_extractor.calculate_singularities(
                    img, smooth_angles_img, 1, block_size, mask)
                
                # Getting the type of the basic pattern
                img_type = singularity_extractor.get_pattern_type(
                    loop_list, 
                    delta_list, 
                    whorl_list)
                
                type_list.append([src, img_type if img_type != "none" else 'unknown'])
                

        except Exception:
            traceback.print_exc()
    
    pd.DataFrame(type_list, columns=['Path', 'Type']).to_csv("pattern_types.csv", index=False)

def main():
    input_directory_arg = Path("./LivDet2021-DS/")
    block_size = 16

    pattern_separator(block_size, input_directory_arg)
    
if __name__ == "__main__":
    main()