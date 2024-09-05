import cProfile
import pickle
import cv2
import numpy as np
import pandas as pd
import sys
import os
import traceback
import warnings

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from mindtct.mindtct_processor import get_minutiae
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore")


def get_filtered_minutiae_list(minutiae_file_path, mask):
    """
    Retrieves the filtered minutiae list based on a given mask.

    Attributes:
        minutiae_file_path (str): The file path of the minutiae file.
        mask (list): The mask used for filtering the minutiae.

    Returns:
        tuple: A tuple containing the minutiae count and the filtered minutiae list.

    """

    min_dataframe = get_minutiae(minutiae_file_path)

    # Convert the necessary columns to numpy arrays for faster processing
    x_coords = min_dataframe["x_coord"].to_numpy(dtype=int)
    y_coords = min_dataframe["y_coord"].to_numpy(dtype=int)

    # Use numpy to filter based on the mask and extract valid minutiae
    valid_mask = ~mask[y_coords, x_coords]  # Get valid points where mask is False

    # Filter the DataFrame indexes based on the valid mask
    minutiae_filtered = min_dataframe.index[valid_mask].tolist()

    # Count the valid minutiae
    minutiae_count = valid_mask.sum()

    return minutiae_count, minutiae_filtered


def get_filtered_minutiae_info_of_images(
    img1, img2, img1_minutiae_path, img2_minutiae_path
):
    # Get the cropped images
    gray_img1_crop, gray_img2_crop = img1, img2
    cropped_section_img1 = gray_img1_crop == 0
    cropped_section_img2 = gray_img2_crop == 0
    minutiae_count_img1, minutiae_list_filtered_img1 = get_filtered_minutiae_list(
        img1_minutiae_path, cropped_section_img1
    )
    minutiae_count_img2, minutiae_list_filtered_img2 = get_filtered_minutiae_list(
        img2_minutiae_path, cropped_section_img2
    )

    return (
        minutiae_count_img1,
        minutiae_count_img2,
        minutiae_list_filtered_img1,
        minutiae_list_filtered_img2,
    )


def get_cropped_images(img1, img2, mask, pts):
    """
    Get the cropped images based on the given mask and points
    Args:
        img1: The first fingerprint image.
        img2: The second fingerprint image.
        mask: The mask used for cropping the images.
        pts: The points used for cropping the images.
    """
    # Draw the contour on the mask
    cv2.drawContours(mask, np.int32([pts]), 0, 255, -1)

    # Create masked copies of img1 and img2
    img1_1 = img1 * (mask > 0)  # img1 where mask is non-zero
    img2_2 = img2 * (mask == 0)  # img2 where mask is zero
    img2_1 = img2 * (mask > 0)  # img2 where mask is non-zero
    img1_2 = img1 * (mask == 0)  # img1 where mask is zero

    return img1_1, img2_2, img2_1, img1_2


def get_minutiae_df(
    img1_cropped, img2_cropped, img1_cropped_minutiae_path, img2_cropped_minutiae_path
):
    minutiae_df = pd.DataFrame(dtype=object)

    # Horizontal cutline

    y1, y2 = 0, 512
    for _ in range(513):
        try:
            # Creating a black mask and filling with zeros
            black_mask = np.zeros((512, 512), np.uint8)

            # Defining a set of points for the mask
            # These points will be used to crop the images

            # (0, 0) -> Upper left corner
            # (0, y1) -> Left point of the cutline
            # (512, y2) -> Right point of the cutline
            # (512, 0) -> Upper right corner

            pts = np.array([[0, 0], [0, y1], [512, y2], [512, 0]])

            # Applying the mask to the images

            img1_1, img2_2, img2_1, img1_2 = get_cropped_images(
                img1_cropped, img2_cropped, black_mask, pts
            )

            # Get the filtered minutiae information

            (
                minutiae_count_img1_1,
                minutiae_count_img2_2,
                minutiae_list_filtered_img1_1,
                minutiae_list_filtered_img2_2,
            ) = get_filtered_minutiae_info_of_images(
                img1_1, img2_2, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )

            # Check if the minutiae count is not zero

            if minutiae_count_img1_1 != 0 and minutiae_count_img2_2 != 0:
                minutiae_df = pd.concat(
                    [
                        minutiae_df,
                        pd.DataFrame(
                            [
                                {
                                    "img1_minutiae_count": minutiae_count_img1_1,
                                    "img2_minutiae_count": minutiae_count_img2_2,
                                    "img1_minutiae_list_filtered": tuple(minutiae_list_filtered_img1_1),
                                    "img2_minutiae_list_filtered": tuple(minutiae_list_filtered_img2_2),
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

            # Swap the images and get the filtered minutiae information

            (
                minutiae_count_img1_2,
                minutiae_count_img2_1,
                minutiae_list_filtered_img1_2,
                minutiae_list_filtered_img2_1,
            ) = get_filtered_minutiae_info_of_images(
                img1_2, img2_1, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutiae_count_img1_2 != 0 and minutiae_count_img2_1 != 0:
                minutiae_df = pd.concat(
                    [
                        minutiae_df,
                        pd.DataFrame(
                            [
                                {
                                    "img1_minutiae_count": minutiae_count_img1_2,
                                    "img2_minutiae_count": minutiae_count_img2_1,
                                    "img1_minutiae_list_filtered": tuple(minutiae_list_filtered_img1_2),
                                    "img2_minutiae_list_filtered": tuple(minutiae_list_filtered_img2_1),
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

            y1 += 1
            y2 -= 1

        except Exception:
            continue

    # vertical cutline
    x1, x2 = 512, 0
    for _ in range(513):
        try:
            # Creating a black mask and filling with zeros
            black_mask = np.zeros((512, 512), np.uint8)

            # Defining a set of points for the mask
            # These points will be used to crop the images

            # (0, 0) -> Upper left corner
            # (x1, 0) -> Upper point of the cutline
            # (x2, 512) -> Lower point of the cutline
            # (0, 512) -> Lower left corner

            pts = np.array([[0, 0], [x1, 0], [x2, 512], [0, 512]])

            img1_1, img2_2, img2_1, img1_2 = get_cropped_images(
                img2_cropped, img2_cropped, black_mask, pts
            )

            # Getting the filtered minutiae information
            (
                minutiae_count_img1_1,
                minutiae_count_img2_2,
                minutiae_list_filtered_img1_1,
                minutiae_list_filtered_img2_2,
            ) = get_filtered_minutiae_info_of_images(
                img1_1, img2_2, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutiae_count_img1_1 != 0 and minutiae_count_img2_2 != 0:
                minutiae_df = pd.concat([minutiae_df, pd.DataFrame([
                    {
                        "img1_minutiae_count": minutiae_count_img1_1,
                        "img2_minutiae_count": minutiae_count_img2_2,
                        "img1_minutiae_list_filtered": tuple(minutiae_list_filtered_img1_1),
                        "img2_minutiae_list_filtered": tuple(minutiae_list_filtered_img2_2),
                    }])],
                    ignore_index=True,
                )

            # Swap the images and get the filtered minutiae information

            (
                minutiae_count_img1_2,
                minutiae_count_img2_1,
                minutiae_list_filtered_img1_2,
                minutiae_list_filtered_img2_1,
            ) = get_filtered_minutiae_info_of_images(
                img1_2, img2_1, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutiae_count_img1_2 != 0 and minutiae_count_img2_1 != 0:
                minutiae_df = pd.concat([minutiae_df, pd.DataFrame([
                    {
                        "img1_minutiae_count": minutiae_count_img1_2,
                        "img2_minutiae_count": minutiae_count_img2_1,
                        "img1_minutiae_list_filtered": tuple(minutiae_list_filtered_img1_2),
                        "img2_minutiae_list_filtered": tuple(minutiae_list_filtered_img2_1),
                    }])],
                    ignore_index=True,
                )

            x1 -= 1
            x2 -= 1
        except Exception:
            continue

    return minutiae_df


def make_single_optimal_cut(
    img_1_path, img_2_path, img_1_minutiae_path, img_2_minutiae_path
):
    def check_suitability(row):
        if row["img1_minutiae_count"] > 12 and row["img2_minutiae_count"] > 12:
            return row
        else:
            row["img1_minutiae_count"] = 0
            row["img2_minutiae_count"] = 0
            return row

    img1_minutiae_count = 0
    img2_minutiae_count = 0

    img1_cropped = cv2.imread(img_1_path, cv2.IMREAD_GRAYSCALE)
    img2_cropped = cv2.imread(img_2_path, cv2.IMREAD_GRAYSCALE)

    minutiae_df_final = get_minutiae_df(
        img1_cropped, img2_cropped, img_1_minutiae_path, img_2_minutiae_path
    )

    try:
        minutiae_df_final_filtered = minutiae_df_final.drop_duplicates(keep="first")
    except Exception:
        minutiae_df_final_filtered = minutiae_df_final

    # Adding a new column to the dataframe
    # This represents the product of the minutiae count of the two images
    # and will be used for sorting the dataframe

    minutiae_df_final_filtered["mul_value"] = (
        minutiae_df_final_filtered["img1_minutiae_count"]
        * minutiae_df_final_filtered["img2_minutiae_count"]
    )
    minutiae_df_final_filtered = minutiae_df_final_filtered.sort_values(
        by="mul_value", ascending=False
    )

    # Checking for a suitable minutiae pair (minutiae count > 12 for both images)

    minutiae_df_final_filtered = minutiae_df_final_filtered.apply(
        check_suitability, axis=1
    )

    # If no suitable minutiae pair is found, select the first row (fallback)

    if img1_minutiae_count == 0 and img2_minutiae_count == 0:
        img1_minutiae_count = minutiae_df_final_filtered.iloc[0]["img1_minutiae_count"]
        img2_minutiae_count = minutiae_df_final_filtered.iloc[0]["img2_minutiae_count"]

    selected_minutiae_df = minutiae_df_final_filtered[
        (minutiae_df_final_filtered["img1_minutiae_count"] == img1_minutiae_count)
        & (minutiae_df_final_filtered["img2_minutiae_count"] == img2_minutiae_count)
    ]

    img1_minutiae_list_filtered = selected_minutiae_df[
        "img1_minutiae_list_filtered"
    ].iloc[0]
    img2_minutiae_list_filtered = selected_minutiae_df[
        "img2_minutiae_list_filtered"
    ].iloc[0]

    print(f"Processing {img_1_path.stem[:-2].split('_')[1]}")

    # Processing strings
    img1_minutiae_list_filtered = [int(x) for x in img1_minutiae_list_filtered]
    img2_minutiae_list_filtered = [int(x) for x in img2_minutiae_list_filtered]

    # Getting the miunutiae_files 

    minutiae_1 = get_minutiae(img_1_minutiae_path)
    minutiae_2 = get_minutiae(img_2_minutiae_path)

    # Filtering

    minutiae_1_filtered = minutiae_1.iloc[img1_minutiae_list_filtered]
    minutiae_1_filtered.insert(0, "finger", 1)
    minutiae_2_filtered = minutiae_2.iloc[img2_minutiae_list_filtered]
    minutiae_2_filtered.insert(0, "finger", 2)

    minutiae_filtered = pd.concat([minutiae_1_filtered, minutiae_2_filtered])

    # Saving the minutiae

    minutiae_save_path = (
        img_1_path.parent / f"selected_min_{img_1_path.parent.name}.pkl"
    )

    minutiae_filtered.to_pickle(minutiae_save_path)

def make_multiple_optimal_cuts(cropped_path, multiprocessing=True):
    img_1_path = []
    img_2_path = []
    img_1_minutiae_path = []
    img_2_minutiae_path = []

    for folder in cropped_path.iterdir():
        img_1_path.append((folder / f"cropped_{folder.stem}_1.jpg").resolve())
        img_2_path.append((folder / f"cropped_{folder.stem}_2.jpg").resolve())

        # Getting the minutiae file paths

        img_1_minutiae_path.append(
            (
                folder
                / f"mindtct_cropped_{folder.name}_1"
                / f"cropped_{folder.name}_1.min"
            ).resolve()
        )
        img_2_minutiae_path.append(
            (
                folder
                / f"mindtct_cropped_{folder.name}_2"
                / f"cropped_{folder.name}_2.min"
            ).resolve()
        )

    args = list(zip(img_1_path, img_2_path, img_1_minutiae_path, img_2_minutiae_path))

    if multiprocessing:
        with Pool(processes=cpu_count()) as pool:
            pool.starmap(make_single_optimal_cut, args)

    else:
        for arg in args:
            make_single_optimal_cut(*arg)


def main():

    make_multiple_optimal_cuts(Path("./aligned_images"), multiprocessing=True)


if __name__ == "__main__":
    main()
