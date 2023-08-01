import sys
import subprocess
import numpy as np 
import os
from PIL import Image, ImageDraw, ImageChops
import math
import tempfile
import traceback


def create_Patches(minutiae_list, bw_image, patch_size, min_reliability): 
    """Create minutia map from a list of minitiae by cropping patches around minutiae locations.
    """    

    minutiae_map = np.zeros(bw_image.shape,dtype=np.uint8)+255

    for minutiae in minutiae_list:
      if minutiae['Quality'] > min_reliability:

        angle = minutiae['Angle']
        x = minutiae['X']
        y = minutiae['Y']
        #x = x + 5.0 * math.cos(angle*math.pi/180.0)
        #y = y + 5.0 * math.sin(angle*math.pi/180.0)
            
        #draw square
        left =   int(x-0.5*patch_size+0.5)
        right =  int(x+0.5*patch_size+0.5)
        top =    int(y-0.5*patch_size+0.5)
        bottom = int(y+0.5*patch_size+0.5)
        #foo = minutiae_map[top:bottom, left:right]
        #print(foo.size)
        minutiae_map[top:bottom, left:right] = bw_image[top:bottom, left:right]		 
    
    return minutiae_map  



def create_pointingMinutiae(minutiae_list, im_size, square_size, line_length, line_width, min_reliability): 
    """Create minutia map from a list of minitiae by depicting a minutiae as a circle and a connected 
    line pointing to the minutiae direction. Endings are in black and bifurcations are in white. 
    """    
    
    minutiae_map = np.zeros(im_size,dtype=np.uint8)+128

    for minutiae in minutiae_list:
      if minutiae['Quality'] > min_reliability:

        angle = minutiae['Angle']
        x1 = minutiae['X']
        y1 = minutiae['Y']
        x2 = x1 + float(line_length) * math.cos(angle*math.pi/180.0)
        y2 = y1 + float(line_length) * math.sin(angle*math.pi/180.0)
        if minutiae['Type'] == 'Bifurcation':
            color = 255
        elif minutiae['Type'] == 'End':
            color = 0
            
        im = Image.fromarray(minutiae_map)
        draw = ImageDraw.Draw(im)
        #draw line
        draw.line( [int(x1+0.5), int(y1+0.5), int(x2+0.5), int(y2+0.5)], fill=color, width=line_width )

        left =   int(x1-0.5*square_size+0.5)
        right =  int(x1+0.5*square_size+0.5)
        top =    int(y1-0.5*square_size+0.5)
        bottom = int(y1+0.5*square_size+0.5)

        #draw circle
        #draw.ellipse( (left,top,right,bottom), fill=color, outline=color )
        
        # # create a numpy array from the image
        minutiae_map = np.array(im)

        # draw square
        minutiae_map[top:bottom,left:right] = color
    
    return minutiae_map        


def create_directedMinutiae(minutiae_list, im_size, line_length, line_width, min_reliability): 
    """Create minutia map from a list of minitiae by depicting a minutiae as a circle and a connected 
    line pointing to the minutiae direction. Endings are in black and bifurcations are in white. 
    """    
    
    minutiae_map = np.zeros(im_size,dtype=np.uint8)+128

    for minutiae in minutiae_list:
      if minutiae['Quality'] > min_reliability:

        angle = minutiae['Angle']
        x1 = minutiae['X']
        y1 = minutiae['Y']
        x2 = x1 + float(line_length) * math.cos(angle*math.pi/180.0)
        y2 = y1 + float(line_length) * math.sin(angle*math.pi/180.0)
        if minutiae['Type'] == 'Bifurcation':
            color = 255
        elif minutiae['Type'] == 'End':
            color = 0
            
        im = Image.fromarray(minutiae_map)
        draw = ImageDraw.Draw(im)

        #draw line
        draw.line( [int(x1+0.5), int(y1+0.5), int(x2+0.5), int(y2+0.5)], fill=color, width=line_width )
        
        # create a numpy array from the image
        minutiae_map = np.array(im)
        
    
    return minutiae_map    


def create_graySquare(minutiae_list, im_size, square_size, min_reliability): 
    """Create minutia map from a list of minitiae by depicting minutiae as gray squares. 
    The shadow of gray is given by the quantized minutiae direction. 
    """

    minutiae_map = np.zeros(im_size,dtype=np.uint8)+128

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:

            theta_color = int( minutiae['Angle'] / 360.0 * 128.0 + 0.5 );            
            if minutiae['Type'] == 'Bifurcation':
                theta_color = theta_color + 128

            x = minutiae['X']
            y = minutiae['Y']
            left =   int(x-0.5*square_size+0.5)
            right =  int(x+0.5*square_size+0.5)
            top =    int(y-0.5*square_size+0.5)
            bottom = int(y+0.5*square_size+0.5)
            minutiae_map[top:bottom,left:right] = theta_color
                   
    return minutiae_map           




def create_monoSquare(minutiae_list, im_size, square_size, min_reliability): 
    """Create minutia map from a list of minitiae by depicting minutiae as black squares on a white background. 
    There is no destinction between ridge line endings and bifurcations. 
    """

    minutiae_map = np.zeros(im_size,dtype=np.uint8)+255

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:
            x = minutiae['X']
            y = minutiae['Y']
            left =   int(x-0.5*square_size+0.5)
            right =  int(x+0.5*square_size+0.5)
            top =    int(y-0.5*square_size+0.5)
            bottom = int(y+0.5*square_size+0.5)
            minutiae_map[top:bottom,left:right] = 0
            
    return minutiae_map    


def create_minutiaeMap(morphed_minutiae_path, minutiae_map_dir, minutiae_map_save_name, scale = 1, method = 'pointingMinutiae', size = (512,512)):
    """Create minutia map from a list of minitiae by depicting minutiae as black squares on a white background. 
    There is no destinction between ridge line endings and bifurcations. 

    param: morphed_minutiae_path: directory of morphed minutiae txt file
    param: minutiae_map_dir: directory of minutiae map files
    param: scale: scale of minutiae map
    param: method: method of creating minutiae map
    param: size: size of minutiae map
    param: minutiae_map_save_name: name of the minutiae map that will be saved
    return: None
    """

    with open(morphed_minutiae_path,"rt") as txtfile:
        output = txtfile.read();

    lines = output.split('\n')
    minutiaelist = list()
    
    for line in lines:
        try:
            if len(line) > 0 and line[0] == '{':
                X = float(line[line.find("X=") + len("X=") : line.find(", Y")])
                Y = float(line[line.find("Y=") + len("Y=") : line.find(", T")])
                Type = line[line.find("Type=") + len("Type=") : line.find(", A")]
                Angle = float(line[line.find("Angle=") + len("Angle=") : line.find("\\xc2\\xb0")])
                Quality = float(line[line.find("Quality=") + len("Quality=") : line.find("%,")])
                minutiae = {'X': X*scale, 'Y': Y*scale, 'Type': Type, 'Angle': Angle, 'Quality': Quality }
                minutiaelist.append(minutiae)

        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()
            continue

    minutiae_quality_thr = 20.0
            
    if method == 'monoSquare':
        minutiae_map = create_monoSquare(minutiaelist, size, int(12.0*scale+0.5), minutiae_quality_thr) 

    elif method == 'graySquare':
        minutiae_map = create_graySquare(minutiaelist, size, int(12.0*scale+0.5), minutiae_quality_thr)

    elif method == 'pointingMinutiae':
        minutiae_map = create_pointingMinutiae(minutiaelist, size, int(6.0*scale+0.5), int(14.0*scale+0.5), int(3.0*scale+0.5), minutiae_quality_thr)
        
    elif method == 'directedMinutiae':
        minutiae_map = create_directedMinutiae(minutiaelist, size, int(14.0*scale+0.5), int(3.0*scale+0.5), minutiae_quality_thr)

    else:
        print("unknown method for minutiae representation")
        sys.exit(-1) 
  
    minutiae_map = Image.fromarray(minutiae_map)

    # form image for pix2pix
    double_image = Image.new("L", (size[0], size[1]))
    double_image.paste(minutiae_map, (0, 0))        
    double_image.save(minutiae_map_dir + '/' + minutiae_map_save_name)


def main():
    # parse command line parameters
    directory_path = sys.argv[1]
    method = sys.argv[2]
    scale = 1.0
    size = (512,512)
    end_path_str = '_mmap.png'
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            morphed_minutiae_path = ''
            minutiae_map_save_name = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if (file.lower().endswith('_mm.txt')):
                    count = count + 1
                    if (count == 1):
                        morphed_minutiae_path = os.path.join(root, file)
            
            # create minutiae maps.
            if (morphed_minutiae_path):
                if method == 'pointingMinutiae':
                    end_path_str = '_pm_mmap.png'
                elif method == 'directedMinutiae':
                    end_path_str = '_dm_mmap.png'
                minutiae_map_save_name = str(os.path.splitext(os.path.basename(morphed_minutiae_path))[0]) + end_path_str
                create_minutiaeMap(morphed_minutiae_path, root, minutiae_map_save_name, scale, method, size)

            folder_count = folder_count + 1
            print('Folder count - ' + str(folder_count))

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()


    