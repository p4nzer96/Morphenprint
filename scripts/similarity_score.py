import cv2
import numpy as np
import sys

def calculate_psi_theta1_theta2(theta1, theta2):
  return (1 - ((2 * np.absolute(theta1 - theta2)) / np.pi))

def calculate_similarity(theta1, theta2, rel1, rel2):
  nominator = 0
  denominator = 0
  try:
    for i in range(len(theta1)):
      for j in range(len(theta1[i])):
        if (theta1[i][j] > 0 and theta2[i][j] > 0 and rel1[i][j] > 0 and rel2[i][j] > 0):
          psi_theta1_theta2 = calculate_psi_theta1_theta2(theta1[i][j], theta2[i][j])
          reliabilty_1_2 = rel1[i][j] + rel2[i][j]
          nominator = nominator + reliabilty_1_2 * psi_theta1_theta2
          denominator = denominator + reliabilty_1_2

    similarity_score = nominator/denominator
    return similarity_score
  except:
    print('error in similarity calulation')