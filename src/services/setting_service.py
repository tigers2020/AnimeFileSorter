#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애니메이션 분류기 설정 관리 서비스
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path

from src.database.db_manager import DatabaseManager
from src.utils.logger import log_info, log_error, log_debug


class SettingService:
    """애니메이션 분류기 설정 관리 서비스"""
    
    # 기본 설정값
    DEFAULT_SETTINGS = {
        # 기본 경로 설정
        "input_directory": "",
        "output_directory": "",
        "last_used_directory": "",
        
        # 폴더 패턴 설정
        "series_folder_pattern": "{series_name}",
        "season_folder_pattern": "Season {season_number}",
        "episode_pattern": "{series_name} - S{season_number}E{episode_number}",
        "movie_pattern": "{title} ({year})",
        
        # 폴더 생성 옵션
        "create_series_folders": True,
        "create_season_folders": True,
        "preserve_original_filename": True,
        
        # 파일 작업 설정
        "operation_type": "COPY",  # "COPY" 또는 "MOVE"
        "move_subtitles": True,
        "confirm_before_organize": True,
        
        # 스캔 설정
        "video_extensions": ".mp4,.mkv,.avi,.mov,.wmv,.m4v,.flv,.webm",
        "subtitle_extensions": ".srt,.ass,.ssa,.vtt,.sub",
        "ignore_sample_videos": True,
        "scan_recursive": True,
        
        # 정리 설정
        "organize_by_type": True,  # 시리즈와 영화 분리
        "movies_folder_name": "Movies",
        "series_folder_name": "Series",
        "unsorted_folder_name": "Unsorted",
        
        # API 설정
        "tmdb_api_key": "",  
        "anilist_api_key": "",
        "use_external_api": False,
        
        # 메타데이터 설정
        "auto_fetch_metadata": False,
        "overwrite_existing_metadata": False,
        "language": "ko-KR",
        
        # 기타 설정
        "auto_save_settings": True,
        "check_updates": True
    }
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        설정 서비스 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
        """
        self.db_manager = db_manager or DatabaseManager()
        self.settings = {}
        self.load_settings()
        
        # 경로 설정이 비어있을 경우 작업 디렉토리를 기본값으로 설정
        if not self.settings.get("input_directory"):
            self.settings["input_directory"] = str(Path.cwd())
            
        if not self.settings.get("output_directory"):
            self.settings["output_directory"] = str(Path.cwd() / "organized")
            
        if not self.settings.get("last_used_directory"):
            self.settings["last_used_directory"] = str(Path.home())
            
        # 설정이 로드된 후 자동 저장
        if self.settings.get("auto_save_settings", True):
            self.save_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        저장된 설정을 불러오고 기본값과 병합합니다.
        
        Returns:
            현재 설정 딕셔너리
        """
        saved_settings = self.db_manager.load_settings()
        
        # 기본 설정과 병합
        self.settings = {**self.DEFAULT_SETTINGS, **saved_settings}
        log_info(f"설정 로드 완료: {len(self.settings)} 개 항목")
        return self.settings
    
    def save_settings(self) -> bool:
        """
        현재 설정을 저장합니다.
        
        Returns:
            성공 여부
        """
        result = self.db_manager.save_settings(self.settings)
        if result:
            log_info("설정 저장 완료")
        else:
            log_error("설정 저장 실패")
        return result
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        특정 설정값을 가져옵니다.
        
        Args:
            key: 설정 키
            default: 찾을 수 없을 경우 반환할 기본값
            
        Returns:
            설정값 또는 기본값
        """
        # 먼저 현재 메모리 내 설정에서 찾기
        value = self.settings.get(key)
        
        # 없으면 DB에서 직접 조회
        if value is None:
            value = self.db_manager.get_setting(key)
            
            # DB에 있다면 현재 설정에 추가
            if value is not None:
                self.settings[key] = value
            else:
                # 기본 설정에서 찾기
                value = self.DEFAULT_SETTINGS.get(key, default)
                
                # 기본 설정에 있으면 저장
                if value is not None and key in self.DEFAULT_SETTINGS:
                    self.settings[key] = value
                    
        return value
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        설정을 업데이트하고 저장합니다.
        
        Args:
            key: 설정 키
            value: 설정 값
            
        Returns:
            성공 여부
        """
        self.settings[key] = value
        return self.db_manager.save_settings({key: value})
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """
        여러 설정을 한 번에 업데이트하고 저장합니다.
        
        Args:
            settings: 업데이트할 설정 딕셔너리
            
        Returns:
            성공 여부
        """
        self.settings.update(settings)
        return self.db_manager.save_settings(settings)
    
    def reset_to_defaults(self) -> bool:
        """
        모든 설정을 기본값으로 되돌립니다.
        
        Returns:
            성공 여부
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.db_manager.save_settings(self.settings)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        모든 설정을 딕셔너리로 반환합니다.
        
        Returns:
            전체 설정 딕셔너리
        """
        return self.settings.copy()
        
    def get_input_directory(self) -> str:
        """
        입력 디렉토리 경로를 가져옵니다.
        
        Returns:
            입력 디렉토리 경로
        """
        return self.get_setting("input_directory", "")
        
    def get_output_directory(self) -> str:
        """
        출력 디렉토리 경로를 가져옵니다.
        
        Returns:
            출력 디렉토리 경로
        """
        return self.get_setting("output_directory", "")
    
    def set_directories(self, input_dir: str = None, output_dir: str = None) -> bool:
        """
        입력 및 출력 디렉토리를 설정합니다.
        
        Args:
            input_dir: 입력 디렉토리 경로
            output_dir: 출력 디렉토리 경로
            
        Returns:
            성공 여부
        """
        settings_to_update = {}
        
        if input_dir:
            input_dir = os.path.abspath(input_dir)
            settings_to_update["input_directory"] = input_dir
            settings_to_update["last_used_directory"] = os.path.dirname(input_dir)
            
        if output_dir:
            output_dir = os.path.abspath(output_dir)
            settings_to_update["output_directory"] = output_dir
            
        if settings_to_update:
            return self.update_settings(settings_to_update)
        return True 