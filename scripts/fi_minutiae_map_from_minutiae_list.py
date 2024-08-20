import sys
import numpy as np
import os
from PIL import Image, ImageDraw
import math
import traceback


def create_Patches(minutiae_list, bw_image, patch_size, min_reliability):
    """Create minutia map from a list of minitiae by cropping patches around minutiae locations.
    """

    minutiae_map = np.zeros(bw_image.shape, dtype=np.uint8) + 255

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:
            
            x, y, angle = minutiae['X'], minutiae['Y'], minutiae['Angle']  # noqa: F841
            
            #x = x + 5.0 * math.cos(angle*math.pi/180.0)
            #y = y + 5.0 * math.sin(angle*math.pi/180.0)

            # Drawing a square around the minutiae
            left = int(x - 0.5 * patch_size + 0.5)
            right = int(x + 0.5 * patch_size + 0.5)
            top = int(y - 0.5 * patch_size + 0.5)
            bottom = int(y + 0.5 * patch_size + 0.5)
            #foo = minutiae_map[top:bottom, left:right]

            minutiae_map[top:bottom, left:right] = bw_image[top:bottom, left:right]

    return minutiae_map


def create_pointingMinutiae(minutiae_list, im_size, square_size, line_length, line_width, min_reliability):
    """Create minutia map from a list of minutiae by depicting a minutiae as a circle and a connected
    line pointing to the minutiae direction. Endings are in black and bifurcations are in white. 
    """

    minutiae_map = np.zeros(im_size, dtype=np.uint8) + 128

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:

            x1, y1, angle = minutiae['X'], minutiae['Y'], minutiae['Angle']
            
            x2 = x1 + float(line_length) * math.cos(angle * math.pi / 180.0)
            y2 = y1 + float(line_length) * math.sin(angle * math.pi / 180.0)
            
            # Set color based on minutiae type
            if minutiae['Type'] == 'Bifurcation':
                color = 255
            elif minutiae['Type'] == 'End':
                color = 0

            im = Image.fromarray(minutiae_map)
            draw = ImageDraw.Draw(im)
            # Draw a line
            draw.line([int(x1 + 0.5), int(y1 + 0.5), int(x2 + 0.5), int(y2 + 0.5)], fill=color, width=line_width)

            left = int(x1 - 0.5 * square_size + 0.5)
            right = int(x1 + 0.5 * square_size + 0.5)
            top = int(y1 - 0.5 * square_size + 0.5)
            bottom = int(y1 + 0.5 * square_size + 0.5)

            # # create a numpy array from the image
            minutiae_map = np.array(im)

            # draw square
            minutiae_map[top:bottom, left:right] = color

    return minutiae_map


def create_directedMinutiae(minutiae_list, im_size, line_length, line_width, min_reliability):
    """Create minutia map from a list of minitiae by depicting a minutiae as a circle and a connected 
    line pointing to the minutiae direction. Endings are in black and bifurcations are in white.

    Args:
        minutiae_list (list): List of minutiae.
        im_size (tuple): Size of the image.
        line_length (int): Length of the line.
        line_width (int): Width of the line.
        min_reliability (float): Minimum reliability of the minutiae.

    Returns:
        numpy.ndarray: Minutiae map.
    """

    global color
    minutiae_map = np.zeros(im_size, dtype=np.uint8) + 128

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:

            x1, y1, angle = minutiae['X'], minutiae['Y'], minutiae['Angle']
            x2 = x1 + float(line_length) * math.cos(angle * math.pi / 180.0)
            y2 = y1 + float(line_length) * math.sin(angle * math.pi / 180.0)

            # Set color based on minutiae type
            if minutiae['Type'] == 'Bifurcation':
                color = 255
            elif minutiae['Type'] == 'End':
                color = 0

            im = Image.fromarray(minutiae_map)
            draw = ImageDraw.Draw(im)

            # Draw a line
            draw.line([int(x1 + 0.5), int(y1 + 0.5), int(x2 + 0.5), int(y2 + 0.5)], fill=color, width=line_width)

            # Create a numpy array from the image
            minutiae_map = np.array(im)

    return minutiae_map


def create_graySquare(minutiae_list, im_size, square_size, min_reliability):
    """Create minutia map from a list of minutiae by depicting minutiae as gray squares.
    The shadow of gray is given by the quantized minutiae direction.

    Args:
    minutiae_list (list): List of minutiae.
    im_size (tuple): Size of the image.
    square_size (int): Size of the square.
    min_reliability (float): Minimum reliability of the minutiae.

    Returns:
    numpy.ndarray: Minutiae map.
    """
    minutiae_map = np.zeros(im_size, dtype=np.uint8) + 128

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:

            theta_color = int(minutiae['Angle'] / 360.0 * 128.0 + 0.5)
            
            # Set color based on minutiae type
            if minutiae['Type'] == 'Bifurcation':
                theta_color = theta_color + 128

            x, y = minutiae['X'], minutiae['Y']
            
            left = int(x - 0.5 * square_size + 0.5)
            right = int(x + 0.5 * square_size + 0.5)
            top = int(y - 0.5 * square_size + 0.5)
            bottom = int(y + 0.5 * square_size + 0.5)
            minutiae_map[top:bottom, left:right] = theta_color

    return minutiae_map


def create_monoSquare(minutiae_list, im_size, square_size, min_reliability):
    """Create minutia map from a list of minutiae by depicting minutiae as black squares on a white background.
    There is no distinction between ridge line endings and bifurcations.
    """

    minutiae_map = np.zeros(im_size, dtype=np.uint8) + 255

    for minutiae in minutiae_list:
        if minutiae['Quality'] > min_reliability:
            x = minutiae['X']
            y = minutiae['Y']
            left = int(x - 0.5 * square_size + 0.5)
            right = int(x + 0.5 * square_size + 0.5)
            top = int(y - 0.5 * square_size + 0.5)
            bottom = int(y + 0.5 * square_size + 0.5)
            minutiae_map[top:bottom, left:right] = 0

    return minutiae_map


def create_minutiaeMap(morphed_minutiae_path, minutiae_map_dir, minutiae_map_save_name, scale=1,
                       method='pointingMinutiae', size=(512, 512)):
    """
    Create minutia map from a list of minutiae by depicting minutiae as black squares on a white background.
    There is no distinction between ridge line endings and bifurcations.

    Args:
        morphed_minutiae_path: directory of morphed minutiae txt file
        minutiae_map_dir: directory of minutiae maps files
        scale: scale of minutiae map
        method: method of creating minutiae map
        size: size of minutiae map
        minutiae_map_save_name: name of the minutiae map that will be saved

    Returns:
        None
    """

    with open(morphed_minutiae_path, "rt") as txtfile:
        output = txtfile.read()

    lines = output.split('\n')
    minutiaelist = list()

    for line in lines:
        try:
            if len(line) > 0 and line[0] == '{':
                X = float(line[line.find("X=") + len("X="): line.find(", Y")])
                Y = float(line[line.find("Y=") + len("Y="): line.find(", T")])
                Type = line[line.find("Type=") + len("Type="): line.find(", A")]
                Angle = float(line[line.find("Angle=") + len("Angle="): line.find("\\xc2\\xb0")])
                Quality = float(line[line.find("Quality=") + len("Quality="): line.find("%,")])
                minutiae = {'X': X * scale, 'Y': Y * scale, 'Type': Type, 'Angle': Angle, 'Quality': Quality}
                minutiaelist.append(minutiae)

        except Exception as e:
            print('Error -' + str(e))
            traceback.print_exc()
            continue

    minutiae_quality_thr = 20.0

    if method == 'monoSquare':
        minutiae_map = create_monoSquare(minutiaelist, size, int(12.0 * scale + 0.5), minutiae_quality_thr)

    elif method == 'graySquare':
        minutiae_map = create_graySquare(minutiaelist, size, int(12.0 * scale + 0.5), minutiae_quality_thr)

    elif method == 'pointingMinutiae':
        minutiae_map = create_pointingMinutiae(minutiaelist, size, int(6.0 * scale + 0.5), int(14.0 * scale + 0.5),
                                               int(3.0 * scale + 0.5), minutiae_quality_thr)

    elif method == 'directedMinutiae':
        minutiae_map = create_directedMinutiae(minutiaelist, size, int(14.0 * scale + 0.5), int(3.0 * scale + 0.5),
                                               minutiae_quality_thr)

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
    data_txt_path = sys.argv[3]
    scale = 1.0
    size = (512, 512)
    end_path_str = '_mmap.png'
    try:
        folder_count = 0
        for root, _, files in os.walk(directory_path):
            morphed_minutiae_path = ''
            minutiae_map_save_name = ''
            count = 0
            for file in files:
                # Check if the file is an image
                if file.lower().endswith('_mm.txt'):
                    count = count + 1
                    if count == 1:
                        morphed_minutiae_path = os.path.join(root, file)

            # create minutiae maps.
            if morphed_minutiae_path:

                if method == 'pointingMinutiae':
                    end_path_str = '_pm_mmap.png'
                elif method == 'directedMinutiae':
                    end_path_str = '_dm_mmap.png'
                minutiae_map_save_name = str(
                    os.path.splitext(os.path.basename(morphed_minutiae_path))[0]) + end_path_str
                create_minutiaeMap(morphed_minutiae_path, root, minutiae_map_save_name, scale, method, size)
                folder_count = folder_count + 1
                print('Folder count - ' + str(folder_count))
            else:
                with open(data_txt_path, 'a') as file:
                    file.write('\n' + 'Image Sets - ' + str(os.path.basename(root)) + ',' + str(
                        os.path.basename(morphed_minutiae_path)))
                continue

    except Exception as e:
        print('Error -' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
