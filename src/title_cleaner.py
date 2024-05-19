import os

import regex

from .log import logger


class TitleCleaner:
    # Comprehensive regex patterns covering all specified cases
    PATTERNS_TO_REMOVE = [
        regex.compile(r'\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]|<[^<>]*>|『[^『』]*』|「[^「」]*」'),  # Remove all bracketed content
        regex.compile(r'(?:S\d+E\d+|S\d+|EP\d+|\d{1,2}x\d+|Part\d+|Season \d+|\d+기|\d+화).*', regex.IGNORECASE),
        # Episode and season info
        regex.compile(r'\b(?:\d{3,4}p|\d{3,4}[xX]\d{3,4}|[Hx]\s*\.?\s*264|HEVC|AVC)\b', regex.IGNORECASE),
        # Resolutions and codecs
        regex.compile(r'\b(?:RAW|END|FLAC|WEB|BluRay|BDrip|BDRip|DVD|DVDrip|HDRip).*\b', regex.IGNORECASE),
        # Source types
        regex.compile(r'\b(?:AAC|Chap|sp|XviD|AC3|NCOP|AC3_Simu|K2r|2ST-EiN|REALOVE：REALIFE|OP|ext)\b',
                      regex.IGNORECASE),  # Misc tags
        regex.compile(r'- \d{1,2}v\d+|- \d+.\d+|- \d+.*', regex.IGNORECASE)  # Numeric episode formats
    ]

    def __init__(self):
        pass

    def clean_title(self, file_name):
        base_name = os.path.splitext(file_name)[0]
        logger.info(f'Original base name: {base_name}')
        base_name = regex.sub(r'\.', ' ', base_name)  # Replace dots with spaces
        cleaned_name = self.remove_patterns(base_name)
        sanitized_name = self.sanitize_name(cleaned_name)
        logger.info(f'Sanitized name: {sanitized_name}')
        return sanitized_name

    @staticmethod
    def sanitize_name(name):
        # Remove invalid filesystem characters and normalize whitespace
        name = regex.sub(r'[\\/:*!\?"<>|\x00-\x1F]', ' ', name)  # Remove invalid characters
        name = regex.sub(r'\s+', ' ', name)  # Normalize spaces
        name = regex.sub(r'\s*-\s*(?=\s|$)', ' ', name)  # Remove standalone dashes
        # Remove trailing two-digit number (00-99) at the end of the title
        name = regex.sub(r'\b\d\b$', '', name)
        return name

    def remove_patterns(self, name):
        # Apply all regex patterns to remove unwanted text
        for pattern in self.PATTERNS_TO_REMOVE:
            name = pattern.sub(' ', name)
        return name

    @staticmethod
    def extract_resolution(file_name):
        # Extract resolution using regex, handling cases when not found
        match = regex.search(r'(\d{3,4})[xX](\d{3,4})', file_name)
        if match:
            return f"{match.group(2)}p"
        match = regex.search(r'(\d{3,4}p)', file_name)
        return match.group(0) if match else 'Unknown'

    # Just assuming the translate_title_to_korean is a function available in the global scope
    def get_preferred_title(self, raw_title, anime_data):
        if anime_data:
            synonyms = anime_data.get("synonyms", [])
            all_titles = synonyms + [anime_data.get('clean_title', ''), anime_data.get('title', '')]
            preferred_title = self.find_korean_or_english_title(all_titles)
            if preferred_title:
                logger.info(f"Using preferred title from JSON synonyms: {preferred_title}")
                return preferred_title
            logger.info(f"Using main title from JSON: {anime_data['clean_title']}")
            return anime_data["clean_title"]

