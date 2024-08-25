import csv

import numpy as np
import pandas as pd

from PIL import Image
from pathlib import Path
from multiprocessing import Process
from mindtct.minutiae_extractor import mindtct_runner
from pattern_seperator import pattern_separator


def create_dataset_structure(root_folder: Path, output_folder: Path):
    """
    Create the folder structure for the dataset by copying and converting images
    from the root folder to the output folder.

    Args:
        root_folder (Path): The root folder containing the dataset subfolders.
        output_folder (Path): The output folder where the new structure will be created.
    """
    # Define the subfolders to process within the root folder
    subfolders = [
        root_folder / folder_name
        for folder_name in [
            "Dermalog_Consensual",
            "Dermalog_ScreenSpoof",
            "GreenBit_Consensual",
            "GreenBit_ScreenSpoof",
        ]
    ]

    for ds_folder in subfolders:
        # Create corresponding folder in the output directory
        target_folder = output_folder / ds_folder.name
        target_folder.mkdir(exist_ok=True, parents=True)

        # Iterate through all files in the subfolder
        for file_path in ds_folder.rglob("*"):
            relative_path = file_path.relative_to(ds_folder)
            target_file_path = target_folder / relative_path

            try:
                if file_path.is_dir():
                    # Create directories as needed in the target location
                    target_file_path.mkdir(exist_ok=True, parents=True)
                elif file_path.suffix.lower() in [".jpg", ".jpeg", ".bmp", ".png"]:
                    # Convert images to grayscale and save as .jpg in the target location
                    output_image_path = target_file_path.with_suffix(".jpg")
                    if not output_image_path.exists():
                        image = Image.open(file_path).convert("L")
                        image.save(output_image_path)
                else:
                    # Skip non-image files
                    continue
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue


def main():

    # Define the worker functions to process the dataset subfolders

    def worker_1():
        out_folder_name = "./LivDet-2021-Dataset/Dermalog_Consensual"
        pattern_separator(
            input_directory=Path(out_folder_name),
            output_file=Path(out_folder_name) / "pattern.csv",
            W=16,
        )

    def worker_2():
        out_folder_name = "./LivDet-2021-Dataset/Dermalog_ScreenSpoof"
        pattern_separator(
            input_directory=Path(out_folder_name),
            output_file=Path(out_folder_name) / "pattern.csv",
            W=16,
        )

    def worker_3():
        out_folder_name = "./LivDet-2021-Dataset/GreenBit_Consensual"
        pattern_separator(
            input_directory=Path(out_folder_name),
            output_file=Path(out_folder_name) / "pattern.csv",
            W=16,
        )

    def worker_4():
        out_folder_name = "./LivDet-2021-Dataset/GreenBit_ScreenSpoof"
        pattern_separator(
            input_directory=Path(out_folder_name),
            output_file=Path(out_folder_name) / "pattern.csv",
            W=16,
        )

    in_folder_name = "./livdet2021test"
    out_folder_name = "./LivDet-2021-Dataset"

    create_dataset_structure(
        root_folder=Path(in_folder_name), output_folder=Path(out_folder_name)
    )
    mindtct_runner(data_folder=Path(out_folder_name))

    p1 = Process(target=worker_1)
    p1.start()
    p2 = Process(target=worker_2)
    p2.start()
    p3 = Process(target=worker_3)
    p3.start()
    p4 = Process(target=worker_4)
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()


def parse_main():
    """
    Parse the dataset and create a CSV file with the final dataset information
    """

    root_folder = Path("./LivDet-2021-Dataset").absolute()
    dataset_folders = [
        root_folder / folder
        for folder in [
            "Dermalog_Consensual",
            "Dermalog_ScreenSpoof",
            "GreenBit_Consensual",
            "GreenBit_ScreenSpoof",
        ]
    ]

    dataframe_dict = {}
    for folder in dataset_folders:
        rows = []
        pattern_file = folder / "pattern.csv"

        with open(pattern_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                path, pattern = row

                path_components = Path(path).relative_to(root_folder).parts
                sensor, acq_type = path_components[0].split("_")
                user = path_components[1]
                liveness = path_components[2]
                if liveness == "Live":
                    material = path_components[3]
                    acq_number = np.nan
                else:
                    material = np.nan
                    acq_number = path_components[3]
                finger = path_components[4][:-4]
                rows.append(
                    [
                        path,
                        sensor,
                        acq_type,
                        user,
                        liveness,
                        material,
                        acq_number,
                        finger,
                        pattern,
                    ]
                )
                columns = [
                    "Path",
                    "Sensor",
                    "Acq_Type",
                    "User",
                    "Liveness",
                    "Material",
                    "Acq_Number",
                    "Finger",
                    "Pattern",
                ]
            dataframe_dict[folder.name] = pd.DataFrame(rows, columns=columns)

        final_dataframe = pd.concat(dataframe_dict.values(), ignore_index=True)
        final_dataframe.to_csv(root_folder / "./final_dataset_info.csv", index=False)


if __name__ == "__main__":
    #main()
    parse_main()
