#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter 애플리케이션 메인 모듈
"""

import os
import time
import argparse
import asyncio
from typing import List, Optional, Dict, Any

from src.models.media_item import MediaItem
from src.services.scanner_service import ScannerService
from src.services.organizer_service import OrganizerService
from src.services.parser_service import ParserService
from src.services.setting_service import SettingService
from src.database.db_manager import DatabaseManager
from src.utils.logger import log_info, log_error, log_debug, configure_logger


class Application:
    """
    애니메이션 파일 정리 애플리케이션 메인 클래스
    """
    
    def __init__(self):
        """애플리케이션 초기화"""
        # 데이터베이스 및 설정 초기화
        self.db_manager = DatabaseManager()
        self.setting_service = SettingService(self.db_manager)
        
        # 서비스 초기화
        self.scanner_service = ScannerService()
        self.parser_service = ParserService()
        self.organizer_service = OrganizerService(
            setting_service=self.setting_service,
            db_manager=self.db_manager
        )
        
        self.input_dir = None
        self.output_dir = None
        self.preview_mode = False
    
    def configure(self, args: argparse.Namespace) -> None:
        """
        커맨드 라인 인자로 애플리케이션 설정
        
        Args:
            args: 커맨드 라인 인자
        """
        # 필수 인자가 있을 경우에만 설정
        if hasattr(args, 'input_dir') and args.input_dir:
            self.input_dir = args.input_dir
        
        if hasattr(args, 'output_dir') and args.output_dir:
            self.output_dir = args.output_dir
            
        if hasattr(args, 'preview'):
            self.preview_mode = args.preview
        
        # 명령줄에서 설정이 제공된 경우 업데이트
        settings_to_update = {}
        
        if hasattr(args, 'operation') and args.operation:
            settings_to_update["operation_type"] = args.operation
            
        if hasattr(args, 'recursive') and args.recursive is not None:
            settings_to_update["scan_recursive"] = args.recursive
            
        if hasattr(args, 'preserve_filename') and args.preserve_filename is not None:
            settings_to_update["preserve_original_filename"] = args.preserve_filename
        
        if settings_to_update:
            self.setting_service.update_settings(settings_to_update)
            log_info("임시 설정이 적용되었습니다")
    
    async def run(self) -> int:
        """
        애플리케이션 실행
        
        Returns:
            종료 코드 (0: 성공, 기타: 오류)
        """
        # 필수 인자 검사
        if not self.input_dir or not self.output_dir:
            log_error("입력 및 출력 디렉토리가 모두 필요합니다.")
            return 1
            
        try:
            start_time = time.time()
            log_info(f"디렉토리 설정 - 입력: {self.input_dir}, 출력: {self.output_dir}")
            
            # 입력 디렉토리 검사
            if not os.path.exists(self.input_dir):
                log_error(f"입력 디렉토리를 찾을 수 없습니다: {self.input_dir}")
                return 1
            
            # 디렉토리 스캔
            log_info(f"디렉토리 비동기 스캔 시작: {self.input_dir}")
            
            # 설정에서 스캔 관련 값 가져오기
            recursive = self.setting_service.get_setting("scan_recursive")
            video_extensions_str = self.setting_service.get_setting("video_extensions")
            video_extensions = video_extensions_str.split(',') if video_extensions_str else None
            ignore_sample = self.setting_service.get_setting("ignore_sample_videos")
            
            files = await self.scanner_service.scan_directory_async(
                self.input_dir,
                recursive=recursive,
                extensions=video_extensions,
                ignore_sample=ignore_sample
            )
            
            log_info(f"스캔 완료: {len(files)}개 파일 발견")
            
            if not files:
                log_info("처리할 파일이 없습니다. 종료합니다.")
                return 0
            
            # 파일 파싱
            media_items = self.parser_service.parse_files(files)
            log_info(f"스캔 완료: {len(media_items)}개 미디어 아이템")
            
            # 미리보기 모드
            if self.preview_mode:
                log_info("미리보기 모드: 실제 파일 작업은 수행되지 않습니다")
                for item in media_items:
                    dest_path = self.organizer_service._get_destination_path(item, self.output_dir)
                    log_info(f"미리보기: {item.file_name} → {dest_path}")
                log_info(f"미리보기 완료: {len(media_items)}개 작업")
                return 0
            
            # 파일 정리
            operations = self.organizer_service.organize_files(
                media_items,
                self.output_dir,
                preview_only=False
            )
            
            # 결과 출력
            log_info(f"작업 완료: {len(operations)}개 파일 처리됨")
            elapsed_time = time.time() - start_time
            log_info(f"총 실행 시간: {elapsed_time:.2f}초")
            
            return 0
        except Exception as e:
            log_error(f"애플리케이션 실행 중 오류 발생: {e}")
            import traceback
            log_error(traceback.format_exc())
            return 1
        finally:
            # 데이터베이스 연결 종료
            if self.db_manager:
                self.db_manager.close()
                
    def show_settings(self) -> None:
        """현재 설정을 표시합니다"""
        settings = self.setting_service.get_all_settings()
        
        log_info("===== 현재 설정 =====")
        for key, value in sorted(settings.items()):
            log_info(f"{key}: {value}")
        log_info("====================")
        
    def reset_settings(self) -> None:
        """설정을 기본값으로 초기화합니다"""
        if self.setting_service.reset_to_defaults():
            log_info("설정이 기본값으로 초기화되었습니다")
        else:
            log_error("설정 초기화 중 오류가 발생했습니다")


def parse_args() -> argparse.Namespace:
    """
    커맨드 라인 인자 파싱
    
    Returns:
        파싱된 인자
    """
    parser = argparse.ArgumentParser(description="애니메이션 파일 자동 정리 도구")
    
    # 인자 그룹 생성
    main_group = parser.add_argument_group("주요 명령")
    setting_group = parser.add_argument_group("설정 관리")
    
    # 주요 명령 인자
    main_group.add_argument("input_dir", help="정리할 파일이 있는 입력 디렉토리", nargs="?")
    main_group.add_argument("output_dir", help="정리된 파일을 저장할 출력 디렉토리", nargs="?")
    main_group.add_argument("--preview", "-p", action="store_true", help="미리보기 모드 (실제 파일 작업 없음)")
    main_group.add_argument("--operation", "-o", choices=["COPY", "MOVE"], help="파일 작업 유형 (COPY 또는 MOVE)")
    main_group.add_argument("--recursive", "-r", action="store_true", help="하위 디렉토리 포함 스캔")
    main_group.add_argument("--preserve-filename", action="store_true", help="원본 파일명 유지")
    
    # 설정 관리 인자
    setting_group.add_argument("--show-settings", action="store_true", help="현재 설정 표시 후 종료")
    setting_group.add_argument("--reset-settings", action="store_true", help="설정을 기본값으로 초기화")
    
    return parser.parse_args()


async def main() -> int:
    """
    프로그램 메인 함수
    
    Returns:
        종료 코드
    """
    # 로거 설정
    configure_logger()
    log_info("애플리케이션 시작")
    
    # 인자 파싱
    args = parse_args()
    
    # 애플리케이션 인스턴스 생성
    app = Application()
    
    # 특수 커맨드 처리
    if args.show_settings:
        app.show_settings()
        return 0
        
    if args.reset_settings:
        app.reset_settings()
        return 0
    
    # 필수 인자 검사
    if not args.input_dir or not args.output_dir:
        if not (args.show_settings or args.reset_settings):
            parser = argparse.ArgumentParser()
            parser.error("input_dir과 output_dir 인자가 필요합니다")
        return 0
    
    # 애플리케이션 설정
    app.configure(args)
    
    # 애플리케이션 실행
    return await app.run()


if __name__ == "__main__":
    # 비동기 메인 함수 실행
    exit_code = asyncio.run(main())
    exit(exit_code) 