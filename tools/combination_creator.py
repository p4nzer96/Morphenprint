import os
import itertools
import shutil
import traceback
import sys


def find_fingerprint_combinations(input_directory):
    """
    Find all the combinations of fingerprint images

    Args:
        input_directory: Input directory containing the fingerprint images

    Returns:
        list: List of all the combinations of fingerprint images
    """
    files = os.listdir(input_directory)
    files = [file for file in files if file.endswith('.png')]
    file_combinations = list(itertools.combinations(files, 3))
    return file_combinations


def find_and_move_fingerprint_image(input_directory, output_directory, count, combination):
    # Create the folder
    folder_path = os.path.join(output_directory, 'image_set_' + str(count))
    os.makedirs(folder_path, exist_ok=True)
    # Find the image file
    for filename in combination:
        # Move the image file to the folder
        try:
            src = os.path.join(input_directory, filename)
            dst = os.path.join(folder_path, filename)
            shutil.copy(src, dst)
        except Exception:
            print('Error in moving the file')
            traceback.print_exc()


def main():
    # Getting command-line arguments
    input_directory_arg = sys.argv[1]
    output_directory_arg = sys.argv[2]
    combinations = find_fingerprint_combinations(input_directory_arg)
    print(len(combinations))

    for count, combination in enumerate(combinations):
        find_and_move_fingerprint_image(
            input_directory_arg, output_directory_arg, count, combination)


if __name__ == '__main__':
    main()
