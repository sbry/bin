import sys, time, os, re, logging, shutil


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s:%(message)s',)

try:
    from pathlib import Path
except ImportError:
    logging.error("no pathlib means no python3, but python 3 is required.")
    sys.exit()


##
# always the same target
home = Path(os.getenv("HOME"))
target = home / "Videos"

logging.info("target dir is %s", target)

##
# different sources
source = home / "Pictures"

logging.info("source is %s", source)

def get_video_files(p):
    ext = {'.avi', '.mp4', '.vob', '.mov'}
    for path in p.rglob(r'*'):
        if path.suffix.lower() in ext:
            yield(path)


            
def process_video_file(filename):
    """we make a relative path and prepend the target and we do that

    because very often the directory-name contains important
    meta-information, and also the video-filenames might be the same.
    so /source/test-name/video-file.mov becomes
    /target/test-name/video-file.mov
    """
    
    target_filename = target / filename.resolve().relative_to(source)
    
    logging.info('%s -> %s', filename, target_filename)  

    if target_filename.exists():
        logging.info('Target already exists %s, bailing out', target_filename)  
        return

    logging.info('Before the copying of %s -> %s', filename, target_filename)  
    target_filename.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(filename, target_filename)
    filename.unlink(missing_ok=True)
    logging.info('%s complete and %s unlinked', target_filename, filename)  

    return

if __name__ == "__main__":
    for f in get_video_files(source):
        process_video_file(f)

