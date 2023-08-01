import sys
import os
import traceback
from subprocess import check_output


def get_verifinger_score(morphed_fingerprint_img, fingerprint_img1, fingerprint_img2):
    try:
        morph_img = os.path.basename(morphed_fingerprint_img)
        img1 = os.path.basename(fingerprint_img1)
        img2 = os.path.basename(fingerprint_img2)
        # get the response
        verifinger_output = check_output( ['Verifinger1toN', morphed_fingerprint_img, fingerprint_img1, fingerprint_img2] )
        output = verifinger_output.split(b'\n');
        print(output)
        morph_img1_score = ''
        morph_img2_score = ''

        output_line = '{Minutiae=PM, Epochs=15, Img_morph='+ str(morph_img) + ', Img1=' + str(img1) + ', Img2=' + str(img2) + ', Morph_Img1_score=' + str(morph_img1_score) + ', Morph_Img2_score=' + str(morph_img2_score) + '}'
        
        return output_line
        
    except Exception as e:
        print('Error in fetching verfinger score -' + str(e))
        traceback.print_exc()


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    verifinger_score_path = sys.argv[2]
    try:
        folder_count = 0
        verifinger_output_lines = []
        for root, _, files in os.walk(directory_path): 
            img1_cropped_path = ''
            img2_cropped_path = ''
            morphed_img_path = ''
            img_count = 0
            morphed_img_count = 0
            verifinger_output_line = ''
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith('_cropped.png')):
                    img_count = img_count + 1
                    if (img_count == 1):
                        img1_cropped_path = os.path.join(root, file)
                    if (img_count == 2):
                        img2_cropped_path = os.path.join(root, file)
                
                if (file.lower().endswith('_fake_15.png')):
                    morphed_img_count = morphed_img_count + 1
                    if (morphed_img_count == 1):
                        morphed_img_path = os.path.join(root, file)

            
            if (img1_cropped_path and img2_cropped_path and morphed_img_path):    
                try:           
                    verifinger_output_line = get_verifinger_score(morphed_img_path, img1_cropped_path, img2_cropped_path)
                    verifinger_output_lines.append(verifinger_output_line)
                    folder_count = folder_count + 1
                    print('Folder count - '+ str(folder_count))
                except:
                    print('Error in getting verfinger score -'  + os.path.basename(img1_cropped_path) + ',' + os.path.basename(img2_cropped_path))
                    continue
        
        with open(verifinger_score_path, 'w', encoding='utf-8') as file:
            for line in verifinger_output_lines:
                file.write(f"{line}\n")
   
    except Exception as e:
        print('Error -'  + os.path.basename(img1_cropped_path) + ',' + os.path.basename(img2_cropped_path) + '-' +str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()