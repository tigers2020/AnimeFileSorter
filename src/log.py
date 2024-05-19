import os
import logging
from datetime import datetime


class CustomFormatter(logging.Formatter):
    # Removed color codes for better compatibility with different terminals
    LOG_FMT = '%(asctime)s [%(levelname)s] %(message)s'

    def format(self, record):
        formatter = logging.Formatter(self.LOG_FMT)
        return formatter.format(record)


class LevelFilter(logging.Filter):
    """
    Custom filter.
    Allow messages from self.level and higher, unless level is DEBUG.
    In that case, only allow DEBUG
    """

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        if self.level == logging.DEBUG:
            return record.levelno == self.level
        else:
            return record.levelno >= self.level


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    for level_name, level in levels.items():
        setup_logging_for_level(level_name, level, logger)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(logging.DEBUG)  # Changed level to DEBUG from INFO
    logger.addHandler(console_handler)
    return logger


def setup_logging_for_level(level_name, level, logger):
    log_dir = os.getenv('LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file_name = f'{date_str}-{level_name}-log.txt'
    log_file_path = os.path.join(log_dir, log_file_name)
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8', delay=True)
    file_handler.setLevel(level)
    file_handler.addFilter(LevelFilter(level))
    file_handler.setFormatter(logging.Formatter(CustomFormatter.LOG_FMT))
    logger.addHandler(file_handler)


def disable_logging():
    logging.disable(logging.CRITICAL)


logger = setup_logging()
