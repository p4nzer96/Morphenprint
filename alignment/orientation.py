import math

import numpy as np
import cv2 as cv

def calculate_angles(im, W, smooth=False):
    """
    Anisotropy orientation estimate, based on equations 5 from:
    https://pdfs.semanticscholar.org/6e86/1d0b58bdf7e2e2bb0ecbf274cee6974fe13f.pdf

    Attributes:
        im: The input image
        W: The width of the ridge
        smooth: A boolean value to smooth the angles

    Returns:
        array: The smoothed angles of the fingerprint image
    """

    y, x = im.shape

    # Defining the Sobel filters
    ySobel = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]], dtype=np.int64)

    xSobel = np.transpose(ySobel)

    ang_result = [[] for _ in range(1, y, W)]
    rel_result = [[] for _ in range(1, y, W)]

    # Calculating the gradients
    Gx_ = cv.filter2D(im / 125, -1, ySobel) * 125
    Gy_ = cv.filter2D(im / 125, -1, xSobel) * 125

    # Calculating the orientation and reliability
    # Shifting the window by W
    for j in range(1, y, W):
        for i in range(1, x, W):
            
            Gx = np.round(Gx_[j: j+W, i: i+W])  # Horizontal gradients at j, i
            Gy = np.round(Gy_[j: j+W, i: i+W])  # Vertical gradients at j, i

            nominator = np.sum(2 * Gx * Gy)
            denominator = np.sum(Gx ** 2 - Gy ** 2)
            
            rel_nom_1 = np.array(denominator, dtype=np.float64)
            rel_nom_2 = np.array(np.sum(Gx * Gy)).astype(np.float64)
            rel_den_1 = np.array(np.sum(Gx ** 2)).astype(np.float64)
            rel_den_2 = np.array(np.sum(Gy ** 2)).astype(np.float64)

            if nominator or denominator:
                reliability = (np.sqrt(rel_nom_1 ** 2 + 4 * (rel_nom_2 ** 2))) / (rel_den_1 + rel_den_2 + 1e-12)
                orientation = math.pi / 2 + math.atan2(nominator, denominator) / 2
                ang_result[int((j - 1) // W)].append(orientation)
                rel_result[int((j - 1) // W)].append(reliability)
            else:
                ang_result[int((j - 1) // W)].append(0)
                rel_result[int((j - 1) // W)].append(0)

    ang_result = np.array(ang_result)
    rel_result = np.array(rel_result)
    rel_result_max = np.max(rel_result)
    rel_result_min = np.min(rel_result)
    rel_result_norm = (rel_result - rel_result_min) / (rel_result_max - rel_result_min)

    smooth_angles_result = smooth_angles(ang_result) if smooth else None

    return smooth_angles_result, ang_result, rel_result_norm


def gauss(x, y):
    ssigma = 1.0
    return (1 / (2 * math.pi * ssigma)) * math.exp(-(x * x + y * y) / (2 * ssigma))


def kernel_from_function(size, f):
    kernel = [[] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            kernel[i].append(f(i - size / 2, j - size / 2))
    return kernel


def smooth_angles(angles):
    """
    reference: https://airccj.org/CSCP/vol7/csit76809.pdf pg91
    Practically, it is possible to have a block so noisy that the directional estimate is completely false.
    This then causes a very large angular variation between two adjacent blocks. However, a
    fingerprint has some directional continuity; such a variation between two adjacent blocks is then
    representative of a bad estimate. To eliminate such discontinuities, a low-pass filter is applied to
    the directional board.

    Attrs:
        angles (np.array): List of angles of the fingerprint image.

    Returns:
        array: Smoothed angles of the fingerprint image.
    """

    cos_angles = np.cos(angles.copy() * 2)
    sin_angles = np.sin(angles.copy() * 2)

    kernel = np.array(kernel_from_function(5, gauss))

    cos_angles = cv.filter2D(cos_angles / 125, -1, kernel) * 125
    sin_angles = cv.filter2D(sin_angles / 125, -1, kernel) * 125
    smooth_angles = np.arctan2(sin_angles, cos_angles) / 2

    return smooth_angles


def get_line_ends(i, j, W, tang):
    if -1 <= tang <= 1:
        begin = (i, int((-W / 2) * tang + j + W / 2))
        end = (i + W, int((W / 2) * tang + j + W / 2))
    else:
        begin = (int(i + W / 2 + W / (2 * tang)), j + W // 2)
        end = (int(i + W / 2 - W / (2 * tang)), j - W // 2)
    return begin, end


def visualize_angles(im, mask, angles, W):
    """
    Visualize the angles of the fingerprint image
    Args:
        im: input image
        mask: image mask
        angles: angles of the fingerprint image
        W: width of the ridge

    Returns: image with visualized angles

    """
    (y, x) = im.shape
    result = cv.cvtColor(np.zeros(im.shape, np.uint8), cv.COLOR_GRAY2RGB)
    mask_threshold = (W - 1) ** 2
    for i in range(1, x, W):
        for j in range(1, y, W):
            radian = np.sum(mask[j - 1:j + W, i - 1:i + W])
            if radian > mask_threshold:
                tang = math.tan(angles[(j - 1) // W][(i - 1) // W])
                begin, end = get_line_ends(i, j, W, tang)
                cv.line(result, begin, end, color=(255, 255, 255), lineType=cv.LINE_AA)

    cv.resize(result, im.shape, result)
    return result


if __name__ == "__main__":
    img = cv.imread("../LivDet2021-DS/A_1/LEFT_INDEX.jpg", cv.IMREAD_GRAYSCALE)
    smooth_angles, angles, reliability = calculate_angles(img, 16, smooth=True)