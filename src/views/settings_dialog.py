#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애플리케이션 설정 대화 상자 구현입니다.
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFormLayout, QDialogButtonBox,
    QMessageBox, QTabWidget, QWidget, QSpinBox, QFileDialog,
    QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSettings, QSize

from src.core.app_config import AppConfig


class SettingsDialog(QDialog):
    """
    애플리케이션 설정 대화 상자.
    
    사용자 설정을 관리하고 저장하는 기능을 제공합니다.
    """
    
    # 설정 변경 시그널
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        """설정 대화 상자 초기화."""
        super().__init__(parent)
        
        # 기본 설정
        self.setWindowTitle("설정")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setModal(True)
        
        # 앱 설정 로드
        self.config = AppConfig()
        
        # UI 초기화
        self._init_ui()
        
        # 설정 값 로드
        self._load_settings()
    
    def _init_ui(self):
        """UI 컴포넌트 초기화."""
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 일반 설정 탭
        self._create_general_tab()
        
        # AniDB API 설정 탭
        self._create_anidb_tab()
        
        # 파일 관리 설정 탭
        self._create_file_management_tab()
        
        # UI 설정 탭
        self._create_ui_tab()
        
        # 버튼 박스
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply_settings)
        layout.addWidget(button_box)
    
    def _create_general_tab(self):
        """일반 설정 탭 생성."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 기본 경로 그룹
        path_group = QGroupBox("기본 경로")
        path_layout = QFormLayout(path_group)
        
        # 기본 미디어 디렉토리
        path_layout.addRow(QLabel("기본 미디어 디렉토리:"))
        
        media_dir_layout = QHBoxLayout()
        self.media_dir_input = QLineEdit()
        media_dir_layout.addWidget(self.media_dir_input)
        
        browse_button = QPushButton("찾아보기...")
        browse_button.clicked.connect(self._browse_media_dir)
        media_dir_layout.addWidget(browse_button)
        
        path_layout.addRow("", media_dir_layout)
        
        # 출력 디렉토리
        path_layout.addRow(QLabel("정리된 파일 출력 디렉토리:"))
        
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        output_dir_layout.addWidget(self.output_dir_input)
        
        browse_output_button = QPushButton("찾아보기...")
        browse_output_button.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(browse_output_button)
        
        path_layout.addRow("", output_dir_layout)
        
        layout.addWidget(path_group)
        
        # 로그 설정 그룹
        log_group = QGroupBox("로그 설정")
        log_layout = QFormLayout(log_group)
        
        # 로그 레벨
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        log_layout.addRow("로그 레벨:", self.log_level_combo)
        
        # 로그 파일 유지 일수
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setMinimum(1)
        self.log_retention_spin.setMaximum(90)
        log_layout.addRow("로그 파일 유지 일수:", self.log_retention_spin)
        
        layout.addWidget(log_group)
        
        # 여백 추가
        layout.addStretch()
        
        # 탭 추가
        self.tab_widget.addTab(tab, "일반")
    
    def _create_anidb_tab(self):
        """AniDB API 설정 탭 생성."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # API 설정 그룹
        api_group = QGroupBox("API 설정")
        api_layout = QFormLayout(api_group)
        
        # UDP API 클라이언트 이름
        self.udp_client_name_input = QLineEdit()
        api_layout.addRow("UDP 클라이언트 이름:", self.udp_client_name_input)
        
        # UDP API 클라이언트 버전
        self.udp_client_version_spin = QSpinBox()
        self.udp_client_version_spin.setMinimum(1)
        self.udp_client_version_spin.setMaximum(9)
        api_layout.addRow("UDP 클라이언트 버전:", self.udp_client_version_spin)
        
        # HTTP API 클라이언트 이름
        self.http_client_name_input = QLineEdit()
        api_layout.addRow("HTTP 클라이언트 이름:", self.http_client_name_input)
        
        # HTTP API 클라이언트 버전
        self.http_client_version_spin = QSpinBox()
        self.http_client_version_spin.setMinimum(1)
        self.http_client_version_spin.setMaximum(9)
        api_layout.addRow("HTTP 클라이언트 버전:", self.http_client_version_spin)
        
        layout.addWidget(api_group)
        
        # 자동 로그인 설정
        self.auto_login_check = QCheckBox("시작 시 자동 로그인")
        layout.addWidget(self.auto_login_check)
        
        # 캐시 설정 그룹
        cache_group = QGroupBox("캐시 설정")
        cache_layout = QFormLayout(cache_group)
        
        # 캐시 디렉토리
        cache_dir_layout = QHBoxLayout()
        self.cache_dir_input = QLineEdit()
        cache_dir_layout.addWidget(self.cache_dir_input)
        
        browse_cache_button = QPushButton("찾아보기...")
        browse_cache_button.clicked.connect(self._browse_cache_dir)
        cache_dir_layout.addWidget(browse_cache_button)
        
        cache_layout.addRow("캐시 디렉토리:", cache_dir_layout)
        
        # 캐시 유지 일수
        self.cache_retention_spin = QSpinBox()
        self.cache_retention_spin.setMinimum(1)
        self.cache_retention_spin.setMaximum(90)
        cache_layout.addRow("캐시 유지 일수:", self.cache_retention_spin)
        
        # 캐시 최대 크기 (MB)
        self.cache_max_size_spin = QSpinBox()
        self.cache_max_size_spin.setMinimum(10)
        self.cache_max_size_spin.setMaximum(1000)
        self.cache_max_size_spin.setSuffix(" MB")
        cache_layout.addRow("캐시 최대 크기:", self.cache_max_size_spin)
        
        layout.addWidget(cache_group)
        
        # 여백 추가
        layout.addStretch()
        
        # 탭 추가
        self.tab_widget.addTab(tab, "AniDB API")
    
    def _create_file_management_tab(self):
        """파일 관리 설정 탭 생성."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 파일 명명 규칙 그룹
        naming_group = QGroupBox("파일 명명 규칙")
        naming_layout = QFormLayout(naming_group)
        
        # 파일 이름 형식
        self.filename_pattern_input = QLineEdit()
        naming_layout.addRow("파일 이름 형식:", self.filename_pattern_input)
        
        # 패턴 설명
        pattern_label = QLabel(
            "사용 가능한 변수:\n"
            "{series} - 시리즈 이름\n"
            "{episode} - 에피소드 번호\n"
            "{title} - 에피소드 제목\n"
            "{year} - 방영 연도\n"
            "{resolution} - 해상도\n"
            "{ext} - 파일 확장자"
        )
        pattern_label.setStyleSheet("color: gray;")
        naming_layout.addRow("", pattern_label)
        
        layout.addWidget(naming_group)
        
        # 디렉토리 구조 그룹
        dir_group = QGroupBox("디렉토리 구조")
        dir_layout = QFormLayout(dir_group)
        
        # 디렉토리 구조 형식
        self.dir_pattern_input = QLineEdit()
        dir_layout.addRow("디렉토리 구조 형식:", self.dir_pattern_input)
        
        # 패턴 설명
        dir_pattern_label = QLabel(
            "사용 가능한 변수:\n"
            "{series} - 시리즈 이름\n"
            "{year} - 방영 연도\n"
            "{type} - 애니메이션 타입 (TV, 영화 등)"
        )
        dir_pattern_label.setStyleSheet("color: gray;")
        dir_layout.addRow("", dir_pattern_label)
        
        layout.addWidget(dir_group)
        
        # 파일 처리 옵션 그룹
        options_group = QGroupBox("파일 처리 옵션")
        options_layout = QVBoxLayout(options_group)
        
        # 옵션 체크박스
        self.move_files_check = QCheckBox("원본 파일 이동 (복사 대신)")
        self.create_series_dirs_check = QCheckBox("시리즈별 디렉토리 생성")
        self.overwrite_check = QCheckBox("기존 파일 덮어쓰기")
        self.ignore_non_media_check = QCheckBox("비미디어 파일 무시")
        
        options_layout.addWidget(self.move_files_check)
        options_layout.addWidget(self.create_series_dirs_check)
        options_layout.addWidget(self.overwrite_check)
        options_layout.addWidget(self.ignore_non_media_check)
        
        layout.addWidget(options_group)
        
        # 여백 추가
        layout.addStretch()
        
        # 탭 추가
        self.tab_widget.addTab(tab, "파일 관리")
    
    def _create_ui_tab(self):
        """UI 설정 탭 생성."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 테마 그룹
        theme_group = QGroupBox("테마 설정")
        theme_layout = QVBoxLayout(theme_group)
        
        # 테마 선택
        theme_form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["시스템 기본", "라이트 모드", "다크 모드"])
        theme_form.addRow("UI 테마:", self.theme_combo)
        theme_layout.addLayout(theme_form)
        
        layout.addWidget(theme_group)
        
        # 폰트 크기 그룹
        font_group = QGroupBox("폰트 설정")
        font_layout = QFormLayout(font_group)
        
        # 기본 폰트 크기
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(16)
        font_layout.addRow("기본 폰트 크기:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        # UI 옵션 그룹
        ui_options_group = QGroupBox("UI 옵션")
        ui_options_layout = QVBoxLayout(ui_options_group)
        
        # 옵션 체크박스
        self.restore_window_check = QCheckBox("이전 창 크기 및 위치 복원")
        self.show_status_bar_check = QCheckBox("상태 표시줄 표시")
        self.confirm_exit_check = QCheckBox("종료 시 확인")
        self.show_tooltips_check = QCheckBox("도구 설명 표시")
        
        ui_options_layout.addWidget(self.restore_window_check)
        ui_options_layout.addWidget(self.show_status_bar_check)
        ui_options_layout.addWidget(self.confirm_exit_check)
        ui_options_layout.addWidget(self.show_tooltips_check)
        
        layout.addWidget(ui_options_group)
        
        # 여백 추가
        layout.addStretch()
        
        # 탭 추가
        self.tab_widget.addTab(tab, "UI")
    
    def _browse_media_dir(self):
        """미디어 디렉토리 선택 대화 상자 표시."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "미디어 디렉토리 선택", self.media_dir_input.text()
        )
        if dir_path:
            self.media_dir_input.setText(dir_path)
    
    def _browse_output_dir(self):
        """출력 디렉토리 선택 대화 상자 표시."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "출력 디렉토리 선택", self.output_dir_input.text()
        )
        if dir_path:
            self.output_dir_input.setText(dir_path)
    
    def _browse_cache_dir(self):
        """캐시 디렉토리 선택 대화 상자 표시."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "캐시 디렉토리 선택", self.cache_dir_input.text()
        )
        if dir_path:
            self.cache_dir_input.setText(dir_path)
    
    def _load_settings(self):
        """저장된 설정 로드."""
        # 일반 설정
        self.media_dir_input.setText(self.config.get('general', 'media_directory', str(Path.home() / 'Videos')))
        self.output_dir_input.setText(self.config.get('general', 'output_directory', str(Path.home() / 'Videos' / 'Sorted')))
        self.log_level_combo.setCurrentText(self.config.get('general', 'log_level', 'INFO'))
        self.log_retention_spin.setValue(self.config.get('general', 'log_retention_days', 30))
        
        # AniDB API 설정
        self.udp_client_name_input.setText(self.config.get('anidb', 'udp_client_name', 'animefilesorterudp'))
        self.udp_client_version_spin.setValue(self.config.get('anidb', 'udp_client_version', 1))
        self.http_client_name_input.setText(self.config.get('anidb', 'http_client_name', 'animefilesorterhttp'))
        self.http_client_version_spin.setValue(self.config.get('anidb', 'http_client_version', 1))
        self.auto_login_check.setChecked(self.config.get('anidb', 'auto_login', False))
        self.cache_dir_input.setText(self.config.get('anidb', 'cache_directory', str(Path.home() / '.animefilesorter' / 'cache')))
        self.cache_retention_spin.setValue(self.config.get('anidb', 'cache_retention_days', 30))
        self.cache_max_size_spin.setValue(self.config.get('anidb', 'cache_max_size_mb', 100))
        
        # 파일 관리 설정
        self.filename_pattern_input.setText(self.config.get('file_management', 'filename_pattern', '{series} - {episode} - {title}.{ext}'))
        self.dir_pattern_input.setText(self.config.get('file_management', 'directory_pattern', '{series} ({year})'))
        self.move_files_check.setChecked(self.config.get('file_management', 'move_files', False))
        self.create_series_dirs_check.setChecked(self.config.get('file_management', 'create_series_dirs', True))
        self.overwrite_check.setChecked(self.config.get('file_management', 'overwrite', False))
        self.ignore_non_media_check.setChecked(self.config.get('file_management', 'ignore_non_media', True))
        
        # UI 설정
        self.theme_combo.setCurrentText(self.config.get('ui', 'theme', '시스템 기본'))
        self.font_size_spin.setValue(self.config.get('ui', 'font_size', 10))
        self.restore_window_check.setChecked(self.config.get('ui', 'restore_window', True))
        self.show_status_bar_check.setChecked(self.config.get('ui', 'show_status_bar', True))
        self.confirm_exit_check.setChecked(self.config.get('ui', 'confirm_exit', True))
        self.show_tooltips_check.setChecked(self.config.get('ui', 'show_tooltips', True))
    
    def _apply_settings(self):
        """설정 적용."""
        # 일반 설정
        self.config.set('general', 'media_directory', self.media_dir_input.text())
        self.config.set('general', 'output_directory', self.output_dir_input.text())
        self.config.set('general', 'log_level', self.log_level_combo.currentText())
        self.config.set('general', 'log_retention_days', self.log_retention_spin.value())
        
        # AniDB API 설정
        self.config.set('anidb', 'udp_client_name', self.udp_client_name_input.text())
        self.config.set('anidb', 'udp_client_version', self.udp_client_version_spin.value())
        self.config.set('anidb', 'http_client_name', self.http_client_name_input.text())
        self.config.set('anidb', 'http_client_version', self.http_client_version_spin.value())
        self.config.set('anidb', 'auto_login', self.auto_login_check.isChecked())
        self.config.set('anidb', 'cache_directory', self.cache_dir_input.text())
        self.config.set('anidb', 'cache_retention_days', self.cache_retention_spin.value())
        self.config.set('anidb', 'cache_max_size_mb', self.cache_max_size_spin.value())
        
        # 파일 관리 설정
        self.config.set('file_management', 'filename_pattern', self.filename_pattern_input.text())
        self.config.set('file_management', 'directory_pattern', self.dir_pattern_input.text())
        self.config.set('file_management', 'move_files', self.move_files_check.isChecked())
        self.config.set('file_management', 'create_series_dirs', self.create_series_dirs_check.isChecked())
        self.config.set('file_management', 'overwrite', self.overwrite_check.isChecked())
        self.config.set('file_management', 'ignore_non_media', self.ignore_non_media_check.isChecked())
        
        # UI 설정
        self.config.set('ui', 'theme', self.theme_combo.currentText())
        self.config.set('ui', 'font_size', self.font_size_spin.value())
        self.config.set('ui', 'restore_window', self.restore_window_check.isChecked())
        self.config.set('ui', 'show_status_bar', self.show_status_bar_check.isChecked())
        self.config.set('ui', 'confirm_exit', self.confirm_exit_check.isChecked())
        self.config.set('ui', 'show_tooltips', self.show_tooltips_check.isChecked())
        
        # 설정 저장
        self.config.save()
        
        # 변경 시그널 발생
        self.settings_changed.emit()
    
    def _save_settings(self):
        """설정 저장 및 대화 상자 닫기."""
        self._apply_settings()
        self.accept()
    
    @staticmethod
    def show_settings(parent=None):
        """
        설정 대화 상자 표시.
        
        Args:
            parent: 부모 위젯
            
        Returns:
            변경 사항 저장 여부 (QDialog.Accepted 또는 QDialog.Rejected)
        """
        dialog = SettingsDialog(parent)
        return dialog.exec() 