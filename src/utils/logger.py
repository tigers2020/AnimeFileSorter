#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logger utility for AnimeFileSorter.
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Singleton logger class."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger("AnimeFileSorter")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path.cwd() / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for logs
        log_file = logs_dir / f"animefilesorter_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatting
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        return self.logger
    
    def set_level(self, level: int) -> None:
        """Set the logging level."""
        self.logger.setLevel(level)


# Global logger instance
logger = Logger().get_logger()


def log_exception(e: Exception) -> None:
    """
    Log an exception with full traceback.
    
    Args:
        e: The exception to log
    """
    logger.exception(f"Exception occurred: {e}")


def log_info(message: str) -> None:
    """
    Log an info message.
    
    Args:
        message: Message to log
    """
    logger.info(message)


def log_error(message: str) -> None:
    """
    Log an error message.
    
    Args:
        message: Message to log
    """
    logger.error(message)


def log_warning(message: str) -> None:
    """
    Log a warning message.
    
    Args:
        message: Message to log
    """
    logger.warning(message)


def log_debug(message: str) -> None:
    """
    Log a debug message.
    
    Args:
        message: Message to log
    """
    logger.debug(message) 