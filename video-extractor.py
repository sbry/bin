import time, os, re
from pathlib import Path
from shutil import copyfile

##
# always the same target
home = Path(os.getenv("HOME"))
target = home / "Videos"

##
# different sources
source = home / "Pictures"
source = Path("D:/")
source = Path("E:/")
source = Path("P:/isolde/Eigene Bilder Notebook/")

def get_video_files(p):
    ext = {'.avi', '.mp4', '.vob', '.mov'                  }
    for path in p.rglob(r'*'):
        if path.suffix.lower() in ext:
            yield(path)

def process_video_file(filename):
    target_filename = target / filename.resolve().relative_to(source)
    # return target_filename
    if target_filename.exists():
        return target_filename
    target_filename.parent.mkdir(parents=True, exist_ok=True)
    # cant rename beyond filesystems
    copyfile(filename, target_filename)
    filename.unlink(missing_ok=True)
    # filename.rename(target_filename)
    return target_filename

if __name__ == "__main__":
    ##
    # Test
    # p = Path('C:/Users/Isolde/Pictures/.Picasa3Temp_18/Screenshot_20190418-172441_WhatsApp.jpg')
    # print(process_video_file(p))
    
    for f in get_video_files(source):
        print(f)
        t = process_video_file(f)
        print(t)
    pass
