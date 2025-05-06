#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애플리케이션 설정을 관리하는 모듈입니다.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 설정 파일 기본 경로
DEFAULT_CONFIG_DIR = Path.home() / ".animefilesorter"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"

# 기본 설정값
DEFAULT_CONFIG = {
    "scan_directories": [],
    "output_directory": str(Path.home() / "AnimeFileSorter"),
    "recursive_scan": True,
    "file_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "naming_pattern": "{anime_title} - {episode_number}",
    "database_path": str(DEFAULT_CONFIG_DIR / "anime_files.db"),
    "auto_organize": False,
    "check_duplicates": True,
    "api_settings": {
        "anidb": {
            "client_name": "animefilesorterapp",
            "client_version": 1
        }
    },
    "ui_settings": {
        "theme": "default",
        "language": "ko",
        "window_size": [800, 600]
    }
}


class Config:
    """애플리케이션 설정을 관리하는 클래스."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        설정 관리자 초기화.
        
        Args:
            config_path: 설정 파일 경로 (기본값: ~/.animefilesorter/config.json)
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config = DEFAULT_CONFIG.copy()
        
        # 설정 디렉토리 생성
        os.makedirs(self.config_path.parent, exist_ok=True)
        
        # 설정 파일 로드
        self.load()
    
    def load(self) -> bool:
        """
        설정 파일에서 설정을 로드합니다.
        
        Returns:
            성공 여부
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                return True
            else:
                # 설정 파일이 없으면 기본 설정으로 생성
                return self.save()
        
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {e}")
            return False
    
    def save(self) -> bool:
        """
        현재 설정을 파일에 저장합니다.
        
        Returns:
            성공 여부
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값을 가져옵니다.
        
        Args:
            key: 설정 키
            default: 키가 없을 경우 반환할 기본값
            
        Returns:
            설정값
        """
        # 중첩된 키 처리 (예: "api_settings.anidb.client_name")
        if '.' in key:
            parts = key.split('.')
            value = self.config
            for part in parts:
                if part not in value:
                    return default
                value = value[part]
            return value
        
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        설정값을 설정합니다.
        
        Args:
            key: 설정 키
            value: 설정값
        """
        # 중첩된 키 처리
        if '.' in key:
            parts = key.split('.')
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정을 가져옵니다.
        
        Returns:
            모든 설정이 포함된 딕셔너리
        """
        return self.config.copy()
    
    def reset(self) -> None:
        """설정을 기본값으로 재설정합니다."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()


# 전역 설정 인스턴스
config = Config() 