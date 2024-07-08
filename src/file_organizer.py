import os
from src.tmdb_handler import TMDBHandler
from src.title_cleaner import TitleCleaner
from src.log import logger
from src.file_handler import FileHandler


class FileOrganizer:
    def __init__(self, config):
        self.tmdb_handler = TMDBHandler(config.get('api_key', ''))
        self.title_cleaner = TitleCleaner()
        self.file_handler = None
        self.previous_clean_title = None
        self.previous_search_results = None

    def set_directories(self, input_dir, output_dir):
        self.file_handler = FileHandler(input_dir, output_dir)

    def process_file(self, file_path):
        filename = os.path.basename(file_path)
        logger.info(f"Processing file: {file_path}")

        try:
            clean_title = self.title_cleaner.clean_title(filename)
            resolution = self.title_cleaner.extract_resolution(filename)

            if self.previous_clean_title and clean_title == self.previous_clean_title:
                search_results = self.previous_search_results
            else:
                search_results = self.tmdb_handler.search_media(clean_title)
                self.previous_clean_title = clean_title
                self.previous_search_results = search_results

            if search_results:
                preferred_title = self.tmdb_handler.first_title_from_search_results(search_results) or "Unknown"
                preferred_title = self.title_cleaner.sanitize_name(preferred_title.strip())
                year, quarter = self.tmdb_handler.get_year_quarter(search_results)
            else:
                preferred_title = "Unknown"
                year, quarter = None, None
                logger.error(f"Unable to find TV series or movies for: {filename}", exc_info=True)

            self.file_handler.move_file(file_path, year, quarter, preferred_title, resolution)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)