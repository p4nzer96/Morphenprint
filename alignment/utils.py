import cv2


def get_center_of_image(img):
    """
    Get the center of the fingerprint image

    Args:
    img (numpy.ndarray): Fingerprint image.

    Returns:
    int: x-coordinate of the center of the fingerprint image.
    int: y-coordinate of the center of the fingerprint image.
    """

    # Threshold the image to create a binary image
    _, binary_image = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the contours of the fingerprint object
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the largest area (assuming it's the fingerprint object)
    largest_contour = max(contours, key=cv2.contourArea)

    # Find the minimum enclosing circle of the largest contour
    center, _ = cv2.minEnclosingCircle(largest_contour)
    center_x, center_y = map(int, center)

    return center_x, center_y


def split_list_into_halves(input_list):
    """
    Split the input list into two halves

    Args:
        input_list: The input list to be split

    Returns:
        tuple: The first and the second half of the input list
    """
    middle = len(input_list) // 2
    first_half = input_list[:middle + len(input_list) % 2]
    second_half = input_list[middle + len(input_list) % 2:]
    return first_half, second_half
