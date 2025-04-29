#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Settings screen for AnimeFileSorter.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QFileDialog,
    QSpinBox,
    QMessageBox,
    QScrollArea
)


class SettingsTab(QScrollArea):
    """Base class for settings tabs with scrollable content."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        # Content widget
        self.content = QWidget()
        self.setWidget(self.content)
        
        # Content layout
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)


class GeneralSettingsTab(SettingsTab):
    """General application settings tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Default directories
        self.dir_group = QGroupBox("기본 디렉토리")
        dir_layout = QFormLayout()
        
        self.input_dir = QLineEdit()
        dir_layout.addRow("입력 디렉토리:", self.input_dir)
        
        self.input_browse = QPushButton("찾아보기")
        dir_layout.addWidget(self.input_browse)
        
        self.output_dir = QLineEdit()
        dir_layout.addRow("출력 디렉토리:", self.output_dir)
        
        self.output_browse = QPushButton("찾아보기")
        dir_layout.addWidget(self.output_browse)
        
        self.dir_group.setLayout(dir_layout)
        self.layout.addWidget(self.dir_group)
        
        # Appearance settings
        self.appearance_group = QGroupBox("모양")
        appearance_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["라이트", "다크", "시스템"])
        appearance_layout.addRow("테마:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["한국어", "영어", "일본어"])
        appearance_layout.addRow("언어:", self.language_combo)
        
        self.appearance_group.setLayout(appearance_layout)
        self.layout.addWidget(self.appearance_group)
        
        # Behavior settings
        self.behavior_group = QGroupBox("동작")
        behavior_layout = QFormLayout()
        
        self.startup_check = QCheckBox("시작시 업데이트 확인")
        behavior_layout.addRow(self.startup_check)
        
        self.auto_scan_check = QCheckBox("폴더 열 때 자동 스캔")
        behavior_layout.addRow(self.auto_scan_check)
        
        self.confirm_check = QCheckBox("파일 정리 전 확인")
        self.confirm_check.setChecked(True)
        behavior_layout.addRow(self.confirm_check)
        
        self.behavior_group.setLayout(behavior_layout)
        self.layout.addWidget(self.behavior_group)
        
        # Connect signals
        self.input_browse.clicked.connect(self.on_input_browse)
        self.output_browse.clicked.connect(self.on_output_browse)
        
        # Add stretch to the end
        self.layout.addStretch()
    
    def on_input_browse(self):
        """Handle input directory browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "입력 디렉토리 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.input_dir.setText(directory)
    
    def on_output_browse(self):
        """Handle output directory browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "출력 디렉토리 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.output_dir.setText(directory)


class FileOrganizationTab(SettingsTab):
    """File organization settings tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Organization settings
        self.organization_group = QGroupBox("파일 정리 설정")
        org_layout = QFormLayout()
        
        self.create_subfolder_check = QCheckBox("시리즈별 서브폴더 생성")
        self.create_subfolder_check.setChecked(True)
        org_layout.addRow(self.create_subfolder_check)
        
        self.season_folder_check = QCheckBox("시즌별 서브폴더 생성")
        self.season_folder_check.setChecked(True)
        org_layout.addRow(self.season_folder_check)
        
        self.move_subtitles_check = QCheckBox("자막 파일 비디오와 함께 이동")
        self.move_subtitles_check.setChecked(True)
        org_layout.addRow(self.move_subtitles_check)
        
        self.organization_group.setLayout(org_layout)
        self.layout.addWidget(self.organization_group)
        
        # Naming pattern
        self.naming_group = QGroupBox("파일명 패턴")
        naming_layout = QFormLayout()
        
        self.series_pattern = QLineEdit("{series_name}")
        naming_layout.addRow("시리즈 폴더 패턴:", self.series_pattern)
        
        self.season_pattern = QLineEdit("Season {season_number}")
        naming_layout.addRow("시즌 폴더 패턴:", self.season_pattern)
        
        self.episode_pattern = QLineEdit("{series_name} - S{season_number}E{episode_number} - {episode_title}")
        naming_layout.addRow("에피소드 파일 패턴:", self.episode_pattern)
        
        self.movie_pattern = QLineEdit("{title} ({year})")
        naming_layout.addRow("영화 파일 패턴:", self.movie_pattern)
        
        pattern_help = QLabel("사용 가능한 변수: {series_name}, {season_number}, {episode_number}, {episode_title}, {year}, {title}")
        pattern_help.setWordWrap(True)
        naming_layout.addRow(pattern_help)
        
        self.naming_group.setLayout(naming_layout)
        self.layout.addWidget(self.naming_group)
        
        # File handling
        self.handling_group = QGroupBox("파일 처리")
        handling_layout = QFormLayout()
        
        self.duplicate_combo = QComboBox()
        self.duplicate_combo.addItems(["항상 묻기", "더 높은 해상도 유지", "더 큰 파일 유지", "더 최신 파일 유지"])
        handling_layout.addRow("중복 처리:", self.duplicate_combo)
        
        self.handling_group.setLayout(handling_layout)
        self.layout.addWidget(self.handling_group)
        
        # Add stretch to the end
        self.layout.addStretch()


class APISettingsTab(SettingsTab):
    """API integration settings tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # TMDB API settings
        self.tmdb_group = QGroupBox("TMDB API")
        tmdb_layout = QFormLayout()
        
        self.tmdb_enable = QCheckBox("TMDB API 사용")
        self.tmdb_enable.setChecked(True)
        tmdb_layout.addRow(self.tmdb_enable)
        
        self.tmdb_key = QLineEdit()
        self.tmdb_key.setPlaceholderText("TMDB API 키")
        tmdb_layout.addRow("API 키:", self.tmdb_key)
        
        self.test_tmdb_button = QPushButton("연결 테스트")
        tmdb_layout.addWidget(self.test_tmdb_button)
        
        self.tmdb_group.setLayout(tmdb_layout)
        self.layout.addWidget(self.tmdb_group)
        
        # AniList API settings
        self.anilist_group = QGroupBox("AniList API")
        anilist_layout = QFormLayout()
        
        self.anilist_enable = QCheckBox("AniList API 사용")
        self.anilist_enable.setChecked(True)
        anilist_layout.addRow(self.anilist_enable)
        
        self.anilist_client_id = QLineEdit()
        self.anilist_client_id.setPlaceholderText("AniList 클라이언트 ID")
        anilist_layout.addRow("클라이언트 ID:", self.anilist_client_id)
        
        self.test_anilist_button = QPushButton("연결 테스트")
        anilist_layout.addWidget(self.test_anilist_button)
        
        self.anilist_group.setLayout(anilist_layout)
        self.layout.addWidget(self.anilist_group)
        
        # OpenSubtitles API settings
        self.opensubs_group = QGroupBox("OpenSubtitles API")
        opensubs_layout = QFormLayout()
        
        self.opensubs_enable = QCheckBox("OpenSubtitles API 사용")
        opensubs_layout.addRow(self.opensubs_enable)
        
        self.opensubs_username = QLineEdit()
        opensubs_layout.addRow("사용자명:", self.opensubs_username)
        
        self.opensubs_password = QLineEdit()
        self.opensubs_password.setEchoMode(QLineEdit.Password)
        opensubs_layout.addRow("비밀번호:", self.opensubs_password)
        
        self.test_opensubs_button = QPushButton("연결 테스트")
        opensubs_layout.addWidget(self.test_opensubs_button)
        
        self.opensubs_group.setLayout(opensubs_layout)
        self.layout.addWidget(self.opensubs_group)
        
        # Connect signals
        self.test_tmdb_button.clicked.connect(self.on_test_tmdb)
        self.test_anilist_button.clicked.connect(self.on_test_anilist)
        self.test_opensubs_button.clicked.connect(self.on_test_opensubs)
        
        # Add stretch to the end
        self.layout.addStretch()
    
    def on_test_tmdb(self):
        """Test TMDB API connection."""
        QMessageBox.information(self, "API 테스트", "TMDB API 연결 테스트 기능이 구현될 예정입니다.")
    
    def on_test_anilist(self):
        """Test AniList API connection."""
        QMessageBox.information(self, "API 테스트", "AniList API 연결 테스트 기능이 구현될 예정입니다.")
    
    def on_test_opensubs(self):
        """Test OpenSubtitles API connection."""
        QMessageBox.information(self, "API 테스트", "OpenSubtitles API 연결 테스트 기능이 구현될 예정입니다.")


class SettingsScreen(QWidget):
    """Settings screen for configuring application settings."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.general_tab = GeneralSettingsTab()
        self.tab_widget.addTab(self.general_tab, "일반")
        
        self.organization_tab = FileOrganizationTab()
        self.tab_widget.addTab(self.organization_tab, "파일 정리")
        
        self.api_tab = APISettingsTab()
        self.tab_widget.addTab(self.api_tab, "API 연동")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("저장")
        self.save_button.setMinimumSize(100, 30)
        button_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("초기화")
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self.on_save_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
    
    def on_save_clicked(self):
        """Handle save button click."""
        QMessageBox.information(self, "설정 저장", "설정이 저장되었습니다.")
    
    def on_reset_clicked(self):
        """Handle reset button click."""
        reply = QMessageBox.question(
            self,
            "설정 초기화",
            "모든 설정을 기본값으로 초기화하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset settings to defaults
            pass 