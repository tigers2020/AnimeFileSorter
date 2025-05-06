#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애플리케이션 설정 관리 모듈입니다.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List


class AppConfig:
    """
    애플리케이션 설정 관리 클래스.
    
    설정 값을 파일에 저장하고 로드하는 기능을 제공합니다.
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        설정 관리자 초기화.
        
        Args:
            config_file_path: 설정 파일 경로 (기본값: ~/.animefilesorter/config.json)
        """
        self.logger = logging.getLogger(__name__)
        
        # 기본 설정 파일 경로
        if config_file_path is None:
            config_dir = Path.home() / '.animefilesorter'
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file_path = config_dir / 'config.json'
        else:
            self.config_file_path = Path(config_file_path)
        
        # 설정 값 저장 딕셔너리
        self.settings: Dict[str, Dict[str, Any]] = {}
        
        # 설정 파일 로드 (없으면 기본값 사용)
        self._load()
    
    def _load(self):
        """설정 파일에서 설정 로드."""
        try:
            # 먼저 기본 설정으로 초기화
            self._init_default_settings()
            
            # 파일이 존재하면 설정 값 로드 및 병합
            if self.config_file_path.exists():
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 로드된 설정을 기본 설정과 병합
                for section, values in loaded_settings.items():
                    if section not in self.settings:
                        self.settings[section] = {}
                    
                    # 섹션 내 값들을 병합
                    for key, value in values.items():
                        self.settings[section][key] = value
                        
                self.logger.info(f"설정 파일을 로드했습니다: {self.config_file_path}")
            else:
                self.logger.info(f"설정 파일이 없습니다. 기본 설정을 사용합니다: {self.config_file_path}")
        except Exception as e:
            self.logger.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본 설정 사용
            self._init_default_settings()
    
    def _init_default_settings(self):
        """기본 설정 초기화."""
        self.settings = {
            'general': {
                'media_directory': str(Path.home() / 'Videos'),
                'output_directory': str(Path.home() / 'Videos' / 'Sorted'),
                'log_level': 'DEBUG',
                'log_retention_days': 30
            },
            'anidb': {
                'udp_client_name': 'animerenamerpython',
                'udp_client_version': 3,
                'http_client_name': 'animerenamerpython',
                'http_client_version': 3,
                'auto_login': False,
                'cache_directory': str(Path.home() / '.animefilesorter' / 'cache'),
                'cache_retention_days': 30,
                'cache_max_size_mb': 100
            },
            'file_management': {
                'filename_pattern': '{series} - {episode} - {title}.{ext}',
                'directory_pattern': '{series} ({year})',
                'move_files': False,
                'create_series_dirs': True,
                'overwrite': False,
                'ignore_non_media': True,
                'media_extensions': ['.mkv', '.mp4', '.avi', '.ogm']
            },
            'ui': {
                'theme': '시스템 기본',
                'font_size': 10,
                'restore_window': True,
                'show_status_bar': True,
                'confirm_exit': True,
                'show_tooltips': True
            }
        }
    
    def save(self):
        """설정 파일에 설정 저장."""
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            self.logger.info(f"설정 파일에 저장했습니다: {self.config_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        설정 값 가져오기.
        
        Args:
            section: 설정 섹션
            key: 설정 키
            default: 설정이 없을 경우 기본값
            
        Returns:
            설정 값 또는 기본값
        """
        if section not in self.settings:
            return default
        
        return self.settings[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        설정 값 설정.
        
        Args:
            section: 설정 섹션
            key: 설정 키
            value: 설정 값
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        섹션 전체 설정 가져오기.
        
        Args:
            section: 설정 섹션
            
        Returns:
            섹션의 모든 설정 (딕셔너리)
        """
        return self.settings.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        섹션 전체 설정 업데이트.
        
        Args:
            section: 설정 섹션
            values: 업데이트할 설정 값 (딕셔너리)
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section].update(values)
    
    def reset_to_defaults(self) -> None:
        """모든 설정을 기본값으로 재설정."""
        self._init_default_settings()
        self.save()
    
    def reset_section(self, section: str) -> None:
        """
        지정된 섹션의 설정을 기본값으로 재설정.
        
        Args:
            section: 재설정할 설정 섹션
        """
        # 현재 설정 백업
        current_settings = self.settings.copy()
        
        # 기본값 초기화
        temp_default = {}
        self._init_default_settings()
        temp_default = self.settings.copy()
        
        # 현재 설정 복원
        self.settings = current_settings
        
        # 지정된 섹션만 기본값으로 재설정
        if section in temp_default:
            self.settings[section] = temp_default[section] 