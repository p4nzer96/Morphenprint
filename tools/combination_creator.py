import itertools
from pathlib import Path

import pandas as pd


def make_combinations_manual(fp_list, pattern):
    """
    This function creates all possible combinations of the images in the directory, based on a list of paths
    Args:
        fp_list: list of paths
        pattern: pattern of the images

    Returns:
        A csv file with the combinations
    """

    # Getting the images

    combinations = [list(comb) + [pattern] for comb in itertools.combinations(fp_list, 2)]

    combinations_df = pd.DataFrame(combinations, columns=["Image1", "Image2", "Type"])
    combinations_df.to_csv(f"combinations_{pattern}.csv", index=False)


def make_combinations(dataset_info):
    """
    This function creates all possible combinations of the images in the directory

    Args:
        dataset_info: path to the dataset_info file

    Returns:
        A csv file with the combinations
    """

    # Trying to get al the possible intra user combinations (only same pattern)

    # Loading the dataframe
    ds_info = pd.read_csv(dataset_info)

    # Take only the images of Dermalog and Consensual
    conditions = (
            (ds_info["Sensor"] == "Dermalog")
            & (ds_info["Acq_Type"] == "Consensual")
            & (ds_info["Liveness"] == "Live")
            & (ds_info["Material"] == "A_1")
    )

    # Getting the images
    images_loop = ds_info[conditions & (ds_info["Pattern"] == "loop")]
    images_whorl = ds_info[conditions & (ds_info["Pattern"] == "whorl")]
    images_arch = ds_info[conditions & (ds_info["Pattern"] == "arch")]

    # Getting the combinations

    combinations_loop = itertools.combinations(images_loop["Path"], 2)
    combinations_whorl = itertools.combinations(images_whorl["Path"], 2)
    combinations_arch = itertools.combinations(images_arch["Path"], 2)

    combinations_l = [list(comb) + ['loop'] for comb in combinations_loop]
    combinations_w = [list(comb) + ['whorl'] for comb in combinations_whorl]
    combinations_a = [list(comb) + ['arch'] for comb in combinations_arch]

    # Concatenating the combinations
    combinations_l = pd.DataFrame(combinations_l, columns=["Image1", "Image2", "Type"]).to_csv("combinations_loop.csv",
                                                                                               index=False)
    combinations_w = pd.DataFrame(combinations_w, columns=["Image1", "Image2", "Type"]).to_csv("combinations_whorl.csv",
                                                                                               index=False)
    combinations_a = pd.DataFrame(combinations_a, columns=["Image1", "Image2", "Type"]).to_csv("combinations_arch.csv",
                                                                                               index=False)

    return combinations_l, combinations_w, combinations_a


if __name__ == "__main__":
    dataset_info = Path("./final_dataset_info.csv")

    fp_list = open("./path_morph_right_tented_arch.txt", "r").read().split('\n')

    make_combinations_manual(fp_list=fp_list, pattern="arch")
