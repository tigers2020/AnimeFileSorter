#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
로거 유틸리티 사용 예제
"""

import os
import sys
import traceback
from utils.logger import Logger

def main():
    """
    로거 사용법 예제 메인 함수
    """
    # 로거 인스턴스 가져오기
    logger = Logger.get_instance()
    
    # 정보 로깅 - 프로세스 시작
    logger.log_info("애니메이션 파일 정렬 프로세스 시작")
    
    # 디버그 로깅 - 상세 정보 (파일에만 기록됨)
    logger.log_debug("설정 파일 로드 완료: 기본 설정으로 진행")
    
    # 경고 로깅 - 잠재적 문제
    logger.log_warning("일부 파일은 처리되지 않을 수 있습니다: 지원되지 않는 형식")
    
    # 파일 처리 정보 로깅
    processed_files = {
        "video": 15,
        "subtitle": 10,
        "image": 5
    }
    logger.log_info(f"처리된 파일 통계: {processed_files}")
    
    # 오류 로깅
    try:
        # 고의적인 오류 예시 - 0으로 나누기
        result = 10 / 0
    except Exception as e:
        logger.log_error(f"계산 중 오류 발생: {str(e)}")
        logger.log_exception()  # 스택 트레이스 포함
    
    # 파일 처리 오류 예제
    try:
        # 존재하지 않는 파일 열기
        with open("존재하지_않는_파일.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.log_error(f"파일 처리 중 오류 발생: {str(e)}")
        logger.log_exception("파일 액세스 실패")  # 사용자 정의 메시지와 함께 스택 트레이스
    
    # 심각한 오류 로깅
    # logger.log_critical("데이터베이스 연결 실패: 프로그램을 종료합니다")
    
    # 정보 로깅 - 프로세스 종료
    logger.log_info("애니메이션 파일 정렬 프로세스 완료")

if __name__ == "__main__":
    main() 