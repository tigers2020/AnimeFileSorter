import os
import shutil
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from log import logger


def handle_collision_and_move_file(file_path, target_path):
    """Handles file collision and moves the file from source to target."""
    count = 1
    target_file_path = target_path / file_path.name
    while target_file_path.exists():
        target_file_path = target_file_path.with_name(f"{target_file_path.stem} ({count}){target_file_path.suffix}")
        count += 1
    if not target_file_path.exists():
        shutil.move(str(file_path), str(target_file_path))
        logger.info(f"Moved {file_path} to {target_file_path}")


def remove_empty_directories(source_path):
    """Removes all empty directories within the source path."""
    empty_directories_found = True
    while empty_directories_found:
        empty_directories = [dir_path for dir_path in source_path.rglob('*') if
                             dir_path.is_dir() and not any(dir_path.iterdir())]
        if not empty_directories:  # If no empty directories are found, exit the loop
            empty_directories_found = False
        for dir_path in empty_directories:
            try:
                dir_path.rmdir()
                logger.debug(f"Removed empty directory: {dir_path}")
            except (PermissionError, OSError) as e:
                logger.error(f"Failed to remove directory: {dir_path}, error: {str(e)}")


def move_files_to_animations(source_dir, target_dir):
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    if not source_path.exists():
        logger.error("Source directory does not exist.")
        return
    elif target_path in source_path.resolve().parents:
        logger.error("Target directory should not be a subdirectory of the source directory.")
        return
    target_path.mkdir(parents=True, exist_ok=True)  # Create target directory if not exists
    for file_path in source_path.rglob('*'):
        if file_path.is_file():  # Ensure it's a file
            try:
                handle_collision_and_move_file(file_path, target_path)
            except (PermissionError, OSError) as e:
                logger.error(f"Failed to move file: {file_path}, error: {str(e)}")
    remove_empty_directories(source_path)


if __name__ == "__main__":
    move_files_to_animations('.\\organized', '.\\Animations')
