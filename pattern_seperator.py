import sys
import cv2
import traceback
import shutil
import segmentator
import tools.data_preprocessing.singularity_extractor as singularity_extractor

from tqdm import tqdm
from pathlib import Path
from alignment import orientation


def pattern_separator(block_size, input_directory, output_loop_directory,
                      output_whorl_directory, output_arch_directory):
    """
    This function separates the fingerprint images into loop, whorl and arch types

    Args:
        block_size: The block size
        input_directory: The input directory
        output_loop_directory: The output loop directory
        output_whorl_directory: The output whorl directory
        output_arch_directory: The output arch directory

    Returns:
        None
    """

    for file in tqdm(input_directory.iterdir()):
        try:
            if file.suffix in [".png", ".jpg"]:
                # Getting the full path of the fingerprint image
                src = file.absolute()
                
                img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)

                # Computing the angles of the fingerprint image
                smooth_angles_img, _, _ = orientation.calculate_angles(
                    img, block_size, smooth=True)
                
                # Getting the ROI mask
                _, _, mask = segmentator.create_segmented_and_variance_images(
                    img, block_size, threshold=0.2)
                
                # Getting the basic pattern of the fingerprint image
                _, _, loop_list, delta_list, whorl_list = singularity_extractor.calculate_singularities(
                    img, smooth_angles_img, 1, block_size, mask)
                
                # Getting the type of the basic pattern
                img_type = singularity_extractor.get_pattern_type(
                    loop_list, 
                    delta_list, 
                    whorl_list)
                
                # Copying the fingerprint image to the respective directory
                print(img_type)
                if img_type == 'whorl':
                    dst = (output_whorl_directory / file.name).absolute()
                elif img_type == 'loop':
                    dst = (output_loop_directory / file.name).absolute()
                elif img_type == 'arch':
                    dst = (output_arch_directory / file.name).absolute()
                else:
                    continue
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(str(src), str(dst))

        except Exception:
            traceback.print_exc()


def main_bk():
    input_directory_arg = Path(sys.argv[1])
    output_whorl_directory_arg = Path(sys.argv[2])
    output_loop_directory_arg = Path(sys.argv[3])
    output_arch_directory_arg = Path(sys.argv[4])
    block_size = 16

    pattern_separator(block_size, input_directory_arg, output_loop_directory_arg, output_whorl_directory_arg,
                      output_arch_directory_arg)
    
def main():
    input_directory_arg = Path("./test/")
    output_whorl_directory_arg = Path("./patterns/whorl")
    output_loop_directory_arg = Path("./patterns/loop")
    output_arch_directory_arg = Path("./patterns/arch")
    block_size = 16

    pattern_separator(block_size, input_directory_arg, output_loop_directory_arg, output_whorl_directory_arg,
                      output_arch_directory_arg)
    
if __name__ == "__main__":
    main()