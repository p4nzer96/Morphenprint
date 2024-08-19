import sys
import os
import traceback


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    data_txt_path = sys.argv[2]
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            r_pm_15 = ''
            r_pm_30 = ''
            r_pm_55 = ''
            r_dm_15 = ''
            r_dm_30 = ''
            r_dm_55 = ''
            r_mm = ''
            for file in files:
                
                # Lowercase the filename
                file = file.lower()
                # Check if the file is an image
                if file.endswith('_pm_mmap_fake_15.png'):
                    r_pm_15 = os.path.join(root, file)
                elif file.endswith('_pm_mmap_fake_30.png'):
                    r_pm_30 = os.path.join(root, file)
                elif file.endswith('_pm_mmap_fake_55.png'):
                    r_pm_55 = os.path.join(root, file)
                elif file.endswith('_dm_mmap_fake_15.png'):
                    r_dm_15 = os.path.join(root, file)
                elif file.endswith('_dm_mmap_fake_30.png'):
                    r_dm_30 = os.path.join(root, file)
                elif file.endswith('_dm_mmap_fake_55.png'):
                    r_dm_55 = os.path.join(root, file)
                elif file.endswith('_mm.txt'):
                    r_mm = os.path.join(root, file)

            if not r_mm:
                continue
            # create minutiae maps.
            if r_pm_15 and r_pm_30 and r_pm_55 and r_dm_15 and r_dm_30 and r_dm_55:
                continue
            else:
                if not r_pm_15 or not r_pm_30 or not r_pm_55:
                    with open(data_txt_path, 'a') as file:
                        file.write('\n' + 'PM file - ' + str(os.path.basename(root)))

                if not r_dm_15 or not r_dm_30 or not r_dm_55:
                    with open(data_txt_path, 'a') as file:
                        file.write('\n' + 'DM file - ' + str(os.path.basename(root)))

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
