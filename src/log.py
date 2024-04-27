import logging
import os
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Custom formatter to add color to log messages based on their severity."""
    COLORS = {
        'INFO': '\033[94m',  # Blue
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'DEBUG': '\033[92m',  # Green
        'CRITICAL': '\033[95m',  # Magenta
    }

    def format(self, record):
        log_fmt = '%(asctime)s [%(levelname)s] %(message)s'
        formatter = logging.Formatter(log_fmt)
        formatted_message = formatter.format(record)
        color = self.COLORS.get(record.levelname, '\033[0m')  # Default to no color
        return f'{color}{formatted_message}\033[0m'

class LevelFilter(logging.Filter):
    """Filter that only allows messages of a specific log level."""
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

def setup_logging():
    log_dir = os.getenv('LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Define log levels for separate files
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # Set up file handlers for each log level with appropriate filters
    for level_name, level in levels.items():
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file_name = f'{date_str}-{level_name}-log.txt'
        log_file_path = os.path.join(log_dir, log_file_name)

        file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.addFilter(LevelFilter(level))  # Ensure only logs of the specific level are handled
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(file_handler)

    # Stream handler with custom formatting for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(logging.INFO)  # Display all levels of logs on console
    logger.addHandler(console_handler)

    return logger

def disable_logging():
    logging.disable(logging.CRITICAL)

logger = setup_logging()
