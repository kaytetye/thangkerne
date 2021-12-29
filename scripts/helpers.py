import os
import re
import unicodedata
import shutil

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    # split off the file extension first though
    basename, ext = os.path.splitext(value)
    value = str(basename)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    value = re.sub(r'[-_\s]+', '-', value).strip('-_')
    return f"{value}{ext}".lower()

def reset_path(dir_path):
    if dir_path.is_dir():
        shutil.rmtree(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)

def get_files(source_path, extensions):
    all_files = []
    if type(extensions) is tuple:
        for ext in extensions:
            ext = f"**/{ext}"
            print(ext)
            all_files.extend(source_path.glob(ext))
    elif type(extensions) is str:
        ext = f"**/{extensions}"
        all_files.extend(source_path.glob(ext))
    return all_files
