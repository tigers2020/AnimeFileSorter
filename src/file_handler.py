import os
import shutil

from src.log import logger


class FileHandler:
    FILE_TYPES = {
        ".doc": "documents",
        ".docx": "documents",
        ".txt": "documents",
        ".pdf": "documents",
        ".zip": "subtitles",
        ".rar": "subtitles",
    }

    def __init__(self, base_dir, output_dir):
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.dirs = {
            "organized": output_dir,
            "documents": os.path.join(output_dir, "documents"),
            "subtitles": os.path.join(output_dir, "subtitles"),
            "duplicated": os.path.join(output_dir, "duplicated"),
        }
        self._create_directories()

    def _create_directories(self):
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def move_file(self, file_path, year, quarter, title, resolution):
        year_folder = str(year) if year else "Unknown Year"
        quarter_folder = quarter or "Unknown Quarter"
        organized_dir = os.path.join(self.dirs["organized"], year_folder, quarter_folder, title.strip(), resolution)
        os.makedirs(organized_dir, exist_ok=True)

        extension = os.path.splitext(file_path)[1].lower()
        dir_type = self.FILE_TYPES.get(extension)
        target_dir = self.dirs.get(dir_type, organized_dir)
        base_name = os.path.basename(file_path)
        target_file_path = os.path.join(target_dir, base_name)

        try:
            if os.path.exists(target_file_path):
                shutil.move(file_path, os.path.join(self.dirs["duplicated"], base_name))
                logger.info(f"Moved to duplicated: {file_path} -> {os.path.join(self.dirs['duplicated'], base_name)}")
            else:
                shutil.move(file_path, target_file_path)
                logger.info(f"Moved: {file_path} -> {target_file_path}")
        except Exception as e:
            logger.error(f"Error moving {file_path}: {e}")

        self.remove_empty_directories(os.path.dirname(file_path))

    @staticmethod
    def remove_empty_directories(path):
        if not os.path.isdir(path):
            return

        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                dir_path = os.path.join(root, name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logger.info(f"Deleted empty directory: {dir_path}")
