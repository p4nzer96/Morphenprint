from PIL import Image
import sys
import os
import subprocess
import traceback


def main():
    directory_path = sys.argv[1]
    # save path
    original_1_path = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_1_original'
    original_2_path = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_2_original'
    original_3_path = ''#'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_3_original'
    epochs_15_path = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_15'
    epochs_30_path = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_30'
    epochs_55_path = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_55'

    original_1_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_1_original.txt'
    original_2_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_2_original.txt'
    original_3_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/img_3_original.txt'
    epochs_15_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_15.txt'
    epochs_30_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_30.txt'
    epochs_55_path_txt = '' #'/vol1/meghana_rao/thesis/dataset_FVC2004/2_DB_final_comb_3/fvc_2004_db1_a_comb3_bmp_diff_impressions/right_loop/result_img_pm_55.txt'

    original_1_path_f = []
    original_2_path_f = []
    original_3_path_f = []
    epochs_15_path_f = []
    epochs_30_path_f = []
    epochs_55_path_f = []

    folder_count = 0

    for root, _, files in os.walk(directory_path): 
            original_img_count = 0
            epoch_15_img_count = 0
            epoch_30_img_count = 0
            epoch_55_img_count = 0
            img_1_path = '' 
            img_2_path = '' 
            img_3_path = ''
            img_pm_15_path = '' 
            img_pm_30_path = '' 
            img_pm_55_path = ''
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith('.png') and (not file.lower().endswith('_cropped.png')) and (not file.lower().endswith('_mmap.png')) and (not file.lower().endswith('_overlapped.png')) and (not file.lower().endswith('_15.png')) and (not file.lower().endswith('_30.png')) and (not file.lower().endswith('_55.png'))):
                    original_img_count = original_img_count + 1
                    if (original_img_count == 1):
                        img_1_path = os.path.join(root, file)
                    if (original_img_count == 2):
                        img_2_path = os.path.join(root, file)
                    if (original_img_count == 3):
                        img_3_path = os.path.join(root, file)
                
                if (file.lower().endswith('_pm_mmap_fake_15.png')):
                    epoch_15_img_count = epoch_15_img_count + 1
                    if (epoch_15_img_count == 1):
                        img_pm_15_path = os.path.join(root, file)
                
                if (file.lower().endswith('_pm_mmap_fake_30.png')):
                    epoch_30_img_count = epoch_30_img_count + 1
                    if (epoch_30_img_count == 1):
                        img_pm_30_path = os.path.join(root, file)
                
                if (file.lower().endswith('_pm_mmap_fake_55.png')):
                    epoch_55_img_count = epoch_55_img_count + 1
                    if (epoch_55_img_count == 1):
                        img_pm_55_path = os.path.join(root, file)
            
            if (img_1_path and img_2_path and img_3_path and img_pm_15_path and img_pm_30_path and img_pm_55_path):    
                try:
                    img_1_fn = str(os.path.splitext(os.path.basename(img_1_path))[0])    
                    img_2_fn = str(os.path.splitext(os.path.basename(img_2_path))[0])
                    img_3_fn = str(os.path.splitext(os.path.basename(img_3_path))[0])
                    img_pm_15_fn = str(os.path.splitext(os.path.basename(img_pm_15_path))[0])
                    img_pm_30_fn = str(os.path.splitext(os.path.basename(img_pm_30_path))[0])
                    img_pm_55_fn = str(os.path.splitext(os.path.basename(img_pm_55_path))[0])

                    img_1_bmp = (os.path.join(original_1_path, str(folder_count) + '_' + img_1_fn + '.bmp')).replace("\\", "/")
                    img_2_bmp = (os.path.join(original_2_path, str(folder_count) + '_' + img_2_fn + '.bmp')).replace("\\", "/")
                    img_3_bmp = (os.path.join(original_3_path, str(folder_count) + '_' + img_3_fn + '.bmp')).replace("\\", "/")
                    img_pm_15_bmp = (os.path.join(epochs_15_path, str(folder_count) + '_' + img_pm_15_fn + '.bmp')).replace("\\", "/")
                    img_pm_30_bmp = (os.path.join(epochs_30_path, str(folder_count) + '_' + img_pm_30_fn + '.bmp')).replace("\\", "/")
                    img_pm_55_bmp = (os.path.join(epochs_55_path, str(folder_count) + '_' + img_pm_55_fn + '.bmp')).replace("\\", "/")

                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_1_path, 'BMP3:'+img_1_bmp]).wait()
                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_2_path, 'BMP3:'+img_2_bmp]).wait()
                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_3_path, 'BMP3:'+img_3_bmp]).wait()
                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_pm_15_path, 'BMP3:'+img_pm_15_bmp]).wait()
                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_pm_30_path, 'BMP3:'+img_pm_30_bmp]).wait()
                    subprocess.Popen(['convert', '-colors', '256', '-colorspace', 'Gray', '-compress', 'None', '-depth', '8', img_pm_55_path, 'BMP3:'+img_pm_55_bmp]).wait()   

                    original_1_path_f.append(img_1_bmp)
                    original_2_path_f.append(img_2_bmp)
                    original_3_path_f.append(img_3_bmp)
                    epochs_15_path_f.append(img_pm_15_bmp)
                    epochs_30_path_f.append(img_pm_30_bmp)
                    epochs_55_path_f.append(img_pm_55_bmp)
                     
                except Exception as e:
                    print('Error -' + str(os.path.basename(root)) + str(e))
                    traceback.print_exc()
                    continue
            else:
                continue

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    with open(original_1_path_txt, 'w', encoding='utf-8') as file:
        for line in original_1_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")

    with open(original_2_path_txt, 'w', encoding='utf-8') as file:
        for line in original_2_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")
    
    with open(original_3_path_txt, 'w', encoding='utf-8') as file:
        for line in original_3_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")

    with open(epochs_15_path_txt, 'w', encoding='utf-8') as file:
        for line in epochs_15_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")

    with open(epochs_30_path_txt, 'w', encoding='utf-8') as file:
        for line in epochs_30_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")

    with open(epochs_55_path_txt, 'w', encoding='utf-8') as file:
        for line in epochs_55_path_f:
            file.write(f"{line.replace('/vol1', '', 1)}\n")

        

if __name__ == '__main__':
    main()
