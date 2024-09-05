from pathlib import Path

import cv2

from mindtct.minutiae_extractor import mindtct_runner

current_folder = Path(__file__).parent
aligned_folder = current_folder / "aligned_images"

# Flags to run the different steps of the pipeline

create_base_ds = False  # Creating the base dataset structure (convert images to .jpg and pattern extraction)
run_base_me = False  # Running the minutiae extraction on the base dataset
creating_combinations = False  # Creating the combinations of images to align
run_align = False  # Running the alignment of the images
run_second_me = False  # Running the minutiae extraction on the aligned images

# TODO: Add the code to run the different steps of the pipeline

# Run mindtct on the base dataset

files = [x.absolute() for x in aligned_folder.rglob("*.jpg") if "cropped" in str(x) or "aligned" in str(x)]

mindtct_runner(files, multiprocess=True)