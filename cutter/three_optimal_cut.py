import cv2
import numpy as np
import pandas as pd
import sys
import os
import traceback
import warnings

warnings.filterwarnings("ignore")


def get_fi_blob(image):
    gray_img_1 = image
    gray_img_1 = 255 - gray_img_1
    gray_img_1[gray_img_1 > 100] = 255
    gray_img_1[gray_img_1 <= 100] = 0

    kernel = np.ones((30, 30), np.uint8)
    closing = cv2.morphologyEx(gray_img_1, cv2.MORPH_CLOSE, kernel)

    return closing


def get_row_index(image_blob):
    first_row_with_255 = None
    last_row_with_255 = None

    for row in range(len(image_blob)):
        if 255 in image_blob[row]:
            if first_row_with_255 is None:
                first_row_with_255 = row
            last_row_with_255 = row

    return first_row_with_255, last_row_with_255


def get_col_index(image_blob):
    first_column_with_255 = None
    last_column_with_255 = None

    for col in range(len(image_blob[0])):
        for row in range(len(image_blob)):
            if image_blob[row][col] == 255:
                if first_column_with_255 is None:
                    first_column_with_255 = col
                last_column_with_255 = col
                break

    return first_column_with_255, last_column_with_255


def cal_row_col_mid(first_row, last_row, first_column, last_column):
    top_h = [(first_column + last_column) / 2, first_row]
    bottom_h = [(first_column + last_column) / 2, last_row]

    left_h = [first_column, (first_row + last_row) / 2]
    right_h = [last_column, (first_row + last_row) / 2]

    center = [(first_column + last_column) / 2, (first_row + last_row) / 2]

    return center, top_h, bottom_h, left_h, right_h


def get_row_col_second_mid(first_row, last_row, first_column, last_column, top_h, bottom_h, left_h, right_h):
    top_l_h = [(first_column + top_h[0]) / 2, first_row]
    top_r_h = [(last_column + top_h[0]) / 2, first_row]

    bottom_l_h = [(first_column + bottom_h[0]) / 2, last_row]
    bottom_r_h = [(last_column + bottom_h[0]) / 2, last_row]

    left_t_h = [first_column, (first_row + left_h[1]) / 2]
    left_b_h = [first_column, (last_row + left_h[1]) / 2]

    right_t_h = [last_column, (first_row + right_h[1]) / 2]
    right_b_h = [last_column, (last_row + right_h[1]) / 2]

    return top_l_h, top_r_h, bottom_l_h, bottom_r_h, left_t_h, left_b_h, right_t_h, right_b_h


def get_filtered_minutae_list(minutae_file_path, mask):
    read_file = open(minutae_file_path, 'r')
    minutae_list_filtered = ''
    minutae_count = 0
    for line in read_file:
        try:
            minutae_list = line.replace('{', '')
            minutae_list = minutae_list.split(", ")
            x = int(minutae_list[0].split('=')[1])
            y = int(minutae_list[1].split('=')[1])

            if not mask[y][x]:
                minutae_list_filtered = str(minutae_list_filtered) + str(line)
                minutae_count = minutae_count + 1
        except Exception:
            continue

    return minutae_count, minutae_list_filtered


def get_filtered_minutae_info_of_images(img1, img2, img3, img1_minutiae_path, img2_minutiae_path, img3_minutiae_path):
    gray_img1_crop = img1
    gray_img2_crop = img2
    gray_img3_crop = img3
    cropped_section_img1 = gray_img1_crop == 0
    cropped_section_img2 = gray_img2_crop == 0
    cropped_section_img3 = gray_img3_crop == 0
    minutae_count_img1, minutae_list_filtered_img1 = get_filtered_minutae_list(img1_minutiae_path, cropped_section_img1)
    minutae_count_img2, minutae_list_filtered_img2 = get_filtered_minutae_list(img2_minutiae_path, cropped_section_img2)
    minutae_count_img3, minutae_list_filtered_img3 = get_filtered_minutae_list(img3_minutiae_path, cropped_section_img3)

    return minutae_count_img1, minutae_count_img2, minutae_count_img3, minutae_list_filtered_img1, minutae_list_filtered_img2, minutae_list_filtered_img3


def get_cropped_image(image, mask, pts):
    _ = cv2.drawContours(mask, np.int32([pts]), 0, 255, -1)
    img1_1 = image.copy()
    img1_1[mask == 0] = 0

    return img1_1


def get_minutiae_df(img1, img2, img3, img1_m_p, img2_m_p, img3_m_p, points1, points2, points3):
    minutae_df = pd.DataFrame()
    img1_1 = get_cropped_image(img1, np.zeros((512, 512), np.uint8), points1)
    img2_1 = get_cropped_image(img2, np.zeros((512, 512), np.uint8), points2)
    img3_1 = get_cropped_image(img3, np.zeros((512, 512), np.uint8), points3)
    minutae_count_img1_1, minutae_count_img2_1, minutae_count_img3_1, minutae_list_filtered_img1_1, minutae_list_filtered_img2_1, minutae_list_filtered_img3_1 = get_filtered_minutae_info_of_images(
        img1_1, img2_1, img3_1, img1_m_p, img2_m_p, img3_m_p)
    if minutae_count_img1_1 != 0 and minutae_count_img2_1 != 0 and minutae_count_img3_1 != 0:
        minutae_df = minutae_df.append(
            {'img1_minutae_count': minutae_count_img1_1, 'img2_minutae_count': minutae_count_img2_1,
             'img3_minutae_count': minutae_count_img3_1, 'img1_minutae_list_filtered': minutae_list_filtered_img1_1,
             'img2_minutae_list_filtered': minutae_list_filtered_img2_1,
             'img3_minutae_list_filtered': minutae_list_filtered_img3_1}, ignore_index=True)

    img1_2 = get_cropped_image(img1, np.zeros((512, 512), np.uint8), points3)
    img2_2 = get_cropped_image(img2, np.zeros((512, 512), np.uint8), points1)
    img3_2 = get_cropped_image(img3, np.zeros((512, 512), np.uint8), points2)
    minutae_count_img1_2, minutae_count_img2_2, minutae_count_img3_2, minutae_list_filtered_img1_2, minutae_list_filtered_img2_2, minutae_list_filtered_img3_2 = get_filtered_minutae_info_of_images(
        img1_2, img2_2, img3_2, img1_m_p, img2_m_p, img3_m_p)
    if minutae_count_img1_2 != 0 and minutae_count_img2_2 != 0 and minutae_count_img3_2 != 0:
        minutae_df = minutae_df.append(
            {'img1_minutae_count': minutae_count_img1_2, 'img2_minutae_count': minutae_count_img2_2,
             'img3_minutae_count': minutae_count_img3_2, 'img1_minutae_list_filtered': minutae_list_filtered_img1_2,
             'img2_minutae_list_filtered': minutae_list_filtered_img2_2,
             'img3_minutae_list_filtered': minutae_list_filtered_img3_2}, ignore_index=True)

    img1_3 = get_cropped_image(img1, np.zeros((512, 512), np.uint8), points2)
    img2_3 = get_cropped_image(img2, np.zeros((512, 512), np.uint8), points3)
    img3_3 = get_cropped_image(img3, np.zeros((512, 512), np.uint8), points1)
    minutae_count_img1_3, minutae_count_img2_3, minutae_count_img3_3, minutae_list_filtered_img1_3, minutae_list_filtered_img2_3, minutae_list_filtered_img3_3 = get_filtered_minutae_info_of_images(
        img1_3, img2_3, img3_3, img1_m_p, img2_m_p, img3_m_p)
    if minutae_count_img1_3 != 0 and minutae_count_img2_3 != 0 and minutae_count_img3_3 != 0:
        minutae_df = minutae_df.append(
            {'img1_minutae_count': minutae_count_img1_3, 'img2_minutae_count': minutae_count_img2_3,
             'img3_minutae_count': minutae_count_img3_3, 'img1_minutae_list_filtered': minutae_list_filtered_img1_3,
             'img2_minutae_list_filtered': minutae_list_filtered_img2_3,
             'img3_minutae_list_filtered': minutae_list_filtered_img3_3}, ignore_index=True)

    return minutae_df


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    data_txt_path = sys.argv[2]
    folder_count = 0
    try:
        for root, _, files in os.walk(directory_path):
            img1_cropped_path = ''
            img2_cropped_path = ''
            img3_cropped_path = ''
            img1_minutiae_path = ''
            img2_minutiae_path = ''
            img3_minutiae_path = ''
            img_count = 0
            txt_count = 0
            img1_minutiae_count = 0
            img2_minutiae_count = 0
            img3_minutiae_count = 0
            for file in files:
                # consider only cropped images
                if file.lower().endswith('_cropped.png'):
                    img_count = img_count + 1
                    if img_count == 1:
                        img1_cropped_path = os.path.join(root, file)
                    if img_count == 2:
                        img2_cropped_path = os.path.join(root, file)
                    if img_count == 3:
                        img3_cropped_path = os.path.join(root, file)

                if file.lower().endswith('_cropped_minutiae.txt'):
                    txt_count = txt_count + 1
                    if txt_count == 1:
                        img1_minutiae_path = os.path.join(root, file)
                    if txt_count == 2:
                        img2_minutiae_path = os.path.join(root, file)
                    if txt_count == 3:
                        img3_minutiae_path = os.path.join(root, file)

            if (
                    img1_cropped_path and img2_cropped_path and img3_cropped_path and img1_minutiae_path and img2_minutiae_path and img3_minutiae_path):
                if (os.path.getsize(img1_minutiae_path) == 0 or os.path.getsize(
                        img2_minutiae_path) == 0 or os.path.getsize(img3_minutiae_path) == 0):
                    with open(data_txt_path, 'a') as file:
                        file.write('\n' + 'Image Sets - ' + str(os.path.basename(root)) + ',' + str(
                            os.path.basename(img1_cropped_path)) + ',' + str(
                            os.path.basename(img2_cropped_path)) + ',' + str(os.path.basename(img3_cropped_path)))
                    continue

                img1_cropped = cv2.imread(img1_cropped_path, 0)
                img2_cropped = cv2.imread(img2_cropped_path, 0)
                img3_cropped = cv2.imread(img3_cropped_path, 0)

                if str(os.path.splitext(os.path.basename(img1_cropped_path))[0]) in str(
                        os.path.basename(img1_minutiae_path)) and str(
                        os.path.splitext(os.path.basename(img2_cropped_path))[0]) in str(
                        os.path.basename(img2_minutiae_path)) and str(
                        os.path.splitext(os.path.basename(img3_cropped_path))[0]) in str(
                        os.path.basename(img3_minutiae_path)):
                    img1_m_p = img1_minutiae_path
                    img2_m_p = img2_minutiae_path
                    img3_m_p = img3_minutiae_path

                image_blob = get_fi_blob(img1_cropped)
                first_row, last_row = get_row_index(image_blob)
                first_column, last_column = get_col_index(image_blob)

                center, top_h, bottom_h, left_h, right_h = cal_row_col_mid(first_row, last_row, first_column,
                                                                           last_column)

                top_l_h, top_r_h, bottom_l_h, bottom_r_h, left_t_h, left_b_h, right_t_h, right_b_h = get_row_col_second_mid(
                    first_row, last_row, first_column, last_column, top_h, bottom_h, left_h, right_h)

                # points 1
                points1_1 = [[first_column, first_row], [last_column, first_row], right_t_h, center, left_t_h]
                points1_2 = [right_t_h, [last_column, last_row], bottom_h, center]
                points1_3 = [left_t_h, center, bottom_h, [first_column, last_row]]

                # points 2
                points2_1 = [[first_column, last_row], left_b_h, center, right_b_h, [last_column, last_row]]
                points2_2 = [[first_column, first_row], top_h, center, left_b_h]
                points2_3 = [top_h, [last_column, first_row], right_b_h, center]

                # points 3
                points3_1 = [[first_column, first_row], top_l_h, center, bottom_l_h, [first_column, last_row]]
                points3_2 = [top_l_h, [last_column, first_row], right_h, center]
                points3_3 = [center, right_h, [last_column, last_row], bottom_l_h]

                # points 4
                points4_1 = [top_r_h, [last_column, first_row], [last_column, last_row], bottom_r_h, center]
                points4_2 = [left_h, center, bottom_r_h, [first_column, last_row]]
                points4_3 = [[first_column, first_row], top_r_h, center, left_h]

                minutiae_df_1 = get_minutiae_df(img1_cropped, img2_cropped, img3_cropped, img1_m_p, img2_m_p, img3_m_p,
                                                points1_1, points1_2, points1_3)
                minutiae_df_2 = get_minutiae_df(img1_cropped, img2_cropped, img3_cropped, img1_m_p, img2_m_p, img3_m_p,
                                                points2_1, points2_2, points2_3)
                minutiae_df_3 = get_minutiae_df(img1_cropped, img2_cropped, img3_cropped, img1_m_p, img2_m_p, img3_m_p,
                                                points3_1, points3_2, points3_3)
                minutiae_df_4 = get_minutiae_df(img1_cropped, img2_cropped, img3_cropped, img1_m_p, img2_m_p, img3_m_p,
                                                points4_1, points4_2, points4_3)

                minutiae_df_final = pd.concat([minutiae_df_1, minutiae_df_2, minutiae_df_3, minutiae_df_4], axis=0,
                                              ignore_index=True)

                minutiae_df_final_filtered = minutiae_df_final

                minutiae_df_final_filtered['mul_value'] = minutiae_df_final_filtered['img1_minutae_count'] * \
                                                          minutiae_df_final_filtered['img2_minutae_count'] * \
                                                          minutiae_df_final_filtered['img3_minutae_count']
                minutiae_df_final_filtered = minutiae_df_final_filtered.sort_values(by='mul_value', ascending=False)

                for _, row in minutiae_df_final_filtered.iterrows():
                    img1_minutiae_count = row['img1_minutae_count']
                    img2_minutiae_count = row['img2_minutae_count']
                    img3_minutiae_count = row['img3_minutae_count']

                    if img1_minutiae_count > 12 and img2_minutiae_count > 12 and img3_minutiae_count > 12:
                        break
                    else:
                        img1_minutiae_count = 0
                        img2_minutiae_count = 0
                        img3_minutiae_count = 0
                        continue

                if img1_minutiae_count == 0 and img2_minutiae_count == 0 and img3_minutiae_count == 0:
                    img1_minutiae_count = minutiae_df_final_filtered.iloc[0]['img1_minutae_count']
                    img2_minutiae_count = minutiae_df_final_filtered.iloc[0]['img2_minutae_count']
                    img3_minutiae_count = minutiae_df_final_filtered.iloc[0]['img3_minutae_count']

                selected_minutiae_df = minutiae_df_final_filtered[
                    (minutiae_df_final_filtered['img1_minutae_count'] == img1_minutiae_count) & (
                                minutiae_df_final_filtered['img2_minutae_count'] == img2_minutiae_count) & (
                                minutiae_df_final_filtered['img3_minutae_count'] == img3_minutiae_count)]
                img1_minutae_list_filtered = selected_minutiae_df['img1_minutae_list_filtered'].iloc[0]
                img2_minutae_list_filtered = selected_minutiae_df['img2_minutae_list_filtered'].iloc[0]
                img3_minutae_list_filtered = selected_minutiae_df['img3_minutae_list_filtered'].iloc[0]

                img1_minutae_list_filtered = img1_minutae_list_filtered.split('\n')
                img2_minutae_list_filtered = img2_minutae_list_filtered.split('\n')
                img3_minutae_list_filtered = img3_minutae_list_filtered.split('\n')

                morphed_minutiae_save_path = root + '/' + str(
                    os.path.splitext(os.path.basename(img1_cropped_path))[0]) + '_' + str(
                    os.path.splitext(os.path.basename(img2_cropped_path))[0]) + '_' + str(
                    os.path.splitext(os.path.basename(img3_cropped_path))[0]) + '_mm.txt'

                with open(morphed_minutiae_save_path, 'w') as file:
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

                    for line in img3_minutae_list_filtered:
                        try:
                            if line.strip():
                                file.write(f"{line}\n")
                        except Exception:
                            continue

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + os.path.basename(root) + ',' + os.path.basename(img1_cropped_path) + ',' + os.path.basename(
            img2_cropped_path) + ',' + os.path.basename(img3_cropped_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
