#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
미디어 아이템 모델 정의
"""

from enum import Enum
from typing import Dict, Any, Optional


class MediaType(Enum):
    """미디어 타입 열거형"""
    UNKNOWN = "unknown"
    SERIES = "series"
    MOVIE = "movie"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"


class MediaItem:
    """미디어 아이템 기본 클래스"""
    
    def __init__(
        self,
        file_path: str,
        file_name: str,
        title: Optional[str] = None,
        media_type: MediaType = MediaType.UNKNOWN,
        year: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        미디어 아이템 초기화
        
        Args:
            file_path: 파일 경로
            file_name: 파일 이름
            title: 미디어 제목
            media_type: 미디어 타입
            year: 제작 연도
            metadata: 추가 메타데이터
        """
        self.file_path = file_path
        self.file_name = file_name
        self.title = title
        self.media_type = media_type
        self.year = year
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        """문자열 표현"""
        if self.title:
            return f"{self.title} ({self.media_type.value})"
        return f"{self.file_name} ({self.media_type.value})"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return f"MediaItem('{self.file_name}', type={self.media_type.value})"


class Series(MediaItem):
    """시리즈 미디어 아이템"""
    
    def __init__(
        self,
        file_path: str,
        file_name: str,
        title: Optional[str] = None,
        season: int = 1,
        episode: int = 1,
        episode_title: Optional[str] = None,
        media_type: MediaType = MediaType.SERIES,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        시리즈 미디어 아이템 초기화
        
        Args:
            file_path: 파일 경로
            file_name: 파일 이름
            title: 시리즈 제목
            season: 시즌 번호
            episode: 에피소드 번호
            episode_title: 에피소드 제목
            media_type: 미디어 타입
            metadata: 추가 메타데이터
        """
        metadata = metadata or {}
        metadata.update({
            "season": season,
            "episode": episode,
            "episode_title": episode_title
        })
        
        super().__init__(
            file_path=file_path,
            file_name=file_name,
            title=title,
            media_type=media_type,
            metadata=metadata
        )
    
    def __str__(self) -> str:
        """문자열 표현"""
        season = self.metadata.get("season", 1)
        episode = self.metadata.get("episode", 1)
        if self.title:
            return f"{self.title} - S{season:02d}E{episode:02d}"
        return f"{self.file_name}"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        season = self.metadata.get("season", 1)
        episode = self.metadata.get("episode", 1)
        return f"Series('{self.title}', S{season:02d}E{episode:02d})"


class Movie(MediaItem):
    """영화 미디어 아이템"""
    
    def __init__(
        self,
        file_path: str,
        file_name: str,
        title: Optional[str] = None,
        year: Optional[str] = None,
        media_type: MediaType = MediaType.MOVIE,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        영화 미디어 아이템 초기화
        
        Args:
            file_path: 파일 경로
            file_name: 파일 이름
            title: 영화 제목
            year: 제작 연도
            media_type: 미디어 타입
            metadata: 추가 메타데이터
        """
        super().__init__(
            file_path=file_path,
            file_name=file_name,
            title=title,
            media_type=media_type,
            year=year,
            metadata=metadata or {}
        )
    
    def __str__(self) -> str:
        """문자열 표현"""
        if self.title:
            if self.year:
                return f"{self.title} ({self.year})"
            return self.title
        return self.file_name
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        year_str = f", {self.year}" if self.year else ""
        return f"Movie('{self.title}'{year_str})" 