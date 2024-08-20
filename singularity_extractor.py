import cv2
import numpy as np
import math


def poincare_index_at(i, j, angles, tolerance):
    """
    Calculate the Poincare index at a given pixel.

    Args:
        i (int): The row index.
        j (int): The column index.
        angles (numpy.ndarray): The angles of the image.
        tolerance (int): The tolerance value.

    Returns:
        str: The type of the basic pattern.
    """

    # Define the cells around the pixel
    cells = [(-1, -1), (-1, 0), (-1, 1),  # p1 p2 p3
             (0, 1), (1, 1), (1, 0),  # p8    p4
             (1, -1), (0, -1), (-1, -1)]  # p7 p6 p5

    angles_around_index = [math.degrees(
        angles[i - k][j - l]) for k, l in cells]  # noqa: E741
    index = 0

    for k in range(8):

        # calculate the difference
        difference = angles_around_index[k] - angles_around_index[k + 1]
        if difference > 90:
            difference -= 180
        elif difference < -90:
            difference += 180

        index += difference

    if 180 - tolerance <= index <= 180 + tolerance:
        return "delta"
    if -180 - tolerance <= index <= -180 + tolerance:
        return "loop"
    if 360 - tolerance <= index <= 360 + tolerance:
        return "whorl"
    return "none"


def calculate_singularities(im, angles, tolerance, W, mask):
    """
    Calculate the singularities of the fingerprint image.

    Args:
        im (numpy.ndarray): The fingerprint image.
        angles (numpy.ndarray): The angles of the fingerprint image.
        tolerance (int): The tolerance value.
        W (int): The width of the ridge.
        mask (numpy.ndarray): The mask of the fingerprint image.

    Returns:
        numpy.ndarray: The fingerprint image with the singularities.
        list: The list of loops.
        list: The list of deltas.
        list: The list of whorls.
    """

    result = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)

    # DELTA: RED, LOOP: ORANGE, whorl: INK
    colors = {"loop": (0, 0, 255),
              "delta": (0, 128, 255),
              "whorl": (255, 153, 255)}

    loop_list, delta_list, whorl_list = [], [], []
    loop_1d = []

    for i in range(3, len(angles) - 2):
        # Y
        loop, delta, whorl = [], [], []

        for j in range(3, len(angles[i]) - 2):  # x
            # mask any singularity outside the mask
            mask_slice = mask[(i - 2) * W:(i + 3) * W, (j - 2) * W:(j + 3) * W]
            mask_flag = np.sum(mask_slice)
            if mask_flag == (W * 5) ** 2:

                # Check for the singularity
                singularity = poincare_index_at(i, j, angles, tolerance)
                
                # If the singularity is not none, draw a rectangle around it
                if singularity != "none":
                    cv2.rectangle(result, ((j + 0) * W, (i + 0) * W),
                                  ((j + 1) * W, (i + 1) * W), colors[singularity], 3)
                    if singularity == "loop":
                        loop.append([i * W, j * W])
                        loop_1d.append([i * W, j * W])
                    if singularity == "delta":
                        delta.append([i * W, j * W])
                    if singularity == "whorl":
                        whorl.append([i * W, j * W])

        if len(loop) > 0:
            loop_list.append(loop)
        if len(delta) > 0:
            delta_list.append(delta)
        if len(whorl) > 0:
            whorl_list.append(whorl)

    return result, loop_1d, loop_list, delta_list, whorl_list


def get_pattern_type(loop_list, delta_list, whorl_list):
    if len(loop_list) > 2:  # A whorl has 2 or more loops
        return "whorl"
    elif len(loop_list) == 1 or len(loop_list) == 2:  # A loop has 1 or 2 loops
        return "loop"
    elif len(loop_list) == 0 and len(delta_list) == 0 and len(whorl_list) == 0:  # An arch has no loops, deltas or whorls
        return "arch"
