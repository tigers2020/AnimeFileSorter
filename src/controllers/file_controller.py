#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애니메이션 파일 관리를 위한 컨트롤러 모듈입니다.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.file_utils import (
    scan_directory, 
    calculate_ed2k_hash, 
    get_file_metadata
)
from src.models.database import get_session
from src.models.file_model import AnimeFile


class FileController:
    """애니메이션 파일 관리를 위한 컨트롤러."""
    
    def __init__(self):
        """FileController 초기화."""
        self.session = get_session()
    
    def scan_for_anime_files(self, directory: str, recursive: bool = True) -> List[str]:
        """
        지정된 디렉토리에서 애니메이션 파일을 스캔합니다.
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 스캔할지 여부
            
        Returns:
            발견된 비디오 파일 경로 목록
        """
        return scan_directory(directory, recursive)
    
    def process_file(self, file_path: str) -> Optional[AnimeFile]:
        """
        파일을 처리하고 데이터베이스에 저장합니다.
        
        Args:
            file_path: 처리할 파일 경로
            
        Returns:
            생성된 AnimeFile 객체, 실패 시 None
        """
        try:
            # 파일 메타데이터 가져오기
            metadata = get_file_metadata(file_path)
            
            # 이미 처리된 파일인지 확인
            existing_file = self.session.query(AnimeFile).filter_by(path=file_path).first()
            if existing_file:
                # 필요한 경우 업데이트 로직 추가
                return existing_file
            
            # ED2K 해시 계산 (오래 걸릴 수 있음)
            ed2k_hash = calculate_ed2k_hash(file_path)
            
            # 파일 정보 생성
            path_obj = Path(file_path)
            anime_file = AnimeFile(
                path=file_path,
                filename=path_obj.name,
                directory=str(path_obj.parent),
                size=metadata['size'],
                extension=metadata['extension'],
                modified_date=metadata['modified_time'],
                ed2k_hash=ed2k_hash
            )
            
            # 데이터베이스에 저장
            self.session.add(anime_file)
            self.session.commit()
            
            return anime_file
        
        except Exception as e:
            self.session.rollback()
            print(f"파일 처리 중 오류 발생: {e}")
            return None
    
    def get_all_anime_files(self) -> List[AnimeFile]:
        """
        저장된 모든 애니메이션 파일을 가져옵니다.
        
        Returns:
            AnimeFile 객체 목록
        """
        return self.session.query(AnimeFile).all()
    
    def get_file_by_hash(self, ed2k_hash: str) -> Optional[AnimeFile]:
        """
        ED2K 해시로 파일을 검색합니다.
        
        Args:
            ed2k_hash: 검색할 ED2K 해시
            
        Returns:
            일치하는 AnimeFile 객체, 없으면 None
        """
        return self.session.query(AnimeFile).filter_by(ed2k_hash=ed2k_hash).first()
    
    def update_file_metadata(self, file_id: int, metadata: Dict[str, Any]) -> bool:
        """
        파일 메타데이터를 업데이트합니다.
        
        Args:
            file_id: 업데이트할 파일 ID
            metadata: 업데이트할 메타데이터
            
        Returns:
            성공 여부
        """
        try:
            anime_file = self.session.query(AnimeFile).filter_by(id=file_id).first()
            if not anime_file:
                return False
            
            # 메타데이터 업데이트
            for key, value in metadata.items():
                if hasattr(anime_file, key):
                    setattr(anime_file, key, value)
            
            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            print(f"메타데이터 업데이트 중 오류 발생: {e}")
            return False
    
    def delete_file_record(self, file_id: int) -> bool:
        """
        파일 레코드를 삭제합니다.
        
        Args:
            file_id: 삭제할 파일 ID
            
        Returns:
            성공 여부
        """
        try:
            anime_file = self.session.query(AnimeFile).filter_by(id=file_id).first()
            if not anime_file:
                return False
            
            self.session.delete(anime_file)
            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            print(f"파일 레코드 삭제 중 오류 발생: {e}")
            return False 