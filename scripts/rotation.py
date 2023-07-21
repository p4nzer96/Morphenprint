import cv2
import numpy as np
import sys

def rotate_image(image, angle, image_center):
  M = cv2.getRotationMatrix2D(image_center, angle, 1)
  rotated_image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
  return rotated_image

def main():
  image = sys.argv[1]
  rotated_image = rotate_image(image)

if __name__ == '__main__':
    main()