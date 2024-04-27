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
            regex.compile(r'\s*-\s*NanDesuKa\s*|\s*-\s*KyangBang\s*', regex.IGNORECASE),  # Specific unwanted tag
            regex.compile(r'2AUDIO', regex.IGNORECASE),
            re.compile(r'\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]|<[^<>]*>|『[^『』]*』|「[^「」]*」'),
            regex.compile(r'S\d+E\d+.*', regex.IGNORECASE),  # Season and episode info like "S01E02"
            regex.compile(r'S\d+', regex.IGNORECASE),  # Season info like "S01"
            regex.compile(r'Part\d+', regex.IGNORECASE), # Season info like "Part2"
            regex.compile(r'EP\d+.*', regex.IGNORECASE),  # Episode info like "EP01"
            regex.compile(r'\d{1,2}x\d+.*', regex.IGNORECASE),  # Episode info like "1x01"
            regex.compile(r'\d+기', regex.IGNORECASE),  # Episode info like "1기"
            regex.compile(r'Season \d+.*', regex.IGNORECASE),  # Episode info like "1기"
            regex.compile(r'\d+화.*', regex.IGNORECASE),  # Episode info like "1기"
            regex.compile(r'- \d+.*', regex.IGNORECASE),  # Episode info like " - 01"
            regex.compile(r'- \d{1,2}v\d+', regex.IGNORECASE),  # Episode info like " - 01v2"
            regex.compile(r'- \d+.\d+', regex.IGNORECASE),  # Episode info like " - 01.5"
            regex.compile(r'\b\d{3,4}p\b', regex.IGNORECASE),  # Resolution like "1080p"
            regex.compile(r'\b\d{3,4}[xX]\d{3,4}\b', regex.IGNORECASE), # Resolution like "1920x1080"
            regex.compile(r'\b(?:[Hx]\s*\.?\s*264)\b|\bHEVC\b|\bAVC\b', regex.IGNORECASE),  # Video codecs
            regex.compile(r'\bRAW.*\b|\bEND.*\b|\bFLAC.*\b|\bWEB.*\b|\bBluRay.*\b|\bBDrip.*\b|\bBDRip.*\b|\bDVD.*\b|\bDVDrip.*\b|\bHDRip.*\b', regex.IGNORECASE),  # Source types
            regex.compile(r'\bAAC.*\b|\bChap.*\b|\bsp\b', regex.IGNORECASE),
            regex.compile(r'\bXviD.*\b|\bAC3.*\b|\bNCOP.*\b|\bAC3_Simu.*\b|\bK2r.*\b|\b2ST-EiN.*\b', regex.IGNORECASE),
            regex.compile(r'\bREALOVE：REALIFE\b|\bOP\b|\bext\b', regex.IGNORECASE),
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
