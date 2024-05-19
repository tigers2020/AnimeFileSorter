import json
import os
import shutil
from difflib import SequenceMatcher

from src.log import logger
from src.title_cleaner import TitleCleaner
from src.tmdb_handler import TMDbHandler


class FileHandler:
    FILE_TYPES = {
        ".doc": "documents",
        ".docx": "documents",
        ".txt": "documents",
        ".pdf": "documents",
        ".zip": "subtitles",
        ".rar": "subtitles",
    }

    def __init__(self, tmdb_handler, titleCleaner, base_dir):
        self.tmdb_handler = tmdb_handler
        self.title_cleaner = titleCleaner
        self.dirs = {
            "animations": os.path.join(base_dir, "animations"),
            "organized": os.path.join(base_dir, "organized"),
            "documents": os.path.join(base_dir, "documents"),
            "subtitles": os.path.join(base_dir, "subtitles"),
            "duplicated": os.path.join(base_dir, "duplicated"),
        }

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
        year, quarter = self.tmdb_handler.get_year_quarter(search_results) if search_results else (None, None)
        quarter_folder = quarter or "Unknown Quarter"
        year_folder = str(year) if year else "Unknown Year"
        organized_dir = os.path.join(self.dirs["organized"], year_folder, quarter_folder, title.strip(), resolution)

        if organized_dir not in self.dirs:
            try:
                os.makedirs(organized_dir, exist_ok=True)
            except OSError:
                logger.error(f"Failed to create directory: {organized_dir}")
            else:
                self.dirs[organized_dir] = True

        extension = os.path.splitext(file_path)[1].lower()
        dir_type = self.FILE_TYPES.get(extension)
        target_dir = self.dirs.get(dir_type, organized_dir)
        base_name = os.path.basename(file_path)
        target_file_path = os.path.join(target_dir, base_name)

        action = 'Moved'
        try:
            if os.path.exists(target_file_path):
                shutil.move(file_path, os.path.join(self.dirs["duplicated"], base_name))
                action = 'Moved to duplicated because a file with the same name exists'
            else:
                shutil.move(file_path, target_file_path)
        except Exception as e:
            logger.error(f"Error moving {file_path} to {target_file_path}: {e}")
        else:
            logger.info(f"{action} {file_path} to {target_file_path}")
            self.remove_empty_directories(os.path.dirname(file_path))

    def remove_empty_directories(self, path):
        if not os.path.isdir(path):
            return

        # remove empty subdirectories
        files = os.listdir(path)

        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self.remove_empty_directories(fullpath)

        # Modify the condition here
        files = os.listdir(path)
        if len(files) == 0 and 'Animations' not in path.split(os.path.sep):
            os.rmdir(path)
            logger.info(f"Deleted empty directory: {path}")


class FileOrganizer:
    # Constructor of the FileOrganizer class.
    def __init__(self, config_path):
        # Opening and loading configuration from a JSON file.
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            logger.error(f"File {config_path} not found")
            self.config = {}
        # Setting the base directory where files are stored, based on the config.
        self.base_dir = self.config['base_dir']
        # Creating instances of TMDbHandler and TitleCleaner using configurations.
        self.tmdb_handler = TMDbHandler(self.config['api_key'])
        self.title_cleaner = TitleCleaner()
        self.previous_clean_title = None
        self.previous_search_results = None
        self.file_handler = FileHandler(self.tmdb_handler, self.title_cleaner, self.base_dir)

    def process_file(self, directory, filename):
        """Processes each file individually, determining its fate based on its contents and metadata."""
        # Constructing the full path to the file.
        file_path = os.path.join(directory, filename)
        logger.info(f"Processing file: {file_path}")
        # Cleaning and extracting relevant information from the filename.
        clean_title = self.title_cleaner.clean_title(filename)
        resolution = self.title_cleaner.extract_resolution(filename)
        search_results = []

        # Searching for the file's metadata using its title.

        if self.previous_clean_title is not None and SequenceMatcher(None, clean_title,
                                                                     self.previous_clean_title).ratio() > 0.8:
            logger.info(f"Skipping title: {clean_title} as it is similar to previous title {self.previous_clean_title}")
            if self.previous_search_results is not None:
                search_results = self.previous_search_results

        else:
            search_results = self.file_handler.search_until_found(clean_title, filename)
            self.previous_clean_title = clean_title
            self.previous_search_results = search_results

        # Handling search results and organizing files accordingly.

        if search_results:
            preferred_title = self.tmdb_handler.first_title_from_search_results(search_results) or "Unknown"
            preferred_title = self.title_cleaner.sanitize_name(preferred_title.strip())
            logger.info(f"Organizing files for title: {preferred_title}")
        else:
            preferred_title = "Unknown"
            logger.error(f"Unable to find TV series or movies for any version of: {filename}")
            self.previous_preferred_title = preferred_title
        self.previous_preferred_title = preferred_title

        # Moving the file to an appropriate directory based on the search results.
        self.file_handler.move_file_to_organized_dir(file_path, resolution, preferred_title.strip(), search_results)


def main():
    # Initialize with your configuration file path
    file_organizer = FileOrganizer("src/config.json")
    directory = "Animations"
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Ignore directories, process only files
        if os.path.isfile(os.path.join(directory, filename)):
            # Call the process_file function on each file
            file_organizer.process_file(directory, filename)


if __name__ == "__main__":
    main()
