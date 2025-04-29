#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main application window for AnimeFileSorter.
"""

import os
from pathlib import Path

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QTabWidget,
    QToolBar,
    QStatusBar,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QStyle
)

from src.views.screens.dashboard_screen import DashboardScreen
from src.views.screens.file_browser_screen import FileBrowserScreen
from src.views.screens.settings_screen import SettingsScreen
from src.controllers.file_controller import FileController
from src.utils.logger import log_info, log_error, log_debug, log_warning


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        
        # Initialize controllers
        self.file_controller = FileController()
        
        # Connect controller signals to status updates
        self.file_controller.scan_started.connect(self.on_scan_started)
        self.file_controller.scan_completed.connect(self.on_scan_completed)
        self.file_controller.scan_error.connect(self.on_scan_error)
        self.file_controller.scan_progress.connect(self.on_scan_progress)
        self.file_controller.organize_completed.connect(self.on_organize_completed)
        self.file_controller.organize_error.connect(self.on_organize_error)
        
        # Setup UI
        self.setWindowTitle("AnimeFileSorter")
        self.setMinimumSize(1000, 700)
        
        # Setup central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.dashboard_screen = DashboardScreen()
        self.tab_widget.addTab(self.dashboard_screen, "대시보드")
        
        self.file_browser_screen = FileBrowserScreen(self.file_controller)
        self.tab_widget.addTab(self.file_browser_screen, "파일 관리")
        
        self.settings_screen = SettingsScreen()
        self.tab_widget.addTab(self.settings_screen, "설정")
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
        
        # Progress info in status bar
        self.progress_label = QLabel()
        self.status_bar.addPermanentWidget(self.progress_label)
        self.progress_label.setVisible(False)
        
        # Connect signals and slots
        self.connect_signals()
        
        # Log application start
        log_info("AnimeFileSorter 애플리케이션이 시작되었습니다.")
    
    def setup_toolbar(self):
        """Setup the main toolbar."""
        self.toolbar = QToolBar("메인 툴바")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Add actions
        style = self.style()
        
        # Scan action with icon
        self.scan_action = QAction("스캔", self)
        self.scan_action.setIcon(style.standardIcon(QStyle.SP_FileDialogContentsView))
        self.scan_action.setStatusTip("디렉토리 스캔")
        self.toolbar.addAction(self.scan_action)
        
        # Organize action with icon
        self.organize_action = QAction("정리", self)
        self.organize_action.setIcon(style.standardIcon(QStyle.SP_DirIcon))
        self.organize_action.setStatusTip("파일 정리")
        self.toolbar.addAction(self.organize_action)
        
        self.toolbar.addSeparator()
        
        # Settings action with icon
        self.settings_action = QAction("설정", self)
        self.settings_action.setIcon(style.standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_action.setStatusTip("설정 열기")
        self.toolbar.addAction(self.settings_action)
        
        # About action with icon
        self.about_action = QAction("정보", self)
        self.about_action.setIcon(style.standardIcon(QStyle.SP_MessageBoxInformation))
        self.about_action.setStatusTip("프로그램 정보")
        self.toolbar.addAction(self.about_action)
    
    def connect_signals(self):
        """Connect signals and slots."""
        # Toolbar actions
        self.scan_action.triggered.connect(self.on_scan_action)
        self.organize_action.triggered.connect(self.on_organize_action)
        self.settings_action.triggered.connect(self.on_settings_action)
        self.about_action.triggered.connect(self.on_about_action)
        
        # Dashboard buttons
        self.dashboard_screen.scan_button.clicked.connect(self.on_scan_action)
        self.dashboard_screen.organize_button.clicked.connect(self.on_organize_action)
        self.dashboard_screen.settings_button.clicked.connect(self.on_settings_action)
    
    def on_scan_action(self):
        """Handle scan action."""
        # Switch to file browser tab
        self.tab_widget.setCurrentWidget(self.file_browser_screen)
        
        # Open directory dialog
        directory = QFileDialog.getExistingDirectory(
            self, "스캔할 디렉토리 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.status_bar.showMessage(f"디렉토리 스캔 중: {directory}")
            
            # Use the FileBrowserScreen to handle the directory
            self.file_browser_screen.folder_path.setText(directory)
            self.file_browser_screen.current_directory = directory
            self.file_browser_screen.load_directory(directory)
    
    def on_organize_action(self):
        """Handle organize action."""
        # Switch to file browser tab
        self.tab_widget.setCurrentWidget(self.file_browser_screen)
        
        # If we have files loaded, trigger the organize function
        if self.file_browser_screen.current_directory:
            self.file_browser_screen.on_organize_clicked()
        else:
            QMessageBox.information(
                self, 
                "정리", 
                "파일을 정리하려면 먼저 디렉토리를 스캔하세요."
            )
    
    def on_settings_action(self):
        """Handle settings action."""
        self.tab_widget.setCurrentWidget(self.settings_screen)
    
    def on_about_action(self):
        """Handle about action."""
        QMessageBox.about(
            self,
            "AnimeFileSorter 정보",
            "AnimeFileSorter v0.1.0\n\n"
            "모던한 아니메 파일 관리 도구\n"
            "PySide6로 개발됨"
        )
    
    @Slot()
    def on_scan_started(self):
        """Handle scan started signal."""
        self.status_bar.showMessage("디렉토리 스캔 중...")
        self.progress_label.setText("스캔 시작됨")
        self.progress_label.setVisible(True)
        
        # Update dashboard stats when available
        self.update_dashboard_stats(0, "스캔 중...")
    
    @Slot(list)
    def on_scan_completed(self, media_items):
        """Handle scan completed signal."""
        self.status_bar.showMessage(f"스캔 완료: {len(media_items)}개 파일 발견")
        self.progress_label.setVisible(False)
        
        # Update dashboard stats
        self.update_dashboard_stats(len(media_items), "스캔 완료")
    
    @Slot(str)
    def on_scan_error(self, error_message):
        """Handle scan error signal."""
        self.status_bar.showMessage(f"스캔 오류: {error_message}")
        self.progress_label.setVisible(False)
        
        # Update dashboard stats with error
        self.update_dashboard_stats(0, "스캔 오류")
    
    @Slot(int, int, str)
    def on_scan_progress(self, current, total, filename):
        """Handle scan progress signal."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_label.setText(f"스캔 중: {percentage}% ({current}/{total})")
            self.status_bar.showMessage(f"스캔 중: {os.path.basename(filename)}")
    
    @Slot(list)
    def on_organize_completed(self, operations):
        """Handle organize completed signal."""
        self.status_bar.showMessage(f"파일 정리 완료: {len(operations)}개 파일")
        
        # Update dashboard stats
        self.update_dashboard_stats(len(self.file_controller.scanned_files), "정리 완료")
    
    @Slot(str)
    def on_organize_error(self, error_message):
        """Handle organize error signal."""
        self.status_bar.showMessage(f"정리 오류: {error_message}")
    
    def update_dashboard_stats(self, file_count, status):
        """Update dashboard statistics."""
        # Check if the dashboard screen has the stats cards
        if hasattr(self.dashboard_screen, "total_files"):
            self.dashboard_screen.total_files.value_label.setText(str(file_count))
            
            # If we have more detailed information later, we can update other stats
            # For now, just update the status if organized files is available
            if hasattr(self.dashboard_screen, "organized_files"):
                self.dashboard_screen.organized_files.desc_label.setText(status) 