#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File controller for AnimeFileSorter.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from src.services.scanner_service import ScannerService
from src.services.organizer_service import OrganizerService
from src.models.media_item import MediaItem


class FileController:
    """Controller for handling file operations."""
    
    def __init__(self):
        """Initialize the file controller."""
        self.scanner_service = ScannerService()
        self.organizer_service = OrganizerService()
        self.input_directory = ""
        self.output_directory = ""
        self.scanned_files: List[MediaItem] = []
    
    def set_directories(self, input_dir: str, output_dir: Optional[str] = None) -> None:
        """
        Set the input and output directories.
        
        Args:
            input_dir: Path to the input directory
            output_dir: Path to the output directory. If None, defaults to input_dir/organized
        """
        self.input_directory = input_dir
        
        if output_dir is None:
            # Default output directory is a subdirectory named 'organized' in the parent of input_dir
            parent_dir = str(Path(input_dir).parent)
            self.output_directory = os.path.join(parent_dir, "organized")
        else:
            self.output_directory = output_dir
    
    def scan_directory(self, directory: Optional[str] = None) -> List[MediaItem]:
        """
        Scan a directory for media files.
        
        Args:
            directory: Directory to scan. If None, uses the previously set input_directory.
            
        Returns:
            List of media items found
        """
        if directory is not None:
            self.input_directory = directory
            
        if not self.input_directory:
            raise ValueError("Input directory not set.")
            
        self.scanned_files = self.scanner_service.scan_directory(self.input_directory)
        return self.scanned_files
    
    def organize_files(self, preview_only: bool = False) -> List[Tuple[str, str]]:
        """
        Organize the scanned files according to settings.
        
        Args:
            preview_only: If True, returns the operations that would be performed without actually doing them
            
        Returns:
            List of (source, destination) paths for each file
        """
        if not self.scanned_files:
            raise ValueError("No files scanned. Run scan_directory first.")
            
        if not self.output_directory:
            raise ValueError("Output directory not set.")
            
        return self.organizer_service.organize_files(
            self.scanned_files,
            self.output_directory,
            preview_only
        )
    
    def get_file_details(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file details
        """
        # For now, just return basic file info
        # In a real implementation, this would include media-specific metadata
        file = Path(file_path)
        stats = file.stat()
        
        return {
            "name": file.name,
            "path": str(file),
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "extension": file.suffix.lower(),
        } 