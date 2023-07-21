import sys
import os
import cv2
from tqdm import tqdm
import traceback
import shutil
import fi_orientation
import fi_segmentation
import fi_singularity


def separate_fi_based_on_type_of_basic_pattern(block_size, input_directory, output_loop_directory, output_whorl_directory, output_arch_directory):
    for file in tqdm(os.listdir(input_directory)):
        try:
            if file.endswith(".png"):
                file_path = input_directory + '/' + file
                img = cv2.imread(file_path, 0)
                smooth_angles_img, _, _, _ = fi_orientation.calculate_angles(
                    img, block_size, smoth=True)
                _, _, mask = fi_segmentation.create_segmented_and_variance_images(
                    img, block_size, 0.2)
                _, _, loop_list, delta_list, whorl_list = fi_singularity.calculate_singularities(
                    img, smooth_angles_img, 1, block_size, mask)
                img_type = fi_singularity.get_type_of_basic_pattern(
                    loop_list, delta_list, whorl_list)
                src = os.path.join(input_directory, file)
                if (img_type == 'whorl'):
                    dst = os.path.join(output_whorl_directory, file)
                elif (img_type == 'loop'):
                    dst = os.path.join(output_loop_directory, file)
                elif (img_type == 'arch'):
                    dst = os.path.join(output_arch_directory, file)
                else:
                    continue
                shutil.copy(src, dst)

        except Exception as e:
            print('Error in getting fingerprints basic pattern -' + e)
            traceback.print_exc()


def main():
    input_directory_arg = sys.argv[1]
    output_whorl_directory_arg = sys.argv[2]
    output_loop_directory_arg = sys.argv[3]
    output_arch_directory_arg = sys.argv[4]
    block_size = 16

    separate_fi_based_on_type_of_basic_pattern(
        block_size, input_directory_arg, output_loop_directory_arg, output_whorl_directory_arg, output_arch_directory_arg)


if __name__ == '__main__':
    main()
