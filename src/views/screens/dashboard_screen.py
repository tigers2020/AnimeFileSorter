#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard screen for AnimeFileSorter.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QSpacerItem,
    QSizePolicy
)


class StatCard(QGroupBox):
    """A card widget to display statistics."""
    
    def __init__(self, title, value, desc=""):
        super().__init__(title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Value label (large font)
        self.value_label = QLabel(value)
        font = self.value_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # Description label
        self.desc_label = QLabel(desc)
        self.desc_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.desc_label)


class DashboardScreen(QWidget):
    """Dashboard screen displaying overview of the application."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Welcome section
        welcome_layout = QHBoxLayout()
        
        welcome_label = QLabel("환영합니다, AnimeFileSorter에!")
        font = welcome_label.font()
        font.setPointSize(18)
        font.setBold(True)
        welcome_label.setFont(font)
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch()
        
        # Quick actions
        quick_actions_layout = QHBoxLayout()
        
        scan_button = QPushButton("폴더 스캔")
        scan_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(scan_button)
        
        organize_button = QPushButton("파일 정리")
        organize_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(organize_button)
        
        settings_button = QPushButton("설정")
        settings_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(settings_button)
        
        quick_actions_layout.addStretch()
        
        # Stats section
        stats_label = QLabel("통계")
        font = stats_label.font()
        font.setPointSize(14)
        font.setBold(True)
        stats_label.setFont(font)
        
        stats_grid = QGridLayout()
        
        # Sample stats cards - these would be updated with real data
        total_files = StatCard("총 파일", "0", "관리 중인 파일")
        organized_files = StatCard("정리된 파일", "0", "분류된 파일")
        duplicate_files = StatCard("중복 파일", "0", "발견된 중복")
        
        stats_grid.addWidget(total_files, 0, 0)
        stats_grid.addWidget(organized_files, 0, 1)
        stats_grid.addWidget(duplicate_files, 0, 2)
        
        # Recent activity section
        recent_label = QLabel("최근 활동")
        font = recent_label.font()
        font.setPointSize(14)
        font.setBold(True)
        recent_label.setFont(font)
        
        recent_activity = QLabel("최근 활동이 없습니다.")
        recent_activity.setAlignment(Qt.AlignCenter)
        
        # Add all sections to main layout
        layout.addLayout(welcome_layout)
        layout.addSpacing(20)
        layout.addLayout(quick_actions_layout)
        layout.addSpacing(30)
        layout.addWidget(stats_label)
        layout.addLayout(stats_grid)
        layout.addSpacing(30)
        layout.addWidget(recent_label)
        layout.addWidget(recent_activity)
        layout.addStretch()
        
        # Connect signals
        scan_button.clicked.connect(self.on_scan_clicked)
        organize_button.clicked.connect(self.on_organize_clicked)
        settings_button.clicked.connect(self.on_settings_clicked)
    
    def on_scan_clicked(self):
        """Handle scan button click."""
        # This would be connected to the controller/parent window
        print("Scan button clicked")
    
    def on_organize_clicked(self):
        """Handle organize button click."""
        print("Organize button clicked")
    
    def on_settings_clicked(self):
        """Handle settings button click."""
        print("Settings button clicked") 