import sys, time, os, re, logging, shutil
###
## The point is that this stuff runs on windows linux mac like plain
# vanilla python
##
# We like pathlib
try:
    from pathlib import Path
except ImportError:
    logging.error("no pathlib means no python3, but python 3 is required")
    sys.exit()

DEBUG = False
if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:%(message)s',)
    logging.info("debug-mode and not actually doping anything")
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:%(message)s',)
##
# handle args
try:
    source = Path(sys.argv[1])
    try:
        target = Path(sys.argv[2])
    except IndexError:
        target = source.parent  / "Videos"
        logging.warning('target is now %s', target)
except IndexError:
    logging.error('please provide at least a source-dir')
    sys.exit()

logging.debug("source is %s", source)
logging.debug("target dir is %s", target)

if not DEBUG:
    target.mkdir(parents=True, exist_ok=True)
    
def get_video_files(p):
    ext = {'.avi', '.mp4', '.vob', '.mov'}
    for path in p.rglob(r'*'):
        if path.suffix.lower() in ext:
            yield(path)

def get_target_filename(source_filename):
    """make a relative path and prepend the target, because very often

    the directory-name contains important meta-information, and also the
    video-filenames might be the same.  so
    /source/test-name/video-file.mov becomes
    /target/test-name/video-file.mov
    """
    target_filename = target / source_filename.resolve().relative_to(source)
    logging.debug('%s -> %s', source_filename, target_filename)
    return target_filename
    
def process_video_file(source_filename):
    target_filename = get_target_filename(source_filename)
    if target_filename.exists():
        logging.info('target already exists %s, bailing out', target_filename)  
        return

    if DEBUG:
        logging.info('NOT copying %s -> %s, debug, bailing out',
                         source_filename, target_filename)
        return

    logging.info('%s -> %s', source_filename, target_filename)
    
    target_filename.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_filename.rename(target_filename)
        logging.info('renamed')  
    except:
        shutil.copyfile(source_filename, target_filename)
        source_filename.unlink()
        logging.info('copied and unlinked')  


if __name__ == "__main__":
    for f in get_video_files(source):
        process_video_file(f)

