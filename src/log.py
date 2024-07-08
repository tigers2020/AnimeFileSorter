import os
import logging
from datetime import datetime
from functools import lru_cache


class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        if record.levelno == logging.ERROR:
            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            self._style._fmt = '%(asctime)s [%(levelname)s] %(message)s\nTraceback:\n%(exc_text)s'
        else:
            self._style._fmt = '%(asctime)s [%(levelname)s] %(message)s'
        return super().format(record)


class LevelFilter(logging.Filter):
    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record):
        return self.min_level <= record.levelno <= self.max_level


@lru_cache(maxsize=None)
def get_logger(name=None):
    return logging.getLogger(name)


def setup_logging(log_dir='./logs', console_level=logging.INFO, file_level=logging.DEBUG):
    root_logger = get_logger()
    root_logger.setLevel(logging.DEBUG)

    if not root_logger.handlers:
        setup_file_handlers(root_logger, log_dir, file_level)
        setup_console_handler(root_logger, console_level)

    return root_logger


def setup_file_handlers(root_logger, log_dir, file_level):
    os.makedirs(log_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(log_dir, f'{date_str}-log.txt')

    file_handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(file_handler)


def setup_console_handler(root_logger, console_level):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)


def disable_logging():
    logging.disable(logging.CRITICAL)


logger = setup_logging()
