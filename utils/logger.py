#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
애니메이션 파일 정렬기를 위한 로깅 유틸리티
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Optional, Union, Dict, Any

class Logger:
    """
    싱글톤 패턴을 사용한 로깅 클래스
    콘솔 및 파일에 로그 메시지를 기록합니다.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'Logger':
        """
        Logger 클래스의 싱글톤 인스턴스를 반환합니다.
        
        Returns:
            Logger: Logger 클래스의 인스턴스
        """
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
    
    def __init__(self):
        """
        로거를 초기화하고 콘솔과 파일 핸들러를 설정합니다.
        """
        if Logger._instance is not None:
            raise Exception("이 클래스는 싱글톤입니다. get_instance() 메서드를 사용하세요.")
            
        # 기존 로거 인스턴스가 없는 경우에만 초기화 진행
        self.logger = logging.getLogger('AnimeFileSorter')
        self.logger.setLevel(logging.DEBUG)  # 모든 로그 레벨 캡처
        
        # 로그 포맷 설정
        log_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)  # 콘솔에는 INFO 이상만 표시
        
        # 파일 핸들러 설정
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)  # logs 디렉토리 생성
        
        log_filename = f"anime_sorter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(logs_dir, log_filename)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 레벨 기록
        
        # 핸들러 추가
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # 시작 로그 메시지
        self.log_info(f"로거 초기화 완료: {log_path}")
    
    def log_debug(self, message: str) -> None:
        """
        디버그 수준의 로그 메시지를 기록합니다.
        
        Args:
            message (str): 기록할 메시지
        """
        self.logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """
        정보 수준의 로그 메시지를 기록합니다.
        
        Args:
            message (str): 기록할 메시지
        """
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """
        경고 수준의 로그 메시지를 기록합니다.
        
        Args:
            message (str): 기록할 메시지
        """
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """
        오류 수준의 로그 메시지를 기록합니다.
        
        Args:
            message (str): 기록할 메시지
        """
        self.logger.error(message)
    
    def log_critical(self, message: str) -> None:
        """
        심각한 수준의 로그 메시지를 기록합니다.
        
        Args:
            message (str): 기록할 메시지
        """
        self.logger.critical(message)
    
    def log_exception(self, message: Optional[str] = None) -> None:
        """
        현재 예외에 대한 스택 트레이스를 포함한 예외 로그를 기록합니다.
        
        Args:
            message (Optional[str]): 예외와 함께 기록할 추가 메시지
        """
        if message:
            self.logger.exception(message)
        else:
            self.logger.exception("예외 발생:") 