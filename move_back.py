from pathlib import Path
import shutil
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from log import logger

def move_files_to_animations(source_dir, target_dir):
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)  # Create target directory if not exists

    def handle_collision(target_file):
        """Generates a new path for files that would otherwise collide."""
        count = 1
        while target_file.exists():
            target_file = target_file.with_name(f"{target_file.stem} ({count}){target_file.suffix}")
            count += 1
        return target_file

    for file_path in source_path.rglob('*'):
        if file_path.is_file():  # Ensure it's a file
            target_file_path = target_path / file_path.name
            target_file_path = handle_collision(target_file_path)
            shutil.move(str(file_path), str(target_file_path))
            logger.info(f"Moved {file_path} to {target_file_path}")

    # Remove empty directories after processing all files
    for dir_path in source_path.rglob('*'):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            dir_path.rmdir()
            logger.debug(f"Removed empty directory: {dir_path}")

if __name__ == "__main__":
    move_files_to_animations('.\\organized', '.\\Animations')
