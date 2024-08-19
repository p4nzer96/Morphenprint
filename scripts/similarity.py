import numpy as np


def calculate_psi_theta1_theta2(theta1, theta2):
    """
    Calculate psi(theta1, theta2) as defined in the paper.

    Args:
        theta1 (float): Angle of fingerprint 1.
        theta2 (float): Angle of fingerprint 2.

    Returns:
        float: psi(theta1, theta2) as defined in the paper.
    """
    return 1 - ((2 * np.absolute(theta1 - theta2)) / np.pi)


def calculate_similarity(theta1, theta2, rel1, rel2):
    """
    Calculate similarity score between two fingerprints.

    Args:
        theta1 (list): List of angles of fingerprint 1.
        theta2 (list): List of angles of fingerprint 2.
        rel1 (list): List of reliabilities of fingerprint 1.
        rel2 (list): List of reliabilities of fingerprint 2.

    Returns:
        float: Similarity score between two fingerprints.
    """
    nominator, denominator = 0, 0
    
    try:
        for i in range(len(theta1)):
            for j in range(len(theta1[i])):
                if (
                    theta1[i][j] > 0
                    and theta2[i][j] > 0
                    and rel1[i][j] > 0
                    and rel2[i][j] > 0
                ):
                    psi_theta1_theta2 = calculate_psi_theta1_theta2(
                        theta1[i][j], theta2[i][j]
                    )
                    reliabilty_1_2 = rel1[i][j] + rel2[i][j]
                    nominator = nominator + reliabilty_1_2 * psi_theta1_theta2
                    denominator = denominator + reliabilty_1_2

        similarity_score = nominator / denominator
        return similarity_score
    except Exception:
        print("error in similarity calulation")
