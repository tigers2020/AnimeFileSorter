#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main application window for AnimeFileSorter.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
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
    QMessageBox
)

from src.views.screens.dashboard_screen import DashboardScreen
from src.views.screens.file_browser_screen import FileBrowserScreen
from src.views.screens.settings_screen import SettingsScreen
from src.controllers.file_controller import FileController


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        
        # Initialize controllers
        self.file_controller = FileController()
        
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
        
        self.file_browser_screen = FileBrowserScreen()
        self.tab_widget.addTab(self.file_browser_screen, "파일 관리")
        
        self.settings_screen = SettingsScreen()
        self.tab_widget.addTab(self.settings_screen, "설정")
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
        
        # Connect signals and slots
        self.connect_signals()
    
    def setup_toolbar(self):
        """Setup the main toolbar."""
        self.toolbar = QToolBar("메인 툴바")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Add actions
        self.scan_action = QAction("스캔", self)
        self.scan_action.setStatusTip("디렉토리 스캔")
        self.toolbar.addAction(self.scan_action)
        
        self.organize_action = QAction("정리", self)
        self.organize_action.setStatusTip("파일 정리")
        self.toolbar.addAction(self.organize_action)
        
        self.toolbar.addSeparator()
        
        self.settings_action = QAction("설정", self)
        self.settings_action.setStatusTip("설정 열기")
        self.toolbar.addAction(self.settings_action)
        
        self.about_action = QAction("정보", self)
        self.about_action.setStatusTip("프로그램 정보")
        self.toolbar.addAction(self.about_action)
    
    def connect_signals(self):
        """Connect signals and slots."""
        self.scan_action.triggered.connect(self.on_scan_action)
        self.organize_action.triggered.connect(self.on_organize_action)
        self.settings_action.triggered.connect(self.on_settings_action)
        self.about_action.triggered.connect(self.on_about_action)
    
    def on_scan_action(self):
        """Handle scan action."""
        directory = QFileDialog.getExistingDirectory(
            self, "스캔할 디렉토리 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.status_bar.showMessage(f"디렉토리 스캔 중: {directory}")
            # Here we would connect to the controller to perform the scan
            # self.file_controller.scan_directory(directory)
    
    def on_organize_action(self):
        """Handle organize action."""
        QMessageBox.information(self, "정리", "파일 정리 기능이 구현 예정입니다.")
    
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