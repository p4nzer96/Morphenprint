import cv2

import numpy as np

def translate(image, tx, ty):
    """
    Translate the image by the given translation values.
    Args:
        image: The image to be translated.
        tx: The translation value in the x-direction.
        ty: The translation value in the y-direction.

    Returns:
        The translated image.
    """
    # Create the translation matrix
    translation_matrix = np.array([[1, 0, tx], [0, 1, ty]], dtype=np.float32)
    
    # Translating the image
    translated_image = cv2.warpAffine(src=image,
                                      M=translation_matrix,
                                      dsize=(image.shape[1], image.shape[0]),
                                      borderValue=(255, 255, 255))
    return translated_image

def rotate(image, angle, image_center):
    """
    Rotate the image by the given angle.

    Args:
    image (numpy.ndarray): Image to be rotated.
    angle (int): Angle of rotation in degrees.
    image_center (tuple): Center of the image.

    Returns:
    numpy.ndarray: Rotated image.
    """

    # Get the rotation matrix for the given angle
    M = cv2.getRotationMatrix2D(image_center, angle, 1)

    # Rotate the image
    rotated_image = cv2.warpAffine(
        image,
        M,
        (image.shape[1], image.shape[0]),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    return rotated_image