from pathlib import Path


with open("./path_morph_right_tented_arch.txt", "r") as f:
    paths = [Path(x).resolve() for x in f.read().split('\n')]
    Path("errors.txt").unlink(missing_ok=True)
    for file in paths:
        if not file.exists():
            f = open("errors.txt", "a")
            f.write(f"{file}\n")
    if Path("errors.txt").exists():
        print("Some files are missing - check errors.txt")
    else:
        print("All files are present")