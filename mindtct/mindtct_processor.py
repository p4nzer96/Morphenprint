import re
import numpy as np
from pathlib import Path

import pandas as pd


def get_direction_map(filename: Path):
    """
    Parsing of mindtct ".dm" (direction map) file type.
    Source: https://ffpis.sourceforge.net/man/mindtct.html
    Args:
        filename: Path to the ".dm" file.

    Returns: Numpy array containing the parsed direction map data.
    """
    if filename.suffix != ".dm":
        return

    with open(filename, "r") as f:
        lines = f.readlines()
        parsed_lines = []
        # Parsing the dm file
        for line in lines[:-1]:
            parsed_lines.append(
                [int(x) for x in line.split(" ") if x.lstrip("-").isdigit()]
            )
        matrix = np.array(parsed_lines)
        mask = np.where((matrix != -1), 1, 0)
        return np.multiply(matrix, mask) * 11.25 + mask


def get_high_curvature_map(filename: Path):
    """
    Parsing of mindtct ".hcm" (high-curvature map) file type.
    Source: https://ffpis.sourceforge.net/man/mindtct.html
    Args:
        filename: Path to the ".hcm" file.

    Returns: Numpy array containing the parsed high-curvature map data.
    """
    if filename.suffix != ".hcm":
        return

    with open(filename, "r") as f:
        lines = f.readlines()
        parsed_lines = []
        # 
        for line in lines[:-1]:
            parsed_lines.append(
                [int(x) for x in line.split(" ") if x.lstrip("-").isdigit()]
            )
        return np.array(parsed_lines)


def get_low_contrast_map(filename: Path):
    """
    Parsing of mindtct ".lcm" (low-contrast map) file type.
    Source: https://ffpis.sourceforge.net/man/mindtct.html
    Args:
        filename: Path to the ".lcm" file.

    Returns: Numpy array containing the parsed low-contrast map data.
    """
    if filename.suffix != ".lcm":
        return

    with open(filename, "r") as f:
        lines = f.readlines()
        parsed_lines = []
        # Parsing
        for line in lines[:-1]:
            parsed_lines.append(
                [int(x) for x in line.split(" ") if x.lstrip("-").isdigit()]
            )
        return np.array(parsed_lines)


def get_minutiae(filename: Path, cache: bool = True):
    """
    Parsing of mindtct ".min" (minutiae) file type.
    Source: https://ffpis.sourceforge.net/man/mindtct.html

    Attributes:
        filename (Path): Path to the ".min" file.
        cache (bool): Whether to cache the parsed minutiae data (saves the parsed data as file).

    Returns:
        dataframe: DataFrame containing the parsed minutiae data.
    """
    if filename.suffix != ".min":
        return
    
    if cache and (filename.parent / f"{filename.stem}.pkl").exists():
        cache_filename = filename.parent / f"{filename.stem}.pkl"
        try:
            return pd.read_pickle(cache_filename)
        except FileNotFoundError:
            print("Trying to read from cache, but file not found.")

    min_dict = {}
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines[4:-1]:
            split = [x.strip() for x in line.split(":")]
            min_dict[split[0]] = {
                "x_coord": int(split[1].split(", ")[0]),
                "y_coord": int(split[1].split(", ")[1]),
                "direction": int(split[2]),
                "reliability": float(split[3]),
                "type": split[4],
                "internal_type": split[5],
                "feature_id": int(split[6])
            }
            for x in range(7, len(split)):
                nx, ny, rc = re.split(r"[\s,;]+", split[x])
                min_dict[split[0]][f"nx{x-6}"] = nx
                min_dict[split[0]][f"ny{x-6}"] = ny
                min_dict[split[0]][f"rc{x-6}"] = rc
    if cache:
        pd.DataFrame(min_dict).T.to_pickle(filename.parent / f"{filename.stem}.pkl")
    return pd.DataFrame(min_dict).T