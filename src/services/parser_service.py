#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파일 이름을 파싱하여 미디어 아이템으로 변환하는 서비스
"""

import os
import re
from typing import List, Dict, Any, Optional

from src.models.media_item import MediaItem, MediaType, Series, Movie
from src.utils.logger import log_info, log_error, log_debug


class ParserService:
    """파일 이름을 파싱하여 미디어 아이템으로 변환하는 서비스"""
    
    def __init__(self):
        """파서 서비스 초기화"""
        # 시리즈 탐지 패턴 (정규식)
        self.series_patterns = [
            # 일반적인 시리즈 패턴 (SxxExx)
            r"(.+?)[.\s][Ss](\d{1,2})[Ee](\d{1,2})",
            # 시즌 x 에피소드 패턴 (01x02)
            r"(.+?)\s*-\s*(\d{1,2})x(\d{1,2})",
            # 시즌.에피소드 패턴 (1.02)
            r"(.+?)[.\s](\d{1,2})\.(\d{1,2})",
            # 에피소드만 있는 패턴 (EP01, E01)
            r"(.+?)[.\s][Ee][Pp]?\.?(\d{1,2})"
        ]
        
        # 영화 탐지 패턴 (정규식)
        self.movie_patterns = [
            # 일반적인 영화 패턴 (제목 (연도))
            r"(.+?)[\s.]*\((\d{4})\)",
            # 제목.연도 패턴
            r"(.+?)[\s.]+(\d{4})[\s.]*"
        ]
    
    def parse_files(self, file_paths: List[str]) -> List[MediaItem]:
        """
        파일 목록을 파싱하여 미디어 아이템 목록으로 변환합니다.
        
        Args:
            file_paths: 파싱할 파일 경로 목록
            
        Returns:
            미디어 아이템 목록
        """
        media_items: List[MediaItem] = []
        
        for file_path in file_paths:
            try:
                item = self.parse_file(file_path)
                if item:
                    media_items.append(item)
                    log_debug(f"파일 파싱 완료: {os.path.basename(file_path)} → {item.title}")
                else:
                    log_debug(f"파일 파싱 실패: {os.path.basename(file_path)}")
            except Exception as e:
                log_error(f"파일 파싱 중 오류 발생: {file_path} - {e}")
        
        return media_items
    
    def parse_file(self, file_path: str) -> Optional[MediaItem]:
        """
        단일 파일을 파싱하여 미디어 아이템으로 변환합니다.
        
        Args:
            file_path: 파싱할 파일 경로
            
        Returns:
            미디어 아이템 또는 None (파싱 실패 시)
        """
        if not os.path.exists(file_path):
            log_error(f"파일이 존재하지 않습니다: {file_path}")
            return None
        
        file_name = os.path.basename(file_path)
        file_name_no_ext = os.path.splitext(file_name)[0]
        
        # 시리즈 패턴 확인
        for pattern in self.series_patterns:
            match = re.search(pattern, file_name_no_ext, re.IGNORECASE)
            if match:
                # 시리즈로 판단
                return self._create_series_item(file_path, match)
        
        # 영화 패턴 확인
        for pattern in self.movie_patterns:
            match = re.search(pattern, file_name_no_ext, re.IGNORECASE)
            if match:
                # 영화로 판단
                return self._create_movie_item(file_path, match)
        
        # 패턴 매칭 실패 시 기본 미디어 아이템 생성
        return self._create_default_item(file_path)
    
    def _create_series_item(self, file_path: str, match) -> Series:
        """
        시리즈 미디어 아이템을 생성합니다.
        
        Args:
            file_path: 파일 경로
            match: 정규식 매치 객체
            
        Returns:
            Series 인스턴스
        """
        file_name = os.path.basename(file_path)
        series_name = match.group(1).replace(".", " ").strip()
        
        # 시즌/에피소드 정보 추출 시도
        season = 1
        episode = 1
        
        try:
            if len(match.groups()) >= 3:
                season = int(match.group(2))
                episode = int(match.group(3))
            elif len(match.groups()) >= 2:
                # 에피소드만 있는 패턴
                episode = int(match.group(2))
        except (IndexError, ValueError):
            pass
        
        metadata = {
            "season": season,
            "episode": episode
        }
        
        return Series(
            file_path=file_path,
            file_name=file_name,
            title=series_name,
            media_type=MediaType.SERIES,
            metadata=metadata
        )
    
    def _create_movie_item(self, file_path: str, match) -> Movie:
        """
        영화 미디어 아이템을 생성합니다.
        
        Args:
            file_path: 파일 경로
            match: 정규식 매치 객체
            
        Returns:
            Movie 인스턴스
        """
        file_name = os.path.basename(file_path)
        movie_title = match.group(1).replace(".", " ").strip()
        
        # 연도 정보 추출 시도
        year = None
        try:
            if len(match.groups()) >= 2:
                year = match.group(2)
        except IndexError:
            pass
        
        return Movie(
            file_path=file_path,
            file_name=file_name,
            title=movie_title,
            year=year,
            media_type=MediaType.MOVIE
        )
    
    def _create_default_item(self, file_path: str) -> MediaItem:
        """
        기본 미디어 아이템을 생성합니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            MediaItem 인스턴스
        """
        file_name = os.path.basename(file_path)
        title = os.path.splitext(file_name)[0].replace(".", " ").strip()
        
        return MediaItem(
            file_path=file_path,
            file_name=file_name,
            title=title,
            media_type=MediaType.UNKNOWN
        ) 