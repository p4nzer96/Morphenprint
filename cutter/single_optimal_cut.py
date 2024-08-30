import cv2
import numpy as np
import pandas as pd
import sys
import os
import traceback
import warnings

from mindtct.mindtct_processor import get_minutiae

warnings.filterwarnings("ignore")


def get_filtered_minutae_list(minutiae_file_path, mask):
    """
    Retrieves the filtered minutiae list based on a given mask.

    Attributes:
        minutiae_file_path (str): The file path of the minutiae file.
        mask (list): The mask used for filtering the minutiae.

    Returns:
        tuple: A tuple containing the minutiae count and the filtered minutiae list.

    """

    min_dataframe = get_minutiae(minutiae_file_path)
    minutiae_count = 0
    minutiae_filtered = []
    for index, row in min_dataframe.iterrows():
        x = int(row["x_coord"])
        y = int(row["y_coord"])

        if mask[y][x] is False:
            minutiae_count += 1
            minutiae_filtered.append(index)
            
    return minutiae_count, minutiae_filtered


def get_filtered_minutae_info_of_images(
    img1, img2, img1_minutiae_path, img2_minutiae_path
):

    # Get the cropped images
    gray_img1_crop, gray_img2_crop = img1, img2
    cropped_section_img1 = gray_img1_crop == 0
    cropped_section_img2 = gray_img2_crop == 0
    minutae_count_img1, minutae_list_filtered_img1 = get_filtered_minutae_list(
        img1_minutiae_path, cropped_section_img1
    )
    minutae_count_img2, minutae_list_filtered_img2 = get_filtered_minutae_list(
        img2_minutiae_path, cropped_section_img2
    )

    return (
        minutae_count_img1,
        minutae_count_img2,
        minutae_list_filtered_img1,
        minutae_list_filtered_img2,
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
    _ = cv2.drawContours(mask, np.int32([pts]), 0, 255, -1)
    img1_1 = img1.copy()
    img2_2 = img2.copy()
    img1_2 = img1.copy()
    img2_1 = img2.copy()

    img1_1[mask == 0] = 0
    img2_2[mask > 0] = 0
    img2_1[mask == 0] = 0
    img1_2[mask > 0] = 0

    return img1_1, img2_2, img2_1, img1_2


def get_minutiae_df(
    img1_cropped, img2_cropped, img1_cropped_minutiae_path, img2_cropped_minutiae_path
):
    minutiae_df = pd.DataFrame()

    # horizontal cutline
    y1, y2 = 0, 512
    for _ in range(513):
        try:
            pt_2 = [0, y1]
            pt_3 = [512, y2]
            black_mask = np.zeros((512, 512), np.uint8)
            pts = np.array([[0, 0], pt_2, pt_3, [512, 0]])

            img1_1, img2_2, img2_1, img1_2 = get_cropped_images(
                img1_cropped, img2_cropped, black_mask, pts
            )
            (
                minutae_count_img1_1,
                minutae_count_img2_2,
                minutae_list_filtered_img1_1,
                minutae_list_filtered_img2_2,
            ) = get_filtered_minutae_info_of_images(
                img1_1, img2_2, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutae_count_img1_1 != 0 and minutae_count_img2_2 != 0:
                minutiae_df = minutiae_df.append(
                    {
                        "img1_minutae_count": minutae_count_img1_1,
                        "img2_minutae_count": minutae_count_img2_2,
                        "img1_minutae_list_filtered": minutae_list_filtered_img1_1,
                        "img2_minutae_list_filtered": minutae_list_filtered_img2_2,
                    },
                    ignore_index=True,
                )

            (
                minutae_count_img1_2,
                minutae_count_img2_1,
                minutae_list_filtered_img1_2,
                minutae_list_filtered_img2_1,
            ) = get_filtered_minutae_info_of_images(
                img1_2, img2_1, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutae_count_img1_2 != 0 and minutae_count_img2_1 != 0:
                minutiae_df = minutiae_df.append(
                    {
                        "img1_minutae_count": minutae_count_img1_2,
                        "img2_minutae_count": minutae_count_img2_1,
                        "img1_minutae_list_filtered": minutae_list_filtered_img1_2,
                        "img2_minutae_list_filtered": minutae_list_filtered_img2_1,
                    },
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
            pt_2 = [x1, 0]
            pt_3 = [x2, 512]
            black_mask = np.zeros((512, 512), np.uint8)
            pts = np.array([[0, 0], pt_2, pt_3, [0, 512]])

            img1_1, img2_2, img2_1, img1_2 = get_cropped_images(
                img2_cropped, img2_cropped, black_mask, pts
            )
            (
                minutae_count_img1_1,
                minutae_count_img2_2,
                minutae_list_filtered_img1_1,
                minutae_list_filtered_img2_2,
            ) = get_filtered_minutae_info_of_images(
                img1_1, img2_2, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutae_count_img1_1 != 0 and minutae_count_img2_2 != 0:
                minutiae_df = minutiae_df.append(
                    {
                        "img1_minutae_count": minutae_count_img1_1,
                        "img2_minutae_count": minutae_count_img2_2,
                        "img1_minutae_list_filtered": minutae_list_filtered_img1_1,
                        "img2_minutae_list_filtered": minutae_list_filtered_img2_2,
                    },
                    ignore_index=True,
                )

            (
                minutae_count_img1_2,
                minutae_count_img2_1,
                minutae_list_filtered_img1_2,
                minutae_list_filtered_img2_1,
            ) = get_filtered_minutae_info_of_images(
                img1_2, img2_1, img1_cropped_minutiae_path, img2_cropped_minutiae_path
            )
            if minutae_count_img1_2 != 0 and minutae_count_img2_1 != 0:
                minutiae_df = minutiae_df.append(
                    {
                        "img1_minutae_count": minutae_count_img1_2,
                        "img2_minutae_count": minutae_count_img2_1,
                        "img1_minutae_list_filtered": minutae_list_filtered_img1_2,
                        "img2_minutae_list_filtered": minutae_list_filtered_img2_1,
                    },
                    ignore_index=True,
                )

            x1 -= 1
            x2 -= 1
        except Exception:
            continue

    return minutiae_df

def make_single_optimal_cut(img1_cropped, img2_cropped):

    cropped_folder_df = pd.read_csv()

    for index, row in cropped_folder_df.iterrows():
        pass
        
def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    data_txt_path = sys.argv[2]
    folder_count = 0
    try:
        for root, _, files in os.walk(directory_path):
            img1_cropped_path = ""
            img2_cropped_path = ""
            img1_minutiae_path = ""
            img2_minutiae_path = ""
            img_count = 0
            img1_minutiae_count = 0
            img2_minutiae_count = 0
            for file in files:
                # consider only cropped images
                if file.lower().endswith("_cropped.png"):
                    img_count += 1
                    if img_count == 1:
                        img1_cropped_path = os.path.join(root, file)
                    if img_count == 2:
                        img2_cropped_path = os.path.join(root, file)

            if (
                img1_cropped_path
                and img2_cropped_path
                and img1_minutiae_path
                and img2_minutiae_path
            ):
                if (
                    os.path.getsize(img1_minutiae_path) == 0
                    or os.path.getsize(img2_minutiae_path) == 0
                ):
                    with open(data_txt_path, "a") as file:
                        file.write(
                            "\n"
                            + "Image Sets - "
                            + str(os.path.basename(root))
                            + ","
                            + str(os.path.basename(img1_cropped_path))
                            + ","
                            + str(os.path.basename(img2_cropped_path))
                        )
                    continue

                img1_cropped = cv2.imread(img1_cropped_path, cv2.IMREAD_GRAYSCALE)
                img2_cropped = cv2.imread(img2_cropped_path, cv2.IMREAD_GRAYSCALE)

                if str(os.path.splitext(os.path.basename(img1_cropped_path))[0]) in str(
                    os.path.basename(img1_minutiae_path)
                ) and str(
                    os.path.splitext(os.path.basename(img2_cropped_path))[0]
                ) in str(
                    os.path.basename(img2_minutiae_path)
                ):
                    img1_m_p = img1_minutiae_path
                    img2_m_p = img2_minutiae_path
                else:
                    img1_m_p = img2_minutiae_path
                    img2_m_p = img1_minutiae_path

                minutiae_df_final = get_minutiae_df(
                    img1_cropped, img2_cropped, img1_m_p, img2_m_p
                )

                try:
                    minutiae_df_final_filtered = minutiae_df_final.drop_duplicates(
                        keep="first"
                    )
                except Exception:
                    minutiae_df_final_filtered = minutiae_df_final

                minutiae_df_final_filtered["mul_value"] = (
                    minutiae_df_final_filtered["img1_minutae_count"]
                    * minutiae_df_final_filtered["img2_minutae_count"]
                )
                minutiae_df_final_filtered = minutiae_df_final_filtered.sort_values(
                    by="mul_value", ascending=False
                )

                for _, row in minutiae_df_final_filtered.iterrows():
                    img1_minutiae_count = row["img1_minutae_count"]
                    img2_minutiae_count = row["img2_minutae_count"]

                    if img1_minutiae_count > 12 and img2_minutiae_count > 12:
                        break
                    else:
                        img1_minutiae_count = 0
                        img2_minutiae_count = 0
                        continue

                if img1_minutiae_count == 0 and img2_minutiae_count == 0:
                    img1_minutiae_count = minutiae_df_final_filtered.iloc[0][
                        "img1_minutae_count"
                    ]
                    img2_minutiae_count = minutiae_df_final_filtered.iloc[0][
                        "img2_minutae_count"
                    ]

                selected_minutiae_df = minutiae_df_final_filtered[
                    (
                        minutiae_df_final_filtered["img1_minutae_count"]
                        == img1_minutiae_count
                    )
                    & (
                        minutiae_df_final_filtered["img2_minutae_count"]
                        == img2_minutiae_count
                    )
                ]
                img1_minutae_list_filtered = selected_minutiae_df[
                    "img1_minutae_list_filtered"
                ].iloc[0]
                img2_minutae_list_filtered = selected_minutiae_df[
                    "img2_minutae_list_filtered"
                ].iloc[0]

                img1_minutae_list_filtered = img1_minutae_list_filtered.split("\n")
                img2_minutae_list_filtered = img2_minutae_list_filtered.split("\n")

                morphed_minutiae_save_path = (
                    root
                    + "/"
                    + str(os.path.splitext(os.path.basename(img1_cropped_path))[0])
                    + "_"
                    + str(os.path.splitext(os.path.basename(img2_cropped_path))[0])
                    + "_mm.txt"
                )

                with open(morphed_minutiae_save_path, "w") as file:
                    for line in img1_minutae_list_filtered:
                        try:
                            if line.strip():
                                file.write(f"{line}\n")
                        except Exception:
                            continue

                    for line in img2_minutae_list_filtered:
                        try:
                            if line.strip():
                                file.write(f"{line}\n")
                        except Exception:
                            continue

            folder_count = folder_count + 1
            print("Folder count - " + str(folder_count))

    except Exception as e:
        print(
            "Error -"
            + os.path.basename(root)
            + ","
            + os.path.basename(img1_cropped_path)
            + ","
            + os.path.basename(img2_cropped_path)
            + "-"
            + str(e)
        )
        traceback.print_exc()


if __name__ == "__main__":
    main()
