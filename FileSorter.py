import json
import os
import shutil
import sys
from tqdm import tqdm

# Adding the 'src' directory to the system path to allow importing custom modules from it.
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importing custom modules that handle different functionalities of the application.
from tmdb_handler import TMDbHandler
from title_cleaner import TitleCleaner
from log import logger

class FileOrganizer:
    # Constructor of the FileOrganizer class.
    def __init__(self, config_path):
        # Opening and loading configuration from a JSON file.
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        # Setting the base directory where files are stored, based on the config.
        self.base_dir = self.config['base_dir']
        # Creating instances of TMDbHandler and TitleCleaner using configurations.
        self.tmdb_handler = TMDbHandler(self.config['api_key'])
        self.title_cleaner = TitleCleaner()
        # Initializing directories required for organizing files.
        self.initialize_directories()

    def initialize_directories(self):
        """Creates directories listed in the dirs dictionary if they don't exist."""
        # Mapping directory names to their full paths.
        self.dirs = {key: os.path.join(self.base_dir, name) for key, name in 
                     [("subtitles", "subtitles"), ("documents", "documents"),
                      ("others", "others"), ("duplicated", "duplicated"), 
                      ("organized", "organized")]}
        # Creating directories that don't exist using os.makedirs with exist_ok=True.
        for path in self.dirs.values():
            os.makedirs(path, exist_ok=True)

    def organize_files(self, directory):
        """Recursively handles the organization of files and directories within a specified directory."""
        full_path = os.path.join(self.base_dir, directory)
        try:
            items = os.listdir(full_path)
        except FileNotFoundError:
            logger.error(f"Directory not found: {full_path}")
            return
        logger.info(f"Starting the file organization process in {full_path}.")
        for item in tqdm(items, desc="Organizing files", unit="item"):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                self.organize_files(item_path)  # Recursively organize directories
            else:
                self.process_file(full_path, item)
        logger.info(f"File organization process completed successfully for {full_path}.")

    def process_file(self, directory, filename):
        """Processes each file individually, determining its fate based on its contents and metadata."""
        # Constructing the full path to the file.
        file_path = os.path.join(directory, filename)
        print(file_path)
        # Cleaning and extracting relevant information from the filename.
        clean_title = self.title_cleaner.clean_title(filename)
        resolution = self.title_cleaner.extract_resolution(filename)
        
        # Deleting the file if its resolution is 1080p.
        if resolution == "1080p":
            os.remove(file_path)
            logger.warning(f"Deleted {file_path} due to undesired resolution (1080p).")
            return

        # Searching for the file's metadata using its title.
        search_results = self.search_until_found(clean_title, filename)
        # Handling search results and organizing files accordingly.
        if search_results:
            preferred_title = self.tmdb_handler.get_titles(search_results) or "Unknown"
            preferred_title = self.title_cleaner.sanitize_name(preferred_title.strip())
            logger.info(f"Organizing files for title: {preferred_title}")
        else:
            preferred_title = "Unknown"
            logger.error(f"Unable to find TV series or movies for any version of: {filename}")

        # Moving the file to an appropriate directory based on the search results.
        self.move_file_to_organized_dir(file_path, resolution, preferred_title, search_results)

    def search_until_found(self, title, original_filename):
        """Searches for media by progressively shortening the title until a match is found or the title is exhausted."""
        current_title = title
        while current_title:
            search_results = self.tmdb_handler.search_media(current_title)
            if search_results and search_results['results']:
                return search_results
            # Shortening the title by removing the last word and retrying the search.
            current_title = ' '.join(current_title.split()[:-1])
            if current_title:
                logger.info(f"Retrying with shortened title: {current_title}")

        # Logging an error if no media is found for the original filename.
        logger.error(f"No TV series or movies found for: {original_filename}")
        return None

    def move_file_to_organized_dir(self, file_path, resolution, title, search_results):
        """Moves the file to an organized directory structure based on metadata."""
        # Extracting the year and quarter from search results.
        year, quarter = self.tmdb_handler.get_year_quarter(search_results) if search_results else (None, None)
        # Constructing directory names based on the year and quarter.
        quarter_folder = quarter or "Unknown Quarter"
        year_folder = str(year) if year else "Unknown Year"
        # Building the full path to the organized directory.
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
        print(target_dir)

        target_file_path = os.path.join(target_dir, os.path.basename(file_path))
        print(target_file_path)
        # Attempting to move the file to the target directory or handling duplicates.
        try:
            if os.path.exists(target_file_path):
                shutil.move(file_path, os.path.join(self.dirs["duplicated"], os.path.basename(file_path)))
                logger.warning(f"Moved {file_path} to duplicated because a file with the same name exists.")
            else:
                shutil.move(file_path, target_file_path)
                logger.info(f"Moved {file_path} to {target_file_path}")
        except Exception as e:
            # Logging any errors that occur during file movement.
            logger.error(f"Error moving {file_path} to {target_file_path}: {e}")

# Main block to run the file organizer using a specific configuration file.
if __name__ == "__main__":
    organizer = FileOrganizer("./src/config.json")
    organizer.organize_files("Animations")
