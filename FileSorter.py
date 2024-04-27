import json
import os
import shutil
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tqdm import tqdm
from tmdb_handler import TMDbHandler
from title_cleaner import TitleCleaner
from log import logger


class FileOrganizer:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        self.base_dir = config['base_dir']
        self.tmdb_handler = TMDbHandler(config['api_key'])
        self.title_cleaner = TitleCleaner()
        self.initialize_directories()

    def initialize_directories(self):
        """Create necessary directories if they do not exist."""
        self.dirs = {
            "subtitles": os.path.join(self.base_dir, "subtitles"),
            "documents": os.path.join(self.base_dir, "documents"),
            "others": os.path.join(self.base_dir, "others"),
            "duplicated": os.path.join(self.base_dir, "duplicated"),
            "organized": os.path.join(self.base_dir, "organized")
        }
        for path in self.dirs.values():
            os.makedirs(path, exist_ok=True)

    def organize_files(self, directory):
        full_path = os.path.join(self.base_dir, directory)
        files = os.listdir(full_path)
        logger.info("Starting the file organization process.")
        for filename in tqdm(files, desc="Organizing files", unit="file"):
            self.process_file(full_path, filename)
        logger.info("File organization process completed successfully.")

    def process_file(self, directory, filename):
        file_path = os.path.join(directory, filename)
        clean_title = self.title_cleaner.clean_title(filename)
        resolution = self.title_cleaner.extract_resolution(filename)
        
        # If the resolution is 1080p, delete the file and continue with the next one.
        if resolution == "1080p":
            os.remove(file_path)
            logger.warning(f"Deleted {file_path} due to undesired resolution (1080p).")
            return  # Skip further processing of this file

        search_results = self.search_until_found(clean_title, filename)
        preferred_title = "Unknown"
        if search_results:
            preferred_title = self.tmdb_handler.get_titles(search_results) or "Unknown"
            preferred_title = self.title_cleaner.sanitize_name(preferred_title.strip())
            logger.info(f"Organizing files for title: {preferred_title}")
        else:
            logger.error(f"Unable to find TV series or movies for any version of: {filename}")
        self.move_file_to_organized_dir(file_path, resolution, preferred_title, search_results)

    def search_until_found(self, title, original_filename):
        """Attempts to find media by title, shortening the title until a match is found."""
        current_title = title
        while current_title:
            search_results = self.tmdb_handler.search_media(current_title)
            if search_results and search_results['results']:
                return search_results
            current_title = ' '.join(current_title.split()[:-1])  # Shorten title by removing the last word
            if current_title:  # Only log if there's still a title to retry
                logger.info(f"Retrying with shortened title: {current_title}")

        logger.error(f"No TV series or movies found for: {original_filename}")
        return None

    def move_file_to_organized_dir(self, file_path, resolution, title, search_results):
        year, quarter = self.tmdb_handler.get_year_quarter(search_results) if search_results else (None, None)
        quarter_folder = quarter or "Unknown Quarter"
        year_folder = str(year) if year else "Unknown Year"
        organized_dir = os.path.join(self.dirs["organized"], year_folder, quarter_folder, title, resolution)
        os.makedirs(organized_dir, exist_ok=True)

        # File type handling
        extension = os.path.splitext(file_path)[1].lower()
        file_types = {
            ".doc": self.dirs["documents"],
            ".docx": self.dirs["documents"],
            ".txt": self.dirs["documents"],
            ".pdf": self.dirs["documents"],
            ".zip": self.dirs["subtitles"],
            ".rar": self.dirs["subtitles"]
        }
        target_dir = file_types.get(extension, organized_dir)
        target_file_path = os.path.join(target_dir, os.path.basename(file_path))

        # Move or duplicate file handling
        try:
            if os.path.exists(target_file_path):
                shutil.move(file_path, os.path.join(self.dirs["duplicated"], os.path.basename(file_path)))
                logger.warning(f"Moved {file_path} to duplicated because a file with the same name exists.")
            else:
                shutil.move(file_path, target_file_path)
                logger.info(f"Moved {file_path} to {target_file_path}")
        except Exception as e:
            logger.error(f"Error moving {file_path} to {target_file_path}: {e}")

if __name__ == "__main__":
    organizer = FileOrganizer("./src/config.json")
    organizer.organize_files("Animations")
