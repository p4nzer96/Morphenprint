import sys
import traceback

def main():
    # parse command line parameters
    results_path = sys.argv[1]  
    save_results_path = sys.argv[2] 
    results_category = sys.argv[3]
    score36_count = 0
    score48_count = 0
    score60_count = 0
    with open(results_path,"rt") as txtfile:
        output = txtfile.read()
    lines = output.split('\n')
    lines = [line for line in lines if line.strip() != '']
    for index, line in enumerate(lines):
        try:
            if len(line) > 0 and line[0] == '{':
                morph_img1_score = float(line[line.find("Morph_Img1_score=") + len("Morph_Img1_score=") : line.find(", Morph_Img2_score=")])
                morph_img2_score = float(line[line.find("Morph_Img2_score=") + len("Morph_Img2_score=") : line.find("}")])

                if morph_img1_score > 0 and morph_img2_score > 0:

                    if morph_img1_score > 36 and morph_img2_score > 36:
                        score36_count += 1

                    if morph_img1_score > 48 and morph_img2_score > 48:
                        score48_count += + 1

                    if morph_img1_score > 60 and morph_img2_score > 60:
                        score60_count = score60_count + 1

                    print('Line -', index)
                else:
                    continue

                
        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()
            continue

    with open(save_results_path, 'a') as file:
        file.write('\n \n' + str(results_category) + ' - (' + str(len(lines)) + ')' + '\n' + 'Score_36_Count - ' + str(score36_count) + ', Score_48_Count - ' + str(score48_count) + ', Score_60_Count - ' + str(score60_count))