import shutil
from pathlib import Path
import glob
import os
from helpers import slugify, reset_path, get_files


def process_images(source_path: Path, target_path: Path):
    print("\n\n==== Processing images")
    # Process images by combining languages into a single dir
    files = get_files(source_path, ('*.jpg', '*.jpeg', '*.gif', '*.JPG', '*.JPEG', '*.GIF'))
    print(files)
    for each_file in files:
        file_name = each_file.parts
        new_name = slugify(file_name[-1])
        shutil.copy(each_file, target_path.joinpath(new_name))
        print(new_name)


def process_audio(source_path: Path, target_path: Path):
    print("\n\n==== Processing audio")
    files = get_files(source_path, '*.mp3')
    print(files)
    for each_file in files:
        file_name = each_file.parts
        new_name = slugify(file_name[-1])
        shutil.copy(each_file, target_path.joinpath(new_name))
        print(new_name)


if __name__ == "__main__":
    source_path = Path("../media")
    target_audio_path = Path("../output/audio")
    target_image_path = Path("../output/images")

    reset_path(target_audio_path)
    reset_path(target_image_path)

    process_audio(source_path=source_path, target_path=target_audio_path)
    process_images(source_path=source_path, target_path=target_image_path)
