#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter main application entry point.
"""

import sys
import os
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Add the project root to sys.path for easier imports
root_dir = Path(__file__).parent  # 현재 디렉토리를 root_dir로 설정
sys.path.insert(0, str(root_dir))

from src.views.main_window import MainWindow
from src.models.database import init_db


# 로깅 설정
def setup_logging():
    """로깅 설정 초기화."""
    log_dir = Path.home() / '.animefilesorter' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'animefilesorter.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # 외부 라이브러리 로깅 레벨 조정
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def main():
    """Main application entry point."""
    # 로깅 설정
    setup_logging()
    
    # 데이터베이스 초기화
    init_db()
    
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("AnimeFileSorter")
    
    # Set style sheet (can be moved to a dedicated theme manager later)
    # with open(str(Path(__file__).parent / "views" / "resources" / "style.qss"), "r") as f:
    #     app.setStyleSheet(f.read())
    
    # 메인 윈도우 생성
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 