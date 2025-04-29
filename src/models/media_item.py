#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Media item data models for AnimeFileSorter.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field, validator


class MediaType(str, Enum):
    """Enum for different types of media."""
    UNKNOWN = "unknown"
    SERIES = "series"
    MOVIE = "movie"
    SPECIAL = "special"
    OVA = "ova"
    ONA = "ona"


class FileType(str, Enum):
    """Enum for different types of files."""
    VIDEO = "video"
    SUBTITLE = "subtitle"
    IMAGE = "image"
    AUDIO = "audio"
    OTHER = "other"


class MediaItem(BaseModel):
    """Base class for all media items."""
    
    # File information
    file_path: str
    file_name: str
    file_size: int
    file_type: FileType = FileType.OTHER
    file_extension: str
    file_modified: datetime
    file_created: Optional[datetime] = None
    file_hash: Optional[str] = None  # For duplicate detection
    
    # Media information
    media_type: MediaType = MediaType.UNKNOWN
    title: Optional[str] = None
    title_original: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate that the file path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"File does not exist: {v}")
        return str(path.absolute())
    
    @validator('file_name', pre=True, always=True)
    def set_file_name(cls, v, values):
        """Set file_name from file_path if not provided."""
        if v:
            return v
        if 'file_path' in values:
            return Path(values['file_path']).name
        return v
    
    @validator('file_extension', pre=True, always=True)
    def set_file_extension(cls, v, values):
        """Set file_extension from file_path if not provided."""
        if v:
            return v
        if 'file_path' in values:
            return Path(values['file_path']).suffix.lower()
        return v
    
    @validator('file_type', pre=True, always=True)
    def set_file_type(cls, v, values):
        """Determine file type based on extension."""
        if v and v != FileType.OTHER:
            return v
            
        if 'file_extension' in values:
            ext = values['file_extension'].lower()
            
            # Video files
            if ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                return FileType.VIDEO
                
            # Subtitle files
            if ext in ['.srt', '.ass', '.ssa', '.vtt', '.sub']:
                return FileType.SUBTITLE
                
            # Image files
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return FileType.IMAGE
                
            # Audio files
            if ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                return FileType.AUDIO
                
        return FileType.OTHER
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Series(MediaItem):
    """Model for a TV series."""
    
    media_type: MediaType = MediaType.SERIES
    
    # Series specific information
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    total_episodes: Optional[int] = None
    total_seasons: Optional[int] = None
    series_title: Optional[str] = None
    
    # External IDs
    tmdb_id: Optional[int] = None
    anilist_id: Optional[int] = None
    
    @validator('media_type')
    def validate_media_type(cls, v):
        """Ensure the media type is SERIES."""
        if v != MediaType.SERIES:
            raise ValueError(f"Media type must be SERIES for Series model, got {v}")
        return v


class Movie(MediaItem):
    """Model for a movie."""
    
    media_type: MediaType = MediaType.MOVIE
    
    # Movie specific information
    runtime: Optional[int] = None  # in minutes
    director: Optional[str] = None
    
    # External IDs
    tmdb_id: Optional[int] = None
    anilist_id: Optional[int] = None
    
    @validator('media_type')
    def validate_media_type(cls, v):
        """Ensure the media type is MOVIE."""
        if v != MediaType.MOVIE:
            raise ValueError(f"Media type must be MOVIE for Movie model, got {v}")
        return v 