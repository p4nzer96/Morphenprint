import cv2
import numpy as np
import sys

def translate_image(image, tx, ty):
  translation_matrix = np.array([[1, 0, tx], [0, 1, ty]], dtype=np.float32)
  translated_image = cv2.warpAffine(src=image, M=translation_matrix, dsize=(image.shape[1], image.shape[0]), borderValue=(255, 255, 255))
  return translated_image

def main():
  image = sys.argv[1]
  translated_image = translate_image(image)

if __name__ == '__main__':
    main()