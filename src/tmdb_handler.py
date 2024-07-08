import math

import requests
from dateutil import parser

from src.log import logger  # Assuming logger is configured appropriately in the log.py


class TMDBHandler:
    def __init__(self, api_key, result_language='ko'):
        self.api_key = api_key
        self.result_language = result_language
        self.base_url = "https://api.themoviedb.org/3/"

    def _make_request(self, endpoint, params):
        """ Helper method to make API requests and handle responses. """
        url = f"{self.base_url}{endpoint}"
        response = None

        try:
            response = requests.get(url, params=params)
            if response is not None:
                response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
        # Always return, even when requests throws an exception
        return response.json() if response else None

    def search(self, content_type, query, language=None):
        """ General search method for both movies and TV shows. """
        endpoint = f"search/{content_type}"
        params = {'api_key': self.api_key, 'language': language or self.result_language, 'query': query}
        response = self._make_request(endpoint, params)
        if self.has_search_results(response):
            logger.info(f"Search successful for {content_type} with {query}")
        else:
            logger.warning(f"No results found for {content_type} with {query}")
        return response

    def has_search_results(self, search_response):
        """ Check if a given search response has results or not """
        return bool(search_response.get('results'))

    def search_media(self, title, content_types=['tv', 'movie']):
        for content_type in content_types:
            search_results = self.search(content_type, title)
            if self.has_search_results(search_results):
                return search_results
        logger.error(f"No results found for {title}")
        return None

    def first_title_from_search_results(self, search_results):
        """Extract first movie or TV show title from search results."""
        if not self.has_search_results(search_results):
            return None
        titles = [result.get('title') or result.get('name') for result in search_results['results'] if
                  result.get('title') or result.get('name')]
        logger.info(f"Extracted {len(titles)} titles from search results: {titles}")
        return titles[0] if titles else None

    def get_year_quarter(self, search_results):
        """Extract the year and quarter from search results that might include multiple entries."""
        date_str = None
        if self.has_search_results(search_results):
            for result in search_results['results']:
                if result.get('release_date'):
                    date_str = result.get('release_date')
                    break
                if result.get('first_air_date'):
                    date_str = result.get('first_air_date')
                    break
        if not date_str:
            logger.warning("No date found in search results.")
            return None, None  # No valid date found
        return self.parse_date_string(date_str)

    def parse_date_string(self, date_str):
        """Parse the given date as string and return year and quarter"""
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
        return f'{math.ceil(month / 3)}_quarter'
