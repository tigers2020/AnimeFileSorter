#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite 데이터베이스 관리를 위한 모듈입니다.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from src.utils.logger import log_info, log_error, log_debug


class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = None):
        """
        데이터베이스 관리자를 초기화합니다.
        
        Args:
            db_path: 데이터베이스 파일 경로. None이면 기본 경로 사용
        """
        if db_path is None:
            # 기본 경로: 앱 디렉토리 내의 data 폴더
            app_dir = Path.home() / ".anime_sorter"
            os.makedirs(app_dir, exist_ok=True)
            db_path = str(app_dir / "animesorter.db")
        
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """데이터베이스 초기화 및 필요한 테이블 생성"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # 설정 테이블 생성
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 미디어 아이템 테이블 생성
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_items (
                id INTEGER PRIMARY KEY,
                file_path TEXT UNIQUE NOT NULL,
                media_type TEXT,
                title TEXT,
                year TEXT,
                season INTEGER,
                episode INTEGER,
                original_filename TEXT,
                destination_path TEXT,
                processed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 정리 작업 히스토리 테이블
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization_history (
                id INTEGER PRIMARY KEY,
                source_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                operation_type TEXT NOT NULL,  -- 'COPY' or 'MOVE'
                success BOOLEAN NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.connection.commit()
            log_info("데이터베이스 초기화 완료")
        except sqlite3.Error as e:
            log_error(f"데이터베이스 초기화 중 오류 발생: {e}")
            raise
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        설정을 데이터베이스에 저장합니다.
        
        Args:
            settings: 저장할 설정 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            cursor = self.connection.cursor()
            
            for key, value in settings.items():
                # 직렬화할 수 있는 형태로 변환
                if isinstance(value, bool):
                    value = 1 if value else 0
                elif not isinstance(value, (str, int, float)):
                    value = str(value)
                
                # UPSERT 구문 (SQLite 3.24.0 이상)
                cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                ''', (key, str(value)))
            
            self.connection.commit()
            log_info(f"{len(settings)} 개의 설정이 저장되었습니다")
            return True
        except sqlite3.Error as e:
            log_error(f"설정 저장 중 오류 발생: {e}")
            self.connection.rollback()
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """
        데이터베이스에서 모든 설정을 불러옵니다.
        
        Returns:
            설정 딕셔너리
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT key, value FROM settings')
            
            settings = {}
            for key, value in cursor.fetchall():
                # 기본 타입으로 변환 시도
                try:
                    # 정수 변환 시도
                    if value.isdigit():
                        settings[key] = int(value)
                    # 불리언 변환 시도
                    elif value.lower() in ('true', 'false', '1', '0'):
                        settings[key] = value.lower() in ('true', '1')
                    # 실수 변환 시도
                    elif '.' in value and all(part.isdigit() for part in value.split('.', 1)):
                        settings[key] = float(value)
                    else:
                        settings[key] = value
                except (ValueError, AttributeError):
                    settings[key] = value
            
            log_info(f"{len(settings)} 개의 설정을 불러왔습니다")
            return settings
        except sqlite3.Error as e:
            log_error(f"설정 불러오기 중 오류 발생: {e}")
            return {}
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        특정 설정 값을 불러옵니다.
        
        Args:
            key: 설정 키
            default: 설정이 없을 경우 반환할 기본값
            
        Returns:
            설정 값 또는 기본값
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            if result:
                value = result[0]
                # 기본 타입으로 변환 시도
                try:
                    if value.isdigit():
                        return int(value)
                    elif value.lower() in ('true', 'false', '1', '0'):
                        return value.lower() in ('true', '1')
                    elif '.' in value and all(part.isdigit() for part in value.split('.', 1)):
                        return float(value)
                    else:
                        return value
                except (ValueError, AttributeError):
                    return value
            return default
        except sqlite3.Error as e:
            log_error(f"설정 '{key}' 불러오기 중 오류 발생: {e}")
            return default
    
    def save_media_item(self, media_item: Dict[str, Any]) -> int:
        """
        미디어 아이템 정보를 저장합니다.
        
        Args:
            media_item: 미디어 아이템 정보 딕셔너리
            
        Returns:
            생성된 아이템 ID 또는 오류 시 -1
        """
        try:
            cursor = self.connection.cursor()
            
            # 필수 필드 확인
            if 'file_path' not in media_item:
                log_error("미디어 아이템 저장 실패: file_path 없음")
                return -1
            
            # UPSERT 구문
            cursor.execute('''
            INSERT INTO media_items (
                file_path, media_type, title, year, season, episode, 
                original_filename, destination_path, processed, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path) DO UPDATE SET
                media_type = excluded.media_type,
                title = excluded.title,
                year = excluded.year,
                season = excluded.season,
                episode = excluded.episode,
                original_filename = excluded.original_filename,
                destination_path = excluded.destination_path,
                processed = excluded.processed,
                updated_at = CURRENT_TIMESTAMP
            ''', (
                media_item.get('file_path'),
                media_item.get('media_type'),
                media_item.get('title'),
                media_item.get('year'),
                media_item.get('season'),
                media_item.get('episode'),
                media_item.get('original_filename'),
                media_item.get('destination_path'),
                1 if media_item.get('processed') else 0
            ))
            
            self.connection.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.execute(
                'SELECT id FROM media_items WHERE file_path = ?', 
                (media_item.get('file_path'),)
            ).fetchone()[0]
        except sqlite3.Error as e:
            log_error(f"미디어 아이템 저장 중 오류 발생: {e}")
            self.connection.rollback()
            return -1
    
    def get_media_item(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        파일 경로로 미디어 아이템을 검색합니다.
        
        Args:
            file_path: 찾을 파일 경로
            
        Returns:
            미디어 아이템 정보 또는 없을 경우 None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            SELECT id, file_path, media_type, title, year, season, episode, 
                   original_filename, destination_path, processed
            FROM media_items
            WHERE file_path = ?
            ''', (file_path,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'file_path': result[1],
                    'media_type': result[2],
                    'title': result[3],
                    'year': result[4],
                    'season': result[5],
                    'episode': result[6],
                    'original_filename': result[7],
                    'destination_path': result[8],
                    'processed': bool(result[9])
                }
            return None
        except sqlite3.Error as e:
            log_error(f"미디어 아이템 검색 중 오류 발생: {e}")
            return None
    
    def record_organization_operation(
        self, source_path: str, destination_path: str, 
        operation_type: str, success: bool, error_message: str = None
    ) -> int:
        """
        파일 정리 작업을 기록합니다.
        
        Args:
            source_path: 원본 파일 경로
            destination_path: 목적지 파일 경로
            operation_type: 작업 유형 ('COPY' 또는 'MOVE')
            success: 작업 성공 여부
            error_message: 오류 메시지 (실패 시)
            
        Returns:
            생성된 기록 ID 또는 오류 시 -1
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            INSERT INTO organization_history (
                source_path, destination_path, operation_type, success, error_message
            ) VALUES (?, ?, ?, ?, ?)
            ''', (source_path, destination_path, operation_type, 
                  1 if success else 0, error_message))
            
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            log_error(f"작업 기록 중 오류 발생: {e}")
            self.connection.rollback()
            return -1
    
    def get_organization_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        최근 정리 작업 기록을 불러옵니다.
        
        Args:
            limit: 불러올 최대 기록 수
            
        Returns:
            정리 작업 기록 리스트
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            SELECT id, source_path, destination_path, operation_type, 
                   success, error_message, created_at
            FROM organization_history
            ORDER BY created_at DESC
            LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'source_path': row[1],
                    'destination_path': row[2],
                    'operation_type': row[3],
                    'success': bool(row[4]),
                    'error_message': row[5],
                    'created_at': row[6]
                })
            
            return history
        except sqlite3.Error as e:
            log_error(f"작업 기록 조회 중 오류 발생: {e}")
            return [] 