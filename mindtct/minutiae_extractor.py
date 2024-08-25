import subprocess
import multiprocessing
from pathlib import Path

mindtct_path = Path(__file__).parent / "mindtct"
def _mindtct_runner(file):
    if "mindtct" in str(file):
        return
    try:
        output_folder = Path(file.parent / f"mindtct_{file.stem}")
        output_folder.mkdir(exist_ok=True, parents=True)
        subprocess.run(f"./mindtct -b -m1 {file} {output_folder / file.stem}", cwd=Path(__file__).parent, shell=True)

    except Exception as e:
        print(f"Exception {e} while processing: {output_folder}")
        return

def mindtct_runner(data_folder: Path, multiprocess: bool = True):
    files = [x.absolute() for x in data_folder.rglob("*.jpg")]
    if multiprocess:
        pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
        pool.map(_mindtct_runner, files)
    else:
        _mindtct_runner(files)
