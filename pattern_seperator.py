import cv2
import traceback
import segmentator
import singularity_extractor

import pandas as pd

from pathlib import Path
from alignment import orientation


def pattern_separator(input_directory: Path, output_file: Path, W: int):
    """
    This function separates the fingerprint images into loop, whorl and arch types

    Args:
        input_directory (Path): The directory containing the fingerprint images
        W (int): The block size used for the orientation field calculation
        output_file (Path): The output file where the results will be saved
    """
    type_list = []
    
    for file in input_directory.rglob("*.jpg"):

        try:
            # Getting the full path of the fingerprint image
            src = file.absolute()
            
            img = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)

            # Computing the angles of the fingerprint image
            smooth_angles_img, _, _ = orientation.calculate_angles(img, W, smooth=True)
            
            # Getting the ROI mask
            _, _, mask = segmentator.create_segmented_and_variance_images(img, W, threshold=0.2)
            
            # Getting the basic pattern of the fingerprint image
            _, _, loop_list, delta_list, whorl_list = singularity_extractor.calculate_singularities(
                img, smooth_angles_img, 1, W, mask)
            
            # Getting the type of the basic pattern
            img_type = singularity_extractor.get_pattern_type(
                loop_list, 
                delta_list, 
                whorl_list)
            
            type_list.append([src, img_type if img_type != "none" else 'unknown'])
                

        except Exception:
            traceback.print_exc()
    
    pd.DataFrame(type_list, columns=['Path', 'Type']).to_csv(output_file, index=False)

def main():
    
    input_directory_arg = Path("./LivDet2021-DS/")
    W = 16

    pattern_separator(input_directory_arg, W)
    
if __name__ == "__main__":
    main()