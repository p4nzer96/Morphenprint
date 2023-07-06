import os
import itertools
import shutil
import traceback
import sys

class FingerPrintImageCombination:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

    def find_fingerprint_combinations(self):
        files = os.listdir(self.input_directory)
        files = [file for file in files if file.endswith('.png')]
        file_combinations = list(itertools.combinations(files, 2))
        return file_combinations

    def find_and_move_fingerprint_image(self, count, combination):
        # Create the folder
        folder_path = os.path.join(self.output_directory, 'image_set_'+str(count))
        os.makedirs(folder_path, exist_ok=True)
        # Find the image file
        for filename in combination:
            # Move the image file to the folder
            try:
                src = os.path.join(self.input_directory, filename)
                dst = os.path.join(folder_path, filename)
                shutil.copy(src, dst)
            except:
                print('Error in moving the file')
                traceback.print_exc()

# Specify the directory path
input_directory_arg = sys.argv[1]
output_directory_arg = sys.argv[2]

# Call the function to find file combinations of length 2
fi_combination = FingerPrintImageCombination(input_directory_arg, output_directory_arg)
combinations = fi_combination.find_fingerprint_combinations()
print(len(combinations))


# Print the file combinations
for count, combination in enumerate(combinations):
    fi_combination.find_and_move_fingerprint_image(count, combination)
    #print(combination)