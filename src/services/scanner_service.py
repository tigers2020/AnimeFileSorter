#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scanner service for AnimeFileSorter.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional, Callable, Dict, Any

from src.models.media_item import MediaItem, FileType, MediaType
from src.utils.logger import log_info, log_error, log_debug, log_warning


class ScannerService:
    """Service for scanning directories and identifying media files."""
    
    # File extensions to include in scanning
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    SUBTITLE_EXTENSIONS = {'.srt', '.ass', '.ssa', '.vtt', '.sub'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    def __init__(self):
        """Initialize the scanner service."""
        self.excluded_dirs: Set[str] = {'.git', '__pycache__', 'venv', 'env'}
        self.cancel_scan: bool = False
        self.hash_chunk_size: int = 4096
        self.max_hash_size: int = 100 * 1024 * 1024  # 100 MB
    
    def scan_directory(self, directory: str, 
                      progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[MediaItem]:
        """
        Scan a directory for media files.
        
        Args:
            directory: Directory to scan
            progress_callback: Optional callback function to report progress
                The callback receives (files_processed, total_files, current_file)
                
        Returns:
            List of media items found
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Not a valid directory: {directory}")
            
        media_items: List[MediaItem] = []
        self.cancel_scan = False
        
        # First, count total files for progress reporting
        if progress_callback:
            total_files = self._count_media_files(directory)
            files_processed = 0
            progress_callback(files_processed, total_files, "")
        
        for root, dirs, files in os.walk(directory):
            if self.cancel_scan:
                log_info("Scan cancelled by user")
                break
                
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                if self.cancel_scan:
                    break
                    
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Process files based on extension
                if file_ext in self.VIDEO_EXTENSIONS or file_ext in self.SUBTITLE_EXTENSIONS:
                    try:
                        if progress_callback:
                            progress_callback(files_processed, total_files, file)
                            
                        media_item = self._create_media_item(file_path)
                        media_items.append(media_item)
                        
                        if progress_callback:
                            files_processed += 1
                            
                    except Exception as e:
                        log_error(f"Error processing file {file_path}: {e}")
        
        log_info(f"Scan completed: {len(media_items)} files found")
        return media_items
    
    def _count_media_files(self, directory: str) -> int:
        """
        Count the number of media files in a directory tree.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Number of media files found
        """
        count = 0
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in self.VIDEO_EXTENSIONS or file_ext in self.SUBTITLE_EXTENSIONS:
                    count += 1
        
        return count
    
    def cancel_scanning(self) -> None:
        """Cancel the current scanning operation."""
        self.cancel_scan = True
        log_info("Cancellation requested for scanning")
    
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
        file_ext = path.suffix.lower()
        
        # Basic file information
        media_item = MediaItem(
            file_path=str(path),
            file_name=path.name,
            file_size=stats.st_size,
            file_extension=file_ext,
            file_modified=datetime.fromtimestamp(stats.st_mtime),
            file_created=datetime.fromtimestamp(stats.st_ctime),
        )
        
        # Only calculate hash for files under the size limit
        if stats.st_size < self.max_hash_size:
            media_item.file_hash = self._calculate_partial_hash(file_path)
            log_debug(f"Calculated hash for: {path.name}")
        else:
            log_debug(f"Skipped hash calculation for large file: {path.name}")
        
        # Try to extract basic metadata from filename
        self._extract_metadata_from_filename(media_item)
        
        return media_item
    
    def _calculate_partial_hash(self, file_path: str) -> str:
        """
        Calculate a partial hash for a file (first 1MB only).
        
        Args:
            file_path: Path to the file
            
        Returns:
            File hash as a string
        """
        hash_md5 = hashlib.md5()
        bytes_to_read = min(1024 * 1024, os.path.getsize(file_path))  # First 1MB or file size
        
        with open(file_path, "rb") as f:
            # Read first bytes
            data = f.read(bytes_to_read)
            hash_md5.update(data)
            
            # Read last bytes if file is large enough
            if os.path.getsize(file_path) > bytes_to_read * 2:
                f.seek(-bytes_to_read, 2)  # Seek from end
                data = f.read(bytes_to_read)
                hash_md5.update(data)
                
        return hash_md5.hexdigest()
    
    def _extract_metadata_from_filename(self, media_item: MediaItem) -> None:
        """
        Extract basic metadata from the filename and update the media item.
        
        Args:
            media_item: The media item to update
        """
        # This is a simple implementation - would be expanded in MetadataService
        filename = media_item.file_name
        name_without_ext = os.path.splitext(filename)[0]
        
        # Very simple example patterns - to be expanded
        # e.g., "Show Name - S01E02 - Episode Title.mkv"
        import re
        
        # Try to identify if it's an episode
        episode_pattern = re.compile(r"(.+?)[\s.-]*[Ss](\d+)[Ee](\d+)(?:[\s.-]*(.+))?", re.IGNORECASE)
        match = episode_pattern.match(name_without_ext)
        
        if match:
            media_item.media_type = MediaType.SERIES
            media_item.title = match.group(1).replace(".", " ").strip()
            media_item.metadata["season"] = int(match.group(2))
            media_item.metadata["episode"] = int(match.group(3))
            if match.group(4):
                media_item.metadata["episode_title"] = match.group(4).replace(".", " ").strip()
        else:
            # Try to identify if it's a movie
            movie_pattern = re.compile(r"(.+?)[\s.-]*\((\d{4})\)", re.IGNORECASE)
            match = movie_pattern.match(name_without_ext)
            
            if match:
                media_item.media_type = MediaType.MOVIE
                media_item.title = match.group(1).replace(".", " ").strip()
                media_item.year = int(match.group(2))
            else:
                # Default: use the filename as title
                media_item.title = name_without_ext.replace(".", " ")
    
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
                    if item.file_hash is None and os.path.getsize(item.file_path) < self.max_hash_size:
                        item.file_hash = self._calculate_partial_hash(item.file_path)
                
                # Group by hash
                hash_groups = {}
                for item in items:
                    if item.file_hash:
                        if item.file_hash not in hash_groups:
                            hash_groups[item.file_hash] = []
                        hash_groups[item.file_hash].append(item)
                
                # Add duplicate groups to the result
                for hash_val, hash_items in hash_groups.items():
                    if len(hash_items) > 1:
                        duplicates.append(hash_items)
        
        log_info(f"Found {len(duplicates)} sets of duplicate files")
        return duplicates 