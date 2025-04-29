#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scanner service for AnimeFileSorter.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional

from src.models.media_item import MediaItem, FileType


class ScannerService:
    """Service for scanning directories and identifying media files."""
    
    # File extensions to include in scanning
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    SUBTITLE_EXTENSIONS = {'.srt', '.ass', '.ssa', '.vtt', '.sub'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    def __init__(self):
        """Initialize the scanner service."""
        self.excluded_dirs: Set[str] = {'.git', '__pycache__', 'venv', 'env'}
    
    def scan_directory(self, directory: str) -> List[MediaItem]:
        """
        Scan a directory for media files.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of media items found
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Not a valid directory: {directory}")
            
        media_items: List[MediaItem] = []
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Only process video files for now
                if file_ext in self.VIDEO_EXTENSIONS:
                    try:
                        media_item = self._create_media_item(file_path)
                        media_items.append(media_item)
                    except Exception as e:
                        # In a real application, we'd log this error
                        print(f"Error processing file {file_path}: {e}")
        
        return media_items
    
    def _create_media_item(self, file_path: str) -> MediaItem:
        """
        Create a MediaItem from a file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MediaItem instance
        """
        path = Path(file_path)
        stats = path.stat()
        
        # For now, just create a basic MediaItem with file information
        # In a real implementation, we'd extract metadata from the file
        # and populate the media-specific fields
        return MediaItem(
            file_path=str(path),
            file_name=path.name,
            file_size=stats.st_size,
            file_extension=path.suffix.lower(),
            file_modified=datetime.fromtimestamp(stats.st_mtime),
            file_created=datetime.fromtimestamp(stats.st_ctime),
            # In a real implementation, calculating hash for large files would be
            # done in a background thread to avoid blocking the UI
            # file_hash=self._calculate_file_hash(file_path)
        )
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate a hash for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File hash as a string
        """
        # For large files, we might only hash the first few MB
        # to improve performance, but this would reduce accuracy
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                
        return hash_md5.hexdigest()
    
    def scan_for_duplicates(self, media_items: List[MediaItem]) -> List[List[MediaItem]]:
        """
        Find duplicate files in a list of media items.
        
        Args:
            media_items: List of media items to check
            
        Returns:
            List of lists, where each inner list contains duplicate items
        """
        # Group by file size first (quick check)
        size_groups = {}
        for item in media_items:
            if item.file_size not in size_groups:
                size_groups[item.file_size] = []
            size_groups[item.file_size].append(item)
        
        # Calculate hashes only for files with the same size
        duplicates = []
        for size, items in size_groups.items():
            if len(items) > 1:
                # Calculate hashes if not already done
                for item in items:
                    if item.file_hash is None:
                        item.file_hash = self._calculate_file_hash(item.file_path)
                
                # Group by hash
                hash_groups = {}
                for item in items:
                    if item.file_hash not in hash_groups:
                        hash_groups[item.file_hash] = []
                    hash_groups[item.file_hash].append(item)
                
                # Add duplicate groups to the result
                for hash_val, hash_items in hash_groups.items():
                    if len(hash_items) > 1:
                        duplicates.append(hash_items)
        
        return duplicates 