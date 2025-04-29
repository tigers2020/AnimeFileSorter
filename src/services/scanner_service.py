#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
디렉토리를 스캔하여 미디어 파일을 찾는 서비스
"""

import os
import asyncio
from pathlib import Path
from typing import List, Set, Optional

from src.utils.logger import log_info, log_error, log_debug


class ScannerService:
    """디렉토리를 스캔하여 미디어 파일을 찾는 서비스"""
    
    def __init__(self, setting_service=None):
        """
        스캐너 서비스 초기화
        
        Args:
            setting_service: 설정 서비스 인스턴스 (선택 사항)
        """
        # 설정 서비스 저장
        self.setting_service = setting_service
        
        # 기본 비디오 파일 확장자
        self.default_video_extensions = [
            ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".flv", ".webm"
        ]
        
        # 자막 파일 확장자
        self.subtitle_extensions = [
            ".srt", ".ass", ".ssa", ".vtt", ".sub"
        ]
        
        # 무시할 키워드 (샘플 파일 등)
        self.ignore_keywords = [
            "sample", "trailer", "preview", "teaser"
        ]
        
        # 설정 서비스에서 확장자 설정 로드
        if setting_service:
            # 비디오 파일 확장자 설정 로드
            video_extensions = setting_service.get_setting("video_extensions", "")
            if video_extensions:
                # 쉼표로 구분된 확장자 문자열을 리스트로 변환
                self.VIDEO_EXTENSIONS = video_extensions.split(",")
                # 마침표가 없는 확장자에 마침표 추가
                self.VIDEO_EXTENSIONS = [
                    ext if ext.startswith('.') else f".{ext}" 
                    for ext in self.VIDEO_EXTENSIONS
                ]
            else:
                self.VIDEO_EXTENSIONS = self.default_video_extensions
                
            # 자막 파일 확장자 설정 로드
            subtitle_extensions = setting_service.get_setting("subtitle_extensions", "")
            if subtitle_extensions:
                # 쉼표로 구분된 확장자 문자열을 리스트로 변환
                self.SUBTITLE_EXTENSIONS = subtitle_extensions.split(",")
                # 마침표가 없는 확장자에 마침표 추가
                self.SUBTITLE_EXTENSIONS = [
                    ext if ext.startswith('.') else f".{ext}" 
                    for ext in self.SUBTITLE_EXTENSIONS
                ]
            else:
                self.SUBTITLE_EXTENSIONS = self.subtitle_extensions
        else:
            # 설정 서비스가 없는 경우 기본값 사용
            self.VIDEO_EXTENSIONS = self.default_video_extensions
            self.SUBTITLE_EXTENSIONS = self.subtitle_extensions
    
    async def scan_directory_async(
        self,
        directory: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None,
        ignore_sample: bool = True
    ) -> List[str]:
        """
        디렉토리를 비동기적으로 스캔하여 미디어 파일 목록을 반환합니다.
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            extensions: 검색할 파일 확장자 목록 (None이면 기본값 사용)
            ignore_sample: 샘플 파일 무시 여부
            
        Returns:
            미디어 파일 경로 목록
        """
        if not os.path.exists(directory):
            log_error(f"디렉토리가 존재하지 않습니다: {directory}")
            return []
        
        if extensions is None:
            extensions = self.VIDEO_EXTENSIONS
            
        # 소문자로 변환하여 비교 일관성 유지
        extensions = [ext.lower() if not ext.startswith('.') else ext.lower() for ext in extensions]
        extensions = [ext if ext.startswith('.') else f".{ext}" for ext in extensions]
        
        # 스캔 작업을 비동기로 실행
        log_info(f"디렉토리 비동기 스캔 시작: {directory}")
        
        # 병렬 처리를 위한 태스크 생성
        loop = asyncio.get_event_loop()
        task = loop.create_task(
            self._scan_directory_task(directory, recursive, extensions, ignore_sample)
        )
        
        files = await task
        log_info(f"스캔 완료: {len(files)}개 파일 발견")
        return files
    
    async def _scan_directory_task(
        self,
        directory: str,
        recursive: bool,
        extensions: List[str],
        ignore_sample: bool
    ) -> List[str]:
        """
        디렉토리 스캔 비동기 태스크
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            extensions: 검색할 파일 확장자 목록
            ignore_sample: 샘플 파일 무시 여부
            
        Returns:
            미디어 파일 경로 목록
        """
        files = []
        
        # CPU 바운드 작업은 별도 스레드에서 실행
        # 이를 통해 UI 스레드 블로킹 방지
        files = await asyncio.get_event_loop().run_in_executor(
            None,  # 기본 실행자 사용
            self._scan_directory_sync,
            directory, recursive, extensions, ignore_sample
        )
        
        return files
    
    def _scan_directory_sync(
        self,
        directory: str,
        recursive: bool,
        extensions: List[str],
        ignore_sample: bool
    ) -> List[str]:
        """
        디렉토리를 동기적으로 스캔하여 미디어 파일 목록을 반환합니다.
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            extensions: 검색할 파일 확장자 목록
            ignore_sample: 샘플 파일 무시 여부
            
        Returns:
            미디어 파일 경로 목록
        """
        files = []
        
        try:
            if recursive:
                # 재귀적으로 모든 파일 스캔
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if self._is_media_file(file_path, extensions, ignore_sample):
                            files.append(file_path)
            else:
                # 현재 디렉토리만 스캔
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path) and self._is_media_file(file_path, extensions, ignore_sample):
                        files.append(file_path)
                        
            log_debug(f"{len(files)}개 파일 스캔됨")
        except Exception as e:
            log_error(f"디렉토리 스캔 중 오류 발생: {e}")
        
        return files
    
    def _is_media_file(
        self,
        file_path: str,
        extensions: List[str],
        ignore_sample: bool
    ) -> bool:
        """
        파일이 미디어 파일인지 확인합니다.
        
        Args:
            file_path: 확인할 파일 경로
            extensions: 미디어 파일 확장자 목록
            ignore_sample: 샘플 파일 무시 여부
            
        Returns:
            미디어 파일 여부
        """
        # 확장자 확인
        _, ext = os.path.splitext(file_path.lower())
        if ext not in extensions:
            return False
        
        # 샘플 파일 확인
        if ignore_sample:
            filename = os.path.basename(file_path).lower()
            if any(keyword in filename for keyword in self.ignore_keywords):
                log_debug(f"샘플 파일 무시됨: {filename}")
                return False
        
        return True
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None,
        ignore_sample: bool = True
    ) -> List[str]:
        """
        디렉토리를 동기적으로 스캔하여 미디어 파일 목록을 반환합니다.
        
        Args:
            directory: 스캔할 디렉토리 경로
            recursive: 하위 디렉토리 포함 여부
            extensions: 검색할 파일 확장자 목록 (None이면 기본값 사용)
            ignore_sample: 샘플 파일 무시 여부
            
        Returns:
            미디어 파일 경로 목록
        """
        if extensions is None:
            extensions = self.VIDEO_EXTENSIONS
            
        # 소문자로 변환하여 비교 일관성 유지
        extensions = [ext.lower() if not ext.startswith('.') else ext.lower() for ext in extensions]
        extensions = [ext if ext.startswith('.') else f".{ext}" for ext in extensions]
        
        return self._scan_directory_sync(directory, recursive, extensions, ignore_sample) 