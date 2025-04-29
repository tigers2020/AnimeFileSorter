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
from src.utils.logger import log_info, log_error, log_debug
from src.database.db_manager import DatabaseManager
from src.services.setting_service import SettingService


class OrganizerService:
    """Service for organizing media files according to patterns and rules."""
    
    def __init__(self, setting_service: SettingService = None, db_manager: DatabaseManager = None):
        """
        Initialize the organizer service.
        
        Args:
            setting_service: 설정 서비스 인스턴스
            db_manager: 데이터베이스 관리자 인스턴스
        """
        self.db_manager = db_manager or DatabaseManager()
        self.setting_service = setting_service or SettingService(self.db_manager)
        
        # 설정에서 값 가져오기
        self.series_folder_pattern = self.setting_service.get_setting("series_folder_pattern")
        self.season_folder_pattern = self.setting_service.get_setting("season_folder_pattern")
        self.create_series_folders = self.setting_service.get_setting("create_series_folders")
        self.create_season_folders = self.setting_service.get_setting("create_season_folders")
        self.preserve_original_filename = self.setting_service.get_setting("preserve_original_filename")
        self.move_subtitles = self.setting_service.get_setting("move_subtitles")
        self.operation_type = self.setting_service.get_setting("operation_type")
        self.organize_by_type = self.setting_service.get_setting("organize_by_type")
        self.movies_folder_name = self.setting_service.get_setting("movies_folder_name")
        self.series_folder_name = self.setting_service.get_setting("series_folder_name")
        self.unsorted_folder_name = self.setting_service.get_setting("unsorted_folder_name")
    
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
                    
                    # DB에 처리 기록 저장
                    self._record_media_processing(item, dest_path)
                    
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
                log_error(f"Error organizing file {item.file_path}: {e}")
        
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
        # 추출된 타이틀이 있으면 사용, 없으면 파일 이름에서 추출
        if item.title:
            if isinstance(item, Series) or item.media_type == MediaType.SERIES:
                # Process as a series
                return self._get_series_destination(item, output_directory)
            elif isinstance(item, Movie) or item.media_type == MediaType.MOVIE:
                # Process as a movie
                return self._get_movie_destination(item, output_directory)
            else:
                # 타입이 없지만 타이틀은 있는 경우 기본 폴더에 정리
                folder_name = item.title.strip()
                return os.path.join(output_directory, folder_name, item.file_name)
        else:
            # 타이틀이 없으면 기본 폴더에 원본 파일명 그대로 저장
            return os.path.join(output_directory, self.unsorted_folder_name, item.file_name)
    
    def _get_series_destination(self, item: MediaItem, output_directory: str) -> str:
        """
        Generate the destination path for a series item.
        
        Args:
            item: Series media item
            output_directory: Base directory for organized files
            
        Returns:
            Destination path
        """
        # 아이템 메타데이터 사용 또는 파일명에서 추출
        series_name = item.title
        season_number = item.metadata.get("season", 1)
        
        # 시즌 정보가 없을 경우 파일명에서 다시 한번 시도
        if "season" not in item.metadata:
            series_info = self._extract_series_info_from_filename(item.file_name)
            season_number = series_info.get("season_number", 1)
        
        # Prepare values for path pattern
        values = {
            "series_name": series_name,
            "season_number": str(season_number).zfill(2)
        }
        
        # Build the path - 폴더 구조만 생성하고 파일 이름은 원본 유지
        series_folder = self.series_folder_pattern.format(**values) if self.create_series_folders else ""
        season_folder = self.season_folder_pattern.format(**values) if self.create_season_folders else ""
        
        # 원본 파일명 유지
        file_name = item.file_name
        
        # Construct the full path
        path_parts = [output_directory]
        
        # 카테고리별 구성 시 시리즈 루트 폴더 추가
        if self.organize_by_type:
            path_parts.append(self.series_folder_name)
            
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
        # 아이템 메타데이터 사용
        title = item.title
        year = item.year or ""
        
        # 폴더명 생성
        if year:
            folder_name = f"{title} ({year})"
        else:
            folder_name = title
        
        # 원본 파일명 유지
        file_name = item.file_name
        
        # Construct the full path
        path_parts = [output_directory]
        
        # 카테고리별 구성 시 영화 루트 폴더 추가
        if self.organize_by_type:
            path_parts.append(self.movies_folder_name)
            
        path_parts.append(folder_name)
        path_parts.append(file_name)
        
        dest_path = os.path.join(*path_parts)
        
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
        
        operation_success = False
        error_message = None
        
        try:
            # Operation based on settings
            if self.operation_type.upper() == "MOVE":
                shutil.move(source_path, dest_path)
                log_info(f"파일 이동됨: {os.path.basename(source_path)} → {os.path.dirname(dest_path)}")
                operation_success = True
            else:  # Default to COPY
                shutil.copy2(source_path, dest_path)
                log_info(f"파일 복사됨: {os.path.basename(source_path)} → {os.path.dirname(dest_path)}")
                operation_success = True
        except Exception as e:
            error_message = str(e)
            log_error(f"파일 작업 실패 ({self.operation_type}): {error_message}")
            raise
        finally:
            # 기록 저장
            if self.db_manager:
                self.db_manager.record_organization_operation(
                    source_path=source_path,
                    destination_path=dest_path,
                    operation_type=self.operation_type.upper(),
                    success=operation_success,
                    error_message=error_message
                )
    
    def _record_media_processing(self, item: MediaItem, destination_path: str) -> None:
        """
        미디어 처리 정보를 데이터베이스에 기록합니다.
        
        Args:
            item: 처리된 미디어 아이템
            destination_path: 파일 목적지 경로
        """
        if not self.db_manager:
            return
            
        media_data = {
            'file_path': item.file_path,
            'media_type': item.media_type.value if hasattr(item.media_type, 'value') else str(item.media_type),
            'title': item.title,
            'year': item.year,
            'original_filename': item.file_name,
            'destination_path': destination_path,
            'processed': True
        }
        
        # 시리즈인 경우 추가 정보
        if isinstance(item, Series) or item.media_type == MediaType.SERIES:
            media_data['season'] = item.metadata.get('season', 1)
            media_data['episode'] = item.metadata.get('episode', 1)
            
        self.db_manager.save_media_item(media_data)
    
    def _find_related_subtitle_files(self, video_path: str) -> List[str]:
        """
        Find subtitle files related to a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of paths to related subtitle files
        """
        # 설정에서 자막 확장자 가져오기
        subtitle_extensions_str = self.setting_service.get_setting("subtitle_extensions")
        subtitle_extensions = subtitle_extensions_str.split(',') if subtitle_extensions_str else ['.srt', '.ass', '.ssa', '.vtt', '.sub']
        
        # Get the directory and filename without extension
        directory = os.path.dirname(video_path)
        filename_base = os.path.splitext(os.path.basename(video_path))[0]
        
        # Find all files with subtitle extensions that match the base filename
        subtitle_files = []
        for file in os.listdir(directory):
            if any(file.endswith(ext) for ext in subtitle_extensions):
                if file.startswith(filename_base) or filename_base in file:
                    subtitle_files.append(os.path.join(directory, file))
        
        return subtitle_files 