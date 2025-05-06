#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter의 메인 윈도우 구현입니다.
"""

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QPushButton, QSplitter, QMenu, QToolBar, QStatusBar,
    QMenuBar, QDialog, QFileDialog, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, Slot, Signal, QSettings, QSize, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QAction

from src.views.file_browser import FileBrowser
from src.views.metadata_view import MetadataView
from src.views.login_dialog import LoginDialog
from src.views.progress_dialog import ProgressDialog
from src.views.settings_dialog import SettingsDialog
from src.api import AnimeService
from src.core import calculate_ed2k_hash, calculate_ed2k_hash_parallel
from src.core.app_config import AppConfig


class MainWindow(QMainWindow):
    """애니메이션 파일 정리 애플리케이션의 메인 윈도우."""
    
    def __init__(self):
        """메인 윈도우 초기화."""
        super().__init__()
        
        # 윈도우 기본 설정
        self.setWindowTitle("AnimeFileSorter")
        self.setMinimumSize(1200, 800)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃 설정
        main_layout = QVBoxLayout(central_widget)
        
        # 메뉴바 설정
        self._setup_menu()
        
        # 툴바 설정
        self._setup_toolbar()
        
        # 메인 스플리터 (파일 브라우저 + 메타데이터 뷰)
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 파일 브라우저 생성
        self.file_browser = FileBrowser()
        self.file_browser.file_selected.connect(self._on_file_selected)
        self.file_browser.directory_changed.connect(self._on_directory_changed)
        self.main_splitter.addWidget(self.file_browser)
        
        # 메타데이터 뷰 생성
        self.metadata_view = MetadataView()
        self.metadata_view.metadata_updated.connect(self._on_metadata_updated)
        self.main_splitter.addWidget(self.metadata_view)
        
        # 스플리터 크기 설정
        self.main_splitter.setSizes([400, 800])
        
        # 상태 표시줄 설정
        self.statusBar().showMessage("준비")
        
        # 현재 파일 정보
        self._current_file_path = None
        
        # AniDB 서비스 초기화
        self.anime_service = AnimeService()
        self.anidb_authenticated = False
        
        # 설정 로드
        self._load_settings()
    
    def _setup_menu(self):
        """메뉴바 설정."""
        # 파일 메뉴
        file_menu = self.menuBar().addMenu("파일")
        
        # 폴더 열기 액션
        open_dir_action = QAction("폴더 열기...", self)
        open_dir_action.setShortcut(QKeySequence.Open)
        open_dir_action.triggered.connect(self._open_directory)
        file_menu.addAction(open_dir_action)
        
        # 파일 스캔 액션
        scan_action = QAction("ED2K 해시 계산", self)
        scan_action.setShortcut(QKeySequence("Ctrl+E"))
        scan_action.triggered.connect(self._calculate_hash)
        file_menu.addAction(scan_action)
        
        file_menu.addSeparator()
        
        # 종료 액션
        exit_action = QAction("종료", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 편집 메뉴
        edit_menu = self.menuBar().addMenu("편집")
        
        # 편집 모드 액션
        edit_mode_action = QAction("편집 모드", self)
        edit_mode_action.setShortcut(QKeySequence("Ctrl+M"))
        edit_mode_action.setCheckable(True)
        edit_mode_action.toggled.connect(self._toggle_edit_mode)
        edit_menu.addAction(edit_mode_action)
        
        # 메타데이터 저장 액션
        save_metadata_action = QAction("메타데이터 저장", self)
        save_metadata_action.setShortcut(QKeySequence.Save)
        save_metadata_action.triggered.connect(self._save_metadata)
        edit_menu.addAction(save_metadata_action)
        
        # AniDB 메뉴
        anidb_menu = self.menuBar().addMenu("AniDB")
        
        # 로그인 액션
        self.login_action = QAction("AniDB 로그인...", self)
        self.login_action.triggered.connect(self._anidb_login)
        anidb_menu.addAction(self.login_action)
        
        # 로그아웃 액션
        self.logout_action = QAction("AniDB 로그아웃", self)
        self.logout_action.triggered.connect(self._anidb_logout)
        self.logout_action.setEnabled(False)
        anidb_menu.addAction(self.logout_action)
        
        anidb_menu.addSeparator()
        
        # 파일 식별 액션
        self.identify_action = QAction("파일 식별", self)
        self.identify_action.setShortcut(QKeySequence("Ctrl+I"))
        self.identify_action.triggered.connect(self._identify_file)
        self.identify_action.setEnabled(False)
        anidb_menu.addAction(self.identify_action)
        
        # 메타데이터 검색 액션
        self.search_action = QAction("애니메이션 검색...", self)
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.search_action.triggered.connect(self._search_anidb)
        self.search_action.setEnabled(False)
        anidb_menu.addAction(self.search_action)
        
        # 도구 메뉴
        tools_menu = self.menuBar().addMenu("도구")
        
        # 설정 액션
        settings_action = QAction("설정...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # 데이터베이스 관리 액션
        db_action = QAction("데이터베이스 관리", self)
        db_action.triggered.connect(self._manage_database)
        tools_menu.addAction(db_action)
        
        # 도움말 메뉴
        help_menu = self.menuBar().addMenu("도움말")
        
        # 정보 액션
        about_action = QAction("정보", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """툴바 설정."""
        toolbar = QToolBar("메인 툴바")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 폴더 열기 버튼
        open_dir_button = QPushButton("폴더 열기")
        open_dir_button.clicked.connect(self._open_directory)
        toolbar.addWidget(open_dir_button)
        
        toolbar.addSeparator()
        
        # 해시 계산 버튼
        hash_button = QPushButton("ED2K 해시 계산")
        hash_button.clicked.connect(self._calculate_hash)
        toolbar.addWidget(hash_button)
        
        # AniDB 로그인 버튼
        self.login_button = QPushButton("AniDB 로그인")
        self.login_button.clicked.connect(self._anidb_login)
        toolbar.addWidget(self.login_button)
        
        # AniDB 식별 버튼
        self.identify_button = QPushButton("파일 식별")
        self.identify_button.clicked.connect(self._identify_file)
        self.identify_button.setEnabled(False)
        toolbar.addWidget(self.identify_button)
        
        toolbar.addSeparator()
        
        # 편집 모드 버튼
        edit_button = QPushButton("편집 모드")
        edit_button.setCheckable(True)
        edit_button.toggled.connect(self._toggle_edit_mode)
        toolbar.addWidget(edit_button)
    
    def _load_settings(self):
        """설정 로드."""
        settings = QSettings("AnimeFileSorter", "MainWindow")
        
        # 윈도우 위치 및 크기
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 마지막 디렉토리
        last_dir = settings.value("last_directory")
        if last_dir and os.path.exists(last_dir):
            self.file_browser.set_directory(last_dir)
    
    def _save_settings(self):
        """설정 저장."""
        settings = QSettings("AnimeFileSorter", "MainWindow")
        
        # 윈도우 위치 및 크기
        settings.setValue("geometry", self.saveGeometry())
        
        # 현재 디렉토리
        current_dir = self.file_browser.get_current_directory()
        if current_dir:
            settings.setValue("last_directory", current_dir)
    
    def closeEvent(self, event):
        """윈도우 종료 이벤트."""
        self._save_settings()
        
        # AniDB 로그아웃
        if self.anidb_authenticated:
            self.anime_service.disconnect()
        
        event.accept()
    
    @Slot(str)
    def _on_file_selected(self, file_path):
        """파일 선택 이벤트 핸들러."""
        if not file_path or not os.path.exists(file_path):
            return
        
        self._current_file_path = file_path
        self.statusBar().showMessage(f"파일 선택됨: {os.path.basename(file_path)}")
        
        # 파일 정보 가져오기
        from src.core.file_utils import get_file_info
        file_info = get_file_info(file_path)
        
        # 메타데이터 뷰 업데이트
        self.metadata_view.set_file_info(file_info)
        
        # 데이터베이스에서 파일 정보 조회
        self._load_file_metadata(file_path)
    
    @Slot(str)
    def _on_directory_changed(self, directory):
        """디렉토리 변경 이벤트 핸들러."""
        self.statusBar().showMessage(f"디렉토리 변경됨: {directory}")
    
    @Slot(dict)
    def _on_metadata_updated(self, metadata):
        """메타데이터 업데이트 이벤트 핸들러."""
        file_path = metadata.get('file_path')
        if not file_path:
            return
        
        self.statusBar().showMessage(f"메타데이터 업데이트됨: {os.path.basename(file_path)}")
        
        # TODO: 데이터베이스에 메타데이터 저장
    
    def _open_directory(self):
        """디렉토리 열기 대화상자 표시."""
        directory = self.file_browser.select_directory()
        if directory:
            self.statusBar().showMessage(f"디렉토리 열기: {directory}")
    
    def _calculate_hash(self):
        """선택된 파일의 ED2K 해시 계산."""
        if not self._current_file_path:
            QMessageBox.warning(self, "경고", "파일을 먼저 선택해주세요.")
            return
        
        file_name = os.path.basename(self._current_file_path)
        self.statusBar().showMessage(f"ED2K 해시 계산 중: {file_name}")
        
        def hash_task(progress_callback=None, status_callback=None):
            """해시 계산 작업 함수."""
            # 콜백 함수 생성
            def callback(current, total):
                if progress_callback:
                    progress_callback(current, total)
                if status_callback:
                    percentage = int((current / total) * 100)
                    status_callback(f"ED2K 해시 계산 중: {percentage}%")
            
            # 해시 계산
            hash_value = calculate_ed2k_hash_parallel(self._current_file_path, callback=callback)
            
            # 결과 딕셔너리 반환
            from src.core.file_utils import get_file_info
            file_info = get_file_info(self._current_file_path)
            file_info['ed2k_hash'] = hash_value
            return file_info
        
        # 진행 대화 상자 표시
        file_info = ProgressDialog.run(
            "ED2K 해시 계산",
            f"파일 '{file_name}'의 ED2K 해시를 계산하는 중...",
            hash_task,
            parent=self
        )
        
        if file_info:
            # 메타데이터 뷰 업데이트
            self.metadata_view.set_file_info(file_info)
            self.statusBar().showMessage(f"ED2K 해시 계산 완료: {file_info['ed2k_hash']}")
            
            # 식별 버튼 활성화 (AniDB 인증 됐을 경우)
            if self.anidb_authenticated:
                self.identify_button.setEnabled(True)
                self.identify_action.setEnabled(True)
    
    def _anidb_login(self):
        """AniDB 로그인 대화상자 표시."""
        username, password = LoginDialog.get_credentials(self)
        
        if not username or not password:
            return
        
        self.statusBar().showMessage("AniDB 로그인 중...")
        
        def login_task(username, password, progress_callback=None, status_callback=None):
            """로그인 작업 함수."""
            if status_callback:
                status_callback("AniDB 서버에 연결 중...")
            
            # 로그인 시도
            success = self.anime_service.connect(username, password)
            
            if status_callback:
                if success:
                    status_callback("AniDB 로그인 성공!")
                else:
                    status_callback("AniDB 로그인 실패")
            
            return success
        
        # 진행 대화 상자 표시
        success = ProgressDialog.run(
            "AniDB 로그인",
            "AniDB 서버에 로그인하는 중...",
            login_task,
            username,
            password,
            parent=self,
            cancellable=False
        )
        
        if success:
            self.anidb_authenticated = True
            self.statusBar().showMessage(f"AniDB 로그인 성공: {username}")
            
            # UI 버튼 상태 업데이트
            self.login_button.setText("AniDB 연결됨")
            self.login_button.setEnabled(False)
            self.login_action.setEnabled(False)
            self.logout_action.setEnabled(True)
            
            # 현재 파일이 있고 ED2K 해시가 있으면 식별 버튼 활성화
            if self._current_file_path:
                from src.core.file_utils import get_file_info
                file_info = get_file_info(self._current_file_path)
                if file_info.get('ed2k_hash'):
                    self.identify_button.setEnabled(True)
                    self.identify_action.setEnabled(True)
            
            # 검색 버튼 활성화
            self.search_action.setEnabled(True)
        else:
            self.statusBar().showMessage("AniDB 로그인 실패")
            QMessageBox.warning(
                self,
                "로그인 실패",
                "AniDB 로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요."
            )
    
    def _anidb_logout(self):
        """AniDB 로그아웃."""
        if not self.anidb_authenticated:
            return
        
        self.anime_service.disconnect()
        self.anidb_authenticated = False
        
        # UI 버튼 상태 업데이트
        self.login_button.setText("AniDB 로그인")
        self.login_button.setEnabled(True)
        self.login_action.setEnabled(True)
        self.logout_action.setEnabled(False)
        self.identify_button.setEnabled(False)
        self.identify_action.setEnabled(False)
        self.search_action.setEnabled(False)
        
        self.statusBar().showMessage("AniDB 로그아웃 완료")
    
    def _identify_file(self):
        """AniDB에서 파일 식별."""
        if not self._current_file_path:
            QMessageBox.warning(self, "경고", "파일을 먼저 선택해주세요.")
            return
        
        if not self.anidb_authenticated:
            reply = QMessageBox.question(
                self,
                "AniDB 로그인 필요",
                "파일 식별을 위해 AniDB에 로그인해야 합니다. 지금 로그인하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self._anidb_login()
            
            if not self.anidb_authenticated:
                return
        
        file_name = os.path.basename(self._current_file_path)
        
        def identify_task(progress_callback=None, status_callback=None):
            """파일 식별 작업 함수."""
            if status_callback:
                status_callback("파일 정보 수집 중...")
            
            # 파일 식별 및 정보 검색
            file_info = self.anime_service.identify_file(self._current_file_path)
            
            if status_callback:
                if file_info and 'anidb' in file_info:
                    status_callback("AniDB에서 정보를 찾았습니다.")
                else:
                    status_callback("AniDB에서 정보를 찾을 수 없습니다.")
            
            # 데이터베이스에 저장
            if file_info and 'anidb' in file_info:
                if status_callback:
                    status_callback("데이터베이스에 정보 저장 중...")
                
                self.anime_service.save_file_info_to_db(file_info)
            
            return file_info
        
        # 진행 대화 상자 표시
        file_info = ProgressDialog.run(
            "파일 식별",
            f"파일 '{file_name}'을 AniDB에서 식별 중...",
            identify_task,
            parent=self
        )
        
        if file_info:
            if 'anidb' in file_info:
                self.statusBar().showMessage(f"파일 식별 완료: {file_name}")
                
                # 식별된 정보 표시
                anidb_info = file_info['anidb']
                anime_title = (anidb_info.get('anime_english') or 
                              anidb_info.get('anime_romaji') or 
                              anidb_info.get('anime_kanji', '알 수 없음'))
                
                ep_number = anidb_info.get('ep_number', '??')
                ep_title = (anidb_info.get('ep_english') or 
                           anidb_info.get('ep_romaji') or 
                           anidb_info.get('ep_kanji', ''))
                
                QMessageBox.information(
                    self,
                    "파일 식별 결과",
                    f"애니메이션: {anime_title}\n"
                    f"에피소드: {ep_number} - {ep_title}"
                )
                
                # 데이터베이스에서 최신 정보 로드
                self._load_file_metadata(self._current_file_path, refresh=True)
                
            else:
                self.statusBar().showMessage(f"AniDB에서 파일을 식별할 수 없습니다: {file_name}")
                QMessageBox.warning(
                    self,
                    "식별 실패",
                    f"AniDB에서 파일 '{file_name}'을 식별할 수 없습니다.\n"
                    "파일이 AniDB에 등록되지 않았거나 ED2K 해시가 일치하지 않습니다."
                )
    
    def _search_anidb(self):
        """AniDB 검색."""
        if not self.anidb_authenticated:
            reply = QMessageBox.question(
                self,
                "AniDB 로그인 필요",
                "AniDB 검색을 위해 로그인해야 합니다. 지금 로그인하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self._anidb_login()
            
            if not self.anidb_authenticated:
                return
        
        self.statusBar().showMessage("AniDB 검색 기능은 추후 업데이트에서 구현될 예정입니다.")
        QMessageBox.information(
            self,
            "기능 준비 중",
            "AniDB 애니메이션 검색 기능은 추후 업데이트에서 구현될 예정입니다."
        )
    
    def _toggle_edit_mode(self, checked):
        """편집 모드 토글."""
        self.metadata_view.set_editable(checked)
        self.statusBar().showMessage(f"편집 모드: {'활성화' if checked else '비활성화'}")
    
    def _save_metadata(self):
        """메타데이터 저장."""
        # 편집 모드에서 저장 버튼 클릭 시뮬레이션
        if self._current_file_path:
            self.metadata_view._save_changes()
    
    def _show_settings(self):
        """설정 대화 상자 표시."""
        result = SettingsDialog.show_settings(self)
        
        if result == QDialog.Accepted:
            # 설정이 변경되었으면 애플리케이션에 적용
            self._apply_settings()
            self.statusBar().showMessage("설정이 저장되었습니다.", 3000)
    
    def _apply_settings(self):
        """변경된 설정을 애플리케이션에 적용."""
        # 설정 로드
        config = AppConfig()
        
        # UI 테마 적용
        theme = config.get('ui', 'theme', '시스템 기본')
        if theme == '다크 모드':
            self._apply_dark_theme()
        elif theme == '라이트 모드':
            self._apply_light_theme()
        # 시스템 기본값은 별도 처리 없음
        
        # 상태 표시줄 표시 설정
        show_status_bar = config.get('ui', 'show_status_bar', True)
        self.statusBar().setVisible(show_status_bar)
        
        # AnimeService 설정 업데이트
        if self.anime_service:
            # 클라이언트 이름과 버전 설정
            self.anime_service.client_name = config.get('anidb', 'udp_client_name', 'animefilesorterudp')
            self.anime_service.client_version = config.get('anidb', 'udp_client_version', 1)
            
            # 캐시 디렉토리 설정
            cache_dir = config.get('anidb', 'cache_directory', '')
            if cache_dir and self.anime_service.http_client:
                self.anime_service.http_client.cache_dir = cache_dir
    
    def _apply_dark_theme(self):
        """다크 테마 적용."""
        # 다크 테마 스타일시트 적용
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                color: #E1E1E1;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #E1E1E1;
            }
            QMenuBar::item:selected {
                background-color: #3E3E40;
            }
            QMenu {
                background-color: #1E1E1E;
                color: #E1E1E1;
                border: 1px solid #3E3E40;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
            QToolBar {
                background-color: #2D2D30;
                border-bottom: 1px solid #3E3E40;
            }
            QPushButton {
                background-color: #3E3E40;
                color: #E1E1E1;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #454548;
            }
            QPushButton:pressed {
                background-color: #2D2D30;
            }
            QTabWidget::pane {
                border: 1px solid #3E3E40;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #E1E1E1;
                border: 1px solid #3E3E40;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3E3E40;
            }
            QLineEdit, QTextEdit {
                background-color: #1E1E1E;
                color: #E1E1E1;
                border: 1px solid #3E3E40;
            }
            QStatusBar {
                background-color: #1E1E1E;
                color: #E1E1E1;
            }
        """)
    
    def _apply_light_theme(self):
        """라이트 테마 적용."""
        # 라이트 테마는 기본 스타일을 사용하므로 스타일시트 초기화
        self.setStyleSheet("")
    
    def _manage_database(self):
        """데이터베이스 관리 대화상자 표시."""
        self.statusBar().showMessage("데이터베이스 관리 기능은 아직 구현되지 않았습니다.")
    
    def _show_about(self):
        """정보 대화상자 표시."""
        QMessageBox.about(
            self,
            "AnimeFileSorter 정보",
            "AnimeFileSorter v0.1.0\n\n"
            "애니메이션 파일 정리 및 관리 애플리케이션\n"
            "1년차 2분기 프로토타입\n\n"
            "© 2023 AnimeFileSorter Team"
        )
    
    def _load_file_metadata(self, file_path, refresh=False):
        """
        파일 관련 메타데이터 로드.
        
        Args:
            file_path: 파일 경로
            refresh: 데이터베이스에서 강제로 새로 로드할지 여부
        """
        # 이 부분은 나중에 실제 데이터베이스에서 로드하도록 구현해야 함
        # 지금은 샘플 데이터로 표시
        
        # 파일명에서 정보 추출 (임시)
        filename = os.path.basename(file_path)
        
        import datetime
        import random
        
        # 샘플 시리즈 정보
        series_data = {
            'title': "샘플 시리즈",
            'title_japanese': "サンプルシリーズ",
            'title_korean': "샘플 시리즈",
            'anidb_id': 12345,
            'type': "TV",
            'episodes_count': 24,
            'status': "완료",
            'start_date': datetime.datetime(2020, 1, 1),
            'end_date': datetime.datetime(2020, 6, 30),
            'genres': "액션,모험,판타지",
            'description': "이것은 샘플 시리즈에 대한 설명입니다. 실제 정보는 데이터베이스에서 로드됩니다.",
            'rating': 8.5,
            'poster_url': ""  # 실제 URL이나 경로 필요
        }
        
        # 샘플 에피소드 정보
        episode_data = {
            'number': 1,
            'type': "일반",
            'title': "첫 번째 에피소드",
            'title_japanese': "最初のエピソード",
            'title_korean': "첫 번째 에피소드",
            'air_date': datetime.datetime(2020, 1, 1),
            'duration': 24,
            'description': "이것은 첫 번째 에피소드에 대한 설명입니다. 실제 정보는 데이터베이스에서 로드됩니다.",
            'watch_history': [
                {
                    'watched_date': datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
                    'position': 1300,  # 초 단위
                    'completed': True,
                    'play_count': 2
                }
            ]
        }
        
        # 메타데이터 뷰 업데이트
        self.metadata_view.set_series_info(series_data)
        self.metadata_view.set_episode_info(episode_data) 