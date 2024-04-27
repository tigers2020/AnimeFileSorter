import requests
from log import logger  # Assuming logger is configured appropriately in the log.py module
import datetime

from dateutil import parser

class TMDbHandler:
    def __init__(self, api_key, result_language='ko'):
        self.api_key = api_key
        self.result_language = result_language
        self.base_url = "https://api.themoviedb.org/3/"

    def _make_request(self, endpoint, params):
        """ Helper method to make API requests and handle responses. """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def search(self, content_type, query, language=None):
        """ General search method for both movies and TV shows. """
        if language is None:
            language = self.result_language
        endpoint = f"search/{content_type}"
        params = {'api_key': self.api_key, 'language': language, 'query': query}
        
        logger.info(f"Searching for {content_type}: '{query}' with language setting: '{language}'")
        response = self._make_request(endpoint, params)
        if response and 'results' in response and response['results']:
            logger.info(f"Search successful for {content_type} with {query}")
        else:
            logger.warning(f"No results found for {content_type} with {query}")
        return response
    def search_media(self, title):
        for content_type in ['tv', 'movie']:
            search_results = self.search(content_type, title)
            if search_results and search_results['results']:
                return search_results
        # If no results found for either type, raise an exception
        logger.error(f"No results found for {title}")
        return None
        #raise Exception(f"No results found for title: {title}")

    def get_titles(self, search_results):
        """Extract movie or TV show titles from search results."""
        if not search_results or 'results' not in search_results or not search_results['results']:
            return None  # Return None if there are no results to process
        
        titles = [result['title'] if 'title' in result else result['name'] for result in search_results['results']]
        logger.info(f"Extracted {len(titles)} titles from search results: {titles}")
        return titles[0] if titles else None

    # Existing methods like get_movie(), get_year_quarter(), etc., would remain largely unchanged.


    def get_year_quarter(self, search_results):
        """Extract the year and quarter from search results that might include multiple entries."""
        date_str = None
        if search_results is not None:
            # Handling multiple results typically from a search query
            if 'results' in search_results and search_results['results']:
                for result in search_results['results']:
                    if 'release_date' in result and result['release_date']:
                        date_str = result['release_date']
                        break
                    elif 'first_air_date' in result and result['first_air_date']:
                        date_str = result['first_air_date']
                        break

        if not date_str:
            logger.warning("No date found in search results.")
            return None, None  # No valid date found

        # Parsing the date and determining the quarter
        try:
            date = parser.parse(date_str)
            year = date.year
            quarter = self.determine_quarter(date.month)
            return year, quarter
        except ValueError:
            logger.error(f"Failed to parse date: {date_str}")
            return None, None

    def determine_quarter(self, month):
        """Determine the quarter from a month."""
        if 1 <= month <= 3:
            return 'first_quarter'
        elif 4 <= month <= 6:
            return 'second_quarter'
        elif 7 <= month <= 9:
            return 'third_quarter'
        elif 10 <= month <= 12:
            return 'fourth_quarter'
