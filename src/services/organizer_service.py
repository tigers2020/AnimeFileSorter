#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Organizer service for AnimeFileSorter.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from src.models.media_item import MediaItem, MediaType, Series, Movie


class OrganizerService:
    """Service for organizing media files according to patterns and rules."""
    
    def __init__(self):
        """Initialize the organizer service."""
        # Default patterns for destination paths
        self.series_folder_pattern = "{series_name}"
        self.season_folder_pattern = "Season {season_number}"
        self.episode_file_pattern = "{series_name} - S{season_number}E{episode_number} - {episode_title}"
        self.movie_file_pattern = "{title} ({year})"
        
        # Organization settings
        self.create_series_folders = True
        self.create_season_folders = True
        self.preserve_original_extension = True
        self.move_subtitles = True
    
    def organize_files(
        self,
        media_items: List[MediaItem],
        output_directory: str,
        preview_only: bool = False
    ) -> List[Tuple[str, str]]:
        """
        Organize files according to patterns and settings.
        
        Args:
            media_items: List of media items to organize
            output_directory: Base directory for organized files
            preview_only: If True, only returns planned operations without executing them
            
        Returns:
            List of (source_path, destination_path) tuples
        """
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)
            
        operations: List[Tuple[str, str]] = []
        
        for item in media_items:
            try:
                dest_path = self._get_destination_path(item, output_directory)
                operations.append((item.file_path, dest_path))
                
                if not preview_only:
                    self._execute_file_operation(item.file_path, dest_path)
                    
                    # If we should also move subtitle files
                    if self.move_subtitles:
                        subtitle_files = self._find_related_subtitle_files(item.file_path)
                        for sub_file in subtitle_files:
                            # Use same destination directory, but keep subtitle filename
                            sub_dest = os.path.join(
                                os.path.dirname(dest_path),
                                os.path.basename(sub_file)
                            )
                            operations.append((sub_file, sub_dest))
                            
                            if not preview_only:
                                self._execute_file_operation(sub_file, sub_dest)
            except Exception as e:
                # In a real application, we'd log the error
                print(f"Error organizing file {item.file_path}: {e}")
        
        return operations
    
    def _get_destination_path(self, item: MediaItem, output_directory: str) -> str:
        """
        Generate the destination path for a media item.
        
        Args:
            item: Media item to organize
            output_directory: Base directory for organized files
            
        Returns:
            Destination path
        """
        # In a real implementation, we'd parse the filename to extract
        # series/season/episode info, or use metadata from external sources
        
        if isinstance(item, Series) or item.media_type == MediaType.SERIES:
            # Process as a series
            return self._get_series_destination(item, output_directory)
        elif isinstance(item, Movie) or item.media_type == MediaType.MOVIE:
            # Process as a movie
            return self._get_movie_destination(item, output_directory)
        else:
            # Default organization (just put in root output dir)
            return os.path.join(output_directory, item.file_name)
    
    def _get_series_destination(self, item: MediaItem, output_directory: str) -> str:
        """
        Generate the destination path for a series item.
        
        Args:
            item: Series media item
            output_directory: Base directory for organized files
            
        Returns:
            Destination path
        """
        # For now, use a simple pattern match on the filename
        # In a real implementation, we'd use proper metadata extraction
        series_info = self._extract_series_info_from_filename(item.file_name)
        
        # Prepare values for path pattern
        values = {
            "series_name": series_info.get("series_name", "Unknown Series"),
            "season_number": str(series_info.get("season_number", 1)).zfill(2),
            "episode_number": str(series_info.get("episode_number", 1)).zfill(2),
            "episode_title": series_info.get("episode_title", "")
        }
        
        # Build the path
        series_folder = self.series_folder_pattern.format(**values) if self.create_series_folders else ""
        season_folder = self.season_folder_pattern.format(**values) if self.create_season_folders else ""
        
        # Format the filename using the pattern
        file_name = self.episode_file_pattern.format(**values)
        
        # Add the original extension if needed
        if self.preserve_original_extension:
            file_name += item.file_extension
        
        # Construct the full path
        path_parts = [output_directory]
        if series_folder:
            path_parts.append(series_folder)
        if season_folder:
            path_parts.append(season_folder)
        path_parts.append(file_name)
        
        dest_path = os.path.join(*path_parts)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        return dest_path
    
    def _get_movie_destination(self, item: MediaItem, output_directory: str) -> str:
        """
        Generate the destination path for a movie item.
        
        Args:
            item: Movie media item
            output_directory: Base directory for organized files
            
        Returns:
            Destination path
        """
        # For now, use a simple pattern match on the filename
        # In a real implementation, we'd use proper metadata extraction
        movie_info = self._extract_movie_info_from_filename(item.file_name)
        
        # Prepare values for path pattern
        values = {
            "title": movie_info.get("title", "Unknown Movie"),
            "year": movie_info.get("year", "")
        }
        
        # Format the filename using the pattern
        file_name = self.movie_file_pattern.format(**values)
        
        # Add the original extension if needed
        if self.preserve_original_extension:
            file_name += item.file_extension
        
        # Construct the full path
        dest_path = os.path.join(output_directory, "Movies", file_name)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        return dest_path
    
    def _extract_series_info_from_filename(self, filename: str) -> Dict[str, any]:
        """
        Extract series information from a filename using regex patterns.
        
        Args:
            filename: Filename to parse
            
        Returns:
            Dictionary with series information
        """
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Try common patterns
        # Pattern 1: SeriesName.S01E02
        pattern1 = r"(.+?)[.\s][Ss](\d+)[Ee](\d+)"
        match = re.search(pattern1, name)
        if match:
            return {
                "series_name": match.group(1).replace(".", " ").strip(),
                "season_number": int(match.group(2)),
                "episode_number": int(match.group(3)),
                "episode_title": ""
            }
        
        # Pattern 2: SeriesName - 01x02 - EpisodeTitle
        pattern2 = r"(.+?)\s*-\s*(\d+)x(\d+)\s*-\s*(.+)"
        match = re.search(pattern2, name)
        if match:
            return {
                "series_name": match.group(1).strip(),
                "season_number": int(match.group(2)),
                "episode_number": int(match.group(3)),
                "episode_title": match.group(4).strip()
            }
        
        # If no pattern matches, use a fallback
        return {
            "series_name": name,
            "season_number": 1,
            "episode_number": 1,
            "episode_title": ""
        }
    
    def _extract_movie_info_from_filename(self, filename: str) -> Dict[str, any]:
        """
        Extract movie information from a filename using regex patterns.
        
        Args:
            filename: Filename to parse
            
        Returns:
            Dictionary with movie information
        """
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Try common patterns
        # Pattern: Title (Year)
        pattern = r"(.+?)[\s.]*\((\d{4})\)"
        match = re.search(pattern, name)
        if match:
            return {
                "title": match.group(1).replace(".", " ").strip(),
                "year": match.group(2)
            }
        
        # If no pattern matches, use a fallback
        return {
            "title": name,
            "year": ""
        }
    
    def _execute_file_operation(self, source_path: str, dest_path: str) -> None:
        """
        Execute the file operation (copy or move).
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
        """
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # For now, just copy the file
        # In a real implementation, we'd have a setting to control copy vs. move
        shutil.copy2(source_path, dest_path)
    
    def _find_related_subtitle_files(self, video_path: str) -> List[str]:
        """
        Find subtitle files related to a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of paths to related subtitle files
        """
        # Get the directory and filename without extension
        directory = os.path.dirname(video_path)
        filename_base = os.path.splitext(os.path.basename(video_path))[0]
        
        # Find all files with subtitle extensions that match the base filename
        subtitle_files = []
        for file in os.listdir(directory):
            if any(file.endswith(ext) for ext in ['.srt', '.ass', '.ssa', '.vtt', '.sub']):
                if file.startswith(filename_base) or filename_base in file:
                    subtitle_files.append(os.path.join(directory, file))
        
        return subtitle_files 