import os
import shutil
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from log import logger

def move_files_to_animations(source_dir, target_dir):
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir, topdown=False):  # topdown=False to start from the innermost directories
        for file in files:
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_dir, file)

            # Handle potential file name collisions in target directory
            if os.path.exists(target_file_path):
                base, extension = os.path.splitext(file)
                count = 1
                new_base = f"{base} ({count})"
                new_target_file_path = os.path.join(target_dir, f"{new_base}{extension}")

                while os.path.exists(new_target_file_path):
                    count += 1
                    new_base = f"{base} ({count})"
                    new_target_file_path = os.path.join(target_dir, f"{new_base}{extension}")

                target_file_path = new_target_file_path

            # Move the file
            shutil.move(source_file_path, target_file_path)
            logger.info(f"Moved {source_file_path} to {target_file_path}")

        # After moving all files, remove the empty directories
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            if not os.listdir(dir_path):  # Check if the directory is empty
                os.rmdir(dir_path)
                logger.info(f"Removed empty directory: {dir_path}")

# Example usage
if __name__ == "__main__":
    organized_dir = '.\\organized'
    animations_dir = '.\\Animations'
    move_files_to_animations(organized_dir, animations_dir)
