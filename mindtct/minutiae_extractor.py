import subprocess
from pathlib import Path
from PIL import Image

mindtct_path = Path(__file__).parent / "mindtct"


def mindtct_runner(ds_path, new_data_path):
    """
    Run the mindtct on the images in the dataset

    Args:
        ds_path: Path of the dataset
        new_data_path: Path to store the minutiae extracted images and related .jpg images
    """
    for img_path in ds_path.rglob("*"):
        relative_path = img_path.relative_to(ds_path)
        new_path = new_data_path / relative_path
        try:
            if img_path.is_dir():
                new_path.mkdir(exist_ok=True, parents=True)
            elif str(img_path.suffix).lower() in [".jpg", ".jpeg", ".bmp", ".png"]:
                output_image_name = new_path.with_suffix(".jpg")
                if not output_image_name.exists():
                    img = Image.open(img_path).convert("L")
                    img.save(output_image_name)
                subprocess.run(f"./mindtct -b -m1 {new_path.with_suffix('.jpg')} {new_path.with_suffix('')}",
                               cwd=Path(__file__).parent, shell=True)
        except Exception as e:
            print(f"Exception: {img_path} - {e}")
            continue


if __name__ == "__main__":
    mindtct_runner(ds_path=Path("/livdet2021test/Dermalog_Consensual/30_26_0/Live"),
                   new_data_path=(Path(__file__).parent.parent.parent / "LivDet2021-DS"))
