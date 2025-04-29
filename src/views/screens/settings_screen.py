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

from src.services.setting_service import SettingService
from src.utils.logger import log_info, log_error, log_debug


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
    
    def __init__(self, setting_service=None):
        super().__init__()
        self.setting_service = setting_service or SettingService()
        self.has_unsaved_changes = False
        self.init_ui()
        self.load_ui_from_settings()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = GeneralSettingsTab()
        self.tabs.addTab(self.general_tab, "일반")
        
        # File organization tab
        self.organization_tab = FileOrganizationTab()
        self.tabs.addTab(self.organization_tab, "파일 정리")
        
        # API settings tab
        self.api_tab = APISettingsTab()
        self.tabs.addTab(self.api_tab, "API 연동")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_button = QPushButton("초기화")
        self.reset_button.clicked.connect(self.on_reset_clicked)
        button_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("저장")
        self.save_button.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.connect_signals()
    
    def connect_signals(self):
        """Connect widget signals to track changes."""
        # General tab signals
        self.general_tab.input_dir.textChanged.connect(self.mark_changes)
        self.general_tab.output_dir.textChanged.connect(self.mark_changes)
        self.general_tab.startup_check.stateChanged.connect(self.mark_changes)
        self.general_tab.auto_scan_check.stateChanged.connect(self.mark_changes)
        self.general_tab.confirm_check.stateChanged.connect(self.mark_changes)
        
        # Organization tab signals
        self.organization_tab.create_subfolder_check.stateChanged.connect(self.mark_changes)
        self.organization_tab.season_folder_check.stateChanged.connect(self.mark_changes)
        self.organization_tab.move_subtitles_check.stateChanged.connect(self.mark_changes)
        self.organization_tab.series_pattern.textChanged.connect(self.mark_changes)
        self.organization_tab.season_pattern.textChanged.connect(self.mark_changes)
        self.organization_tab.episode_pattern.textChanged.connect(self.mark_changes)
        self.organization_tab.movie_pattern.textChanged.connect(self.mark_changes)
        
        # API tab signals
        self.api_tab.tmdb_enable.stateChanged.connect(self.mark_changes)
        self.api_tab.tmdb_key.textChanged.connect(self.mark_changes)
        self.api_tab.anilist_enable.stateChanged.connect(self.mark_changes)
        self.api_tab.anilist_client_id.textChanged.connect(self.mark_changes)
    
    def mark_changes(self):
        """Mark that there are unsaved changes."""
        self.has_unsaved_changes = True
        
        # 자동 저장 설정이 활성화되어 있으면 즉시 저장
        if self.setting_service.get_setting("auto_save_settings", True):
            self.on_save_clicked()
    
    def load_ui_from_settings(self):
        """Load UI elements from current settings."""
        log_debug("UI 요소를 설정에서 로드합니다")
        
        # UI와 설정 키 매핑에 따라 값 로드
        
        # General Tab
        self.general_tab.input_dir.setText(self.setting_service.get_setting("input_directory", ""))
        self.general_tab.output_dir.setText(self.setting_service.get_setting("output_directory", ""))
        self.general_tab.startup_check.setChecked(self.setting_service.get_setting("check_updates", True))
        self.general_tab.auto_scan_check.setChecked(self.setting_service.get_setting("scan_recursive", True))
        self.general_tab.confirm_check.setChecked(self.setting_service.get_setting("confirm_before_organize", True))
        
        # Organization Tab
        self.organization_tab.create_subfolder_check.setChecked(self.setting_service.get_setting("create_series_folders", True))
        self.organization_tab.season_folder_check.setChecked(self.setting_service.get_setting("create_season_folders", True))
        self.organization_tab.move_subtitles_check.setChecked(self.setting_service.get_setting("move_subtitles", True))
        self.organization_tab.series_pattern.setText(self.setting_service.get_setting("series_folder_pattern", "{series_name}"))
        self.organization_tab.season_pattern.setText(self.setting_service.get_setting("season_folder_pattern", "Season {season_number}"))
        
        # DEFAULT_SETTINGS에 없는 값들은 직접 생성해줘야 할 수 있음
        self.organization_tab.episode_pattern.setText(self.setting_service.get_setting("episode_pattern", 
                                                     "{series_name} - S{season_number}E{episode_number}"))
        self.organization_tab.movie_pattern.setText(self.setting_service.get_setting("movie_pattern", 
                                                   "{title} ({year})"))
        
        # API Tab
        self.api_tab.tmdb_enable.setChecked(self.setting_service.get_setting("use_external_api", False))
        self.api_tab.tmdb_key.setText(self.setting_service.get_setting("tmdb_api_key", ""))
        
        # 애니리스트 설정은 DEFAULT_SETTINGS에 없을 수 있으므로 안전하게 처리
        self.api_tab.anilist_client_id.setText(self.setting_service.get_setting("anilist_api_key", ""))
        
        self.has_unsaved_changes = False
        log_info("설정에서 UI 로드 완료")
    
    def on_save_clicked(self):
        """Handle save button click."""
        log_debug("설정 저장을 시도합니다")
        
        # 변경된 설정을 딕셔너리로 모음
        updates = {
            # General Tab
            "input_directory": self.general_tab.input_dir.text(),
            "output_directory": self.general_tab.output_dir.text(),
            "check_updates": self.general_tab.startup_check.isChecked(),
            "scan_recursive": self.general_tab.auto_scan_check.isChecked(),
            "confirm_before_organize": self.general_tab.confirm_check.isChecked(),
            
            # Organization Tab
            "create_series_folders": self.organization_tab.create_subfolder_check.isChecked(),
            "create_season_folders": self.organization_tab.season_folder_check.isChecked(),
            "move_subtitles": self.organization_tab.move_subtitles_check.isChecked(),
            "series_folder_pattern": self.organization_tab.series_pattern.text(),
            "season_folder_pattern": self.organization_tab.season_pattern.text(),
            "episode_pattern": self.organization_tab.episode_pattern.text(),
            "movie_pattern": self.organization_tab.movie_pattern.text(),
            
            # API Tab
            "use_external_api": self.api_tab.tmdb_enable.isChecked(),
            "tmdb_api_key": self.api_tab.tmdb_key.text(),
            "anilist_api_key": self.api_tab.anilist_client_id.text()
        }
        
        # 디렉토리 경로 검증
        errors = self.validate_settings(updates)
        if errors:
            error_message = "\n".join(errors)
            QMessageBox.warning(self, "설정 오류", f"다음 오류를 수정해주세요:\n{error_message}")
            return
        
        # 설정 저장
        log_info(f"설정 업데이트 시도: {len(updates)}개 항목")
        success = self.setting_service.update_settings(updates)
        
        if success:
            self.has_unsaved_changes = False
            log_info("설정 저장 성공")
        else:
            log_error("설정 저장 실패")
            QMessageBox.warning(self, "저장 실패", "설정 저장에 실패했습니다.")
    
    def validate_settings(self, updates: dict) -> list:
        """
        설정 값을 검증합니다.
        
        Args:
            updates: 검증할 설정 딕셔너리
            
        Returns:
            오류 메시지 리스트 (문제가 없으면 빈 리스트)
        """
        errors = []
        
        # 예시: 입력 디렉토리가 설정된 경우 존재 여부 확인
        input_dir = updates.get("input_directory")
        if input_dir and not Path(input_dir).exists():
            errors.append(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
        
        # 패턴이 빈 문자열인지 확인
        if not updates.get("series_folder_pattern"):
            errors.append("시리즈 폴더 패턴을 지정해야 합니다.")
        
        if not updates.get("season_folder_pattern"):
            errors.append("시즌 폴더 패턴을 지정해야 합니다.")
        
        # 다른 검증 로직 추가...
        
        return errors
    
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
            log_info("설정 초기화 시도")
            if self.setting_service.reset_to_defaults():
                self.load_ui_from_settings()
                log_info("설정이 기본값으로 초기화되었습니다")
                QMessageBox.information(self, "초기화", "기본값으로 초기화되었습니다.")
            else:
                log_error("설정 초기화 중 오류가 발생했습니다")
                QMessageBox.warning(self, "실패", "초기화 중 오류가 발생했습니다.") 