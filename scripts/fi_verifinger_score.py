import sys
import os
import traceback
from subprocess import check_output


def get_verifinger_score(minutia_type, epochs, morphed_fingerprint_img, fingerprint_img1, fingerprint_img2, root):
    try:
        morph_img = str(os.path.basename(morphed_fingerprint_img))
        img1 = str(os.path.basename(fingerprint_img1))
        img2 = str(os.path.basename(fingerprint_img2))
        base_folder = str(os.path.basename(root))
        morph_img1_score = ''
        morph_img2_score = ''

        # get the response
        verifinger_output = check_output(
            ['Verifinger1toN', morphed_fingerprint_img, fingerprint_img1, fingerprint_img2])
        verifinger_output_lines = verifinger_output.split(b'\n')
        for line in verifinger_output_lines:
            line = line.decode('utf-8')
            line_parts = line.split(';')
            if len(line_parts) > 2:
                image_name = str(line_parts[1].strip())
                if image_name == img1:
                    morph_img1_score = str(line_parts[-1].strip())
                if image_name == img2:
                    morph_img2_score = str(line_parts[-1].strip())

        output_line = '{Minutiae=' + str(minutia_type) + ', Epochs=' + str(epochs) + ', Base_Folder=' + str(
            base_folder) + ', Img_morph=' + morph_img + ', Img1=' + str(img1) + ', Img2=' + str(
            img2) + ', Morph_Img1_score=' + str(morph_img1_score) + ', Morph_Img2_score=' + str(morph_img2_score) + '}'

        return verifinger_output_lines, output_line

    except Exception as e:
        print('Error in fetching verifinger score -' + str(e))
        traceback.print_exc()


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    verifinger_score_path = sys.argv[2]
    method = sys.argv[3]
    epochs = sys.argv[4]
    error_txt = sys.argv[5]
    try:
        folder_count = 0
        verifinger_output_lines = []
        if method == 'pointingMinutiae':
            minutia_type = 'PM'
        elif method == 'directedMinutiae':
            minutia_type = 'DM'
        else:
            minutia_type = 'PM'

        if epochs == '15':
            if method == 'pointingMinutiae':
                mimg_end_pattern = '_pm_mmap_fake_15.png'
            elif method == 'directedMinutiae':
                mimg_end_pattern = '_dm_mmap_fake_15.png'
        elif epochs == '30':
            if method == 'pointingMinutiae':
                mimg_end_pattern = '_pm_mmap_fake_30.png'
            elif method == 'directedMinutiae':
                mimg_end_pattern = '_dm_mmap_fake_30.png'
        elif epochs == '55':
            if method == 'pointingMinutiae':
                mimg_end_pattern = '_pm_mmap_fake_55.png'
            elif method == 'directedMinutiae':
                mimg_end_pattern = '_dm_mmap_fake_55.png'
        else:
            mimg_end_pattern = '_pm_mmap_fake_30.png'

        for root, _, files in os.walk(directory_path):
            img1_cropped_path = ''
            img2_cropped_path = ''
            morphed_img_path = ''
            sim_core_txt_path = ''
            img_count = 0
            morphed_img_count = 0
            sim_score_txt_count = 0
            for file in files:
                # Check if the file is an image
                if file.lower().endswith('.png') and (not file.lower().endswith('_cropped.png')) and (
                not file.lower().endswith('_mmap.png')) and (not file.lower().endswith('_overlapped.png')) and (
                not file.lower().endswith('_15.png')) and (not file.lower().endswith('_30.png')) and (
                not file.lower().endswith('_55.png')):
                    img_count = img_count + 1
                    if img_count == 1:
                        img1_cropped_path = os.path.join(root, file)
                    if img_count == 2:
                        img2_cropped_path = os.path.join(root, file)

                if file.lower().endswith(mimg_end_pattern):
                    morphed_img_count = morphed_img_count + 1
                    if morphed_img_count == 1:
                        morphed_img_path = os.path.join(root, file)

                if file.lower().endswith('_sim_score.txt'):
                    sim_score_txt_count = sim_score_txt_count + 1
                    if sim_score_txt_count == 1:
                        sim_core_txt_path = os.path.join(root, file)

            if img1_cropped_path and img2_cropped_path and morphed_img_path and sim_core_txt_path:
                try:
                    verifinger_original_output, verifinger_output_line = get_verifinger_score(minutia_type, epochs,
                                                                                              morphed_img_path,
                                                                                              img1_cropped_path,
                                                                                              img2_cropped_path, root)
                    verifinger_output_lines.append(verifinger_output_line)
                    with open(sim_core_txt_path, 'a') as file:
                        file.write('\n' + 'Verifinger Scores - ' + str(method) + '-' + str(epochs) + ':' + str(
                            verifinger_original_output))
                    folder_count = folder_count + 1
                    print('Folder count - ' + str(folder_count))
                except:
                    with open(error_txt, 'a') as file:
                        file.write('\n' + 'Fake file - ' + str(os.path.basename(morphed_img_path)) + ', ' + str(
                            os.path.basename(root)))
                    print('Error in getting verfinger score -' + str(os.path.basename(morphed_img_path)) + str(
                        os.path.basename(root)))
                    continue
            else:
                continue

        with open(verifinger_score_path, 'a', encoding='utf-8') as file:
            for line in verifinger_output_lines:
                file.write(f"{line}\n")

    except Exception as e:
        print(
            'Error -' + os.path.basename(img1_cropped_path) + ',' + os.path.basename(img2_cropped_path) + '-' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
