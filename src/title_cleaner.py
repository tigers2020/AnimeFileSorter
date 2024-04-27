import re
import os
from log import logger
import regex

class TitleCleaner:
    def __init__(self):
        """
        self.patterns_to_remove = [re.compile(pattern) for pattern in [
            "\[\w+\]|\(\d{3,4}p\)|\[\w+\]$",
            r'\b(720|1080|1920x1080|1280x720)[pi]?\b', r'\b(x|H).264\b', # Combined H.264 patterns
            r'\b(x|H)264\b', r'\bNanDesuKa\b',
            r'\bFLAC\b', 'BDrip', r'\bWEB\b', r'\bBD\b|\brip\b|\bdrip\b',
            r'\.\w+$', r'\[\w+\]', r'\d{1,2}화', r' - \d+', r' \d{4}',
            r'\[[^\]]*\]|\([^)]*\)|\{[^}]*\}', r'S\d+E\d+', r'EP\d+',
            r'-\s*\d{1,2}', r'\b\d{1,2}\b', r'\bRAW\b|\bEND\b', r'[:"]',
            r'[^a-zA-Z\uAC00-\uD7AF\s]+'
        ]]
        self.anime_title_with_number_pattern = re.compile(r'(?P<anime_title>[a-zA-Z ]+) - \d+')
        """
                # Comprehensive regex patterns covering all specified cases
        self.patterns_to_remove = [
            # Combine episode and season patterns into one pattern using non-capturing groups
            regex.compile(r'(?:S\d+E\d+|S\d+|EP\d+|\d{1,2}x\d+|Part\d+|Season \d+|\d+기|\d+화).*', regex.IGNORECASE),
            # Combine resolutions and video codecs
            regex.compile(r'\b(?:\d{3,4}p|\d{3,4}[xX]\d{3,4}|[Hx]\s*\.?\s*264|HEVC|AVC)\b', regex.IGNORECASE),
            # Combine all source types into one pattern
            regex.compile(r'\b(?:RAW|END|FLAC|WEB|BluRay|BDrip|BDRip|DVD|DVDrip|HDRip).*\b', regex.IGNORECASE),
            # Combine miscellaneous and less common tags
            regex.compile(r'\b(?:AAC|Chap|sp|XviD|AC3|NCOP|AC3_Simu|K2r|2ST-EiN|REALOVE：REALIFE|OP|ext)\b', regex.IGNORECASE),
            # Specific unwanted tags and numeric patterns
            regex.compile(r'\s*-\s*(?:NanDesuKa|KyangBang)\s*|2AUDIO', regex.IGNORECASE),
            # Regular expressions for brackets and punctuation marks
            regex.compile(r'\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]|<[^<>]*>|『[^『』]*』|「[^「」]*」'),
            # Regex to remove trailing numbers from 00 to 99 at the end of a title
            regex.compile(r'\b\d{2}\b$', regex.IGNORECASE),
            # Episode info with specific formats
            regex.compile(r'- \d{1,2}v\d+|- \d+.\d+|- \d+.*', regex.IGNORECASE)
        ]


        self.anime_title_with_number_pattern = re.compile(r'(?P<anime_title>[a-zA-Z ]+) - \d+')

    def clean_title(self, file_name):
        # Extract the base filename without extension
        base_name, _ = os.path.splitext(file_name)
        logger.info(f'Original base name: {base_name}')
        
        # replace dots to space first
        base_name = regex.sub(r'\.', ' ', base_name)
        # Further remove unwanted patterns
        cleaned_name = self.remove_patterns(base_name)
        logger.info(f'Cleaned name: {cleaned_name}')
        
        # Sanitize the base name
        sanitized_name = self.sanitize_name(cleaned_name)
        logger.info(f'Sanitized name: {sanitized_name}')

        return sanitized_name.strip()

    def sanitize_name(self, name):
        # Strip invalid file system characters from the name
        # Windows disallows \ / :： * ? " < > | and control characters (0x00-0x1F)
        invalid_chars = r'[_.\\/:*!?"<>|\x00-\x1F]'
        name = regex.sub(invalid_chars, ' ', name)  # Remove invalid characters completely

        # Normalize whitespace and remove standalone dashes
        name = regex.sub(r'\s+', ' ', name).strip()
        name = regex.sub(r'\s*-\s*(?=\s|$)', ' ', name).strip()  # Removes standalone dashes


        return name.strip()


    def remove_patterns(self, name):
        for pattern in self.patterns_to_remove:
            name = pattern.sub(' ', name)
        return name.strip()

    def extract_resolution(self, file_name):
        match = re.search(r'(\d{3,4})[xX](\d{3,4})', file_name)
        if match:
            resolution = f"{match.group(2)}p"
        else:
            match = re.search(r'(\d{3,4}p)', file_name)
            resolution = match.group(0) if match else 'Unknown'
        return resolution

    def find_korean_or_english_title(self, titles):
        korean_range = re.compile('[\uAC00-\uD7AF]+')  # Korean characters
        english_range = re.compile('[a-zA-Z]+')       # English characters
        for title in titles:
            if re.search(korean_range, title) and not re.search(english_range, title):
                logger.info(f"found Korean title {title}")
                return title
        return None

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
        translated_title = translate_title_to_korean(raw_title)
        logger.warning(f"Translated title to Korean: {translated_title}")
        return translated_title
