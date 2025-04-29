#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard screen for AnimeFileSorter.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QFrame,
    QScrollArea
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


class RecentActivityItem(QFrame):
    """A widget to display a recent activity item."""
    
    def __init__(self, title, datetime, description="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        
        # Date and time
        datetime_label = QLabel(datetime)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(datetime_label)
        if description:
            layout.addWidget(desc_label)


class DashboardScreen(QScrollArea):
    """Dashboard screen displaying overview of the application."""
    
    def __init__(self):
        super().__init__()
        
        # Make the scroll area fill the container
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        self.content = QWidget()
        self.setWidget(self.content)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout()
        self.content.setLayout(layout)
        
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
        
        self.scan_button = QPushButton("폴더 스캔")
        self.scan_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(self.scan_button)
        
        self.organize_button = QPushButton("파일 정리")
        self.organize_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(self.organize_button)
        
        self.settings_button = QPushButton("설정")
        self.settings_button.setMinimumSize(150, 40)
        quick_actions_layout.addWidget(self.settings_button)
        
        quick_actions_layout.addStretch()
        
        # Stats section
        stats_label = QLabel("통계")
        font = stats_label.font()
        font.setPointSize(14)
        font.setBold(True)
        stats_label.setFont(font)
        
        stats_grid = QGridLayout()
        
        # Stats cards - these will be updated from the main window
        self.total_files = StatCard("총 파일", "0", "관리 중인 파일")
        self.organized_files = StatCard("정리된 파일", "0", "분류된 파일")
        self.duplicate_files = StatCard("중복 파일", "0", "발견된 중복")
        
        stats_grid.addWidget(self.total_files, 0, 0)
        stats_grid.addWidget(self.organized_files, 0, 1)
        stats_grid.addWidget(self.duplicate_files, 0, 2)
        
        # Recent activity section
        recent_label = QLabel("최근 활동")
        font = recent_label.font()
        font.setPointSize(14)
        font.setBold(True)
        recent_label.setFont(font)
        
        # Activity list container
        self.activity_layout = QVBoxLayout()
        
        # Add sample activity items (these will be replaced with real data)
        self.activity_layout.addWidget(
            RecentActivityItem(
                "애플리케이션 시작", 
                "방금", 
                "AnimeFileSorter가 실행되었습니다."
            )
        )
        
        # Add all sections to main layout
        layout.addLayout(welcome_layout)
        layout.addSpacing(20)
        layout.addLayout(quick_actions_layout)
        layout.addSpacing(30)
        layout.addWidget(stats_label)
        layout.addLayout(stats_grid)
        layout.addSpacing(30)
        layout.addWidget(recent_label)
        layout.addLayout(self.activity_layout)
        layout.addStretch()
    
    def add_activity(self, title, datetime, description=""):
        """
        Add a new activity to the recent activity list.
        
        Args:
            title: Title of the activity
            datetime: Date and time of the activity
            description: Optional description
        """
        # Create a new activity item
        activity_item = RecentActivityItem(title, datetime, description)
        
        # Add it to the beginning of the list
        self.activity_layout.insertWidget(0, activity_item)
        
        # Limit the number of items (keep only the 5 most recent)
        if self.activity_layout.count() > 5:
            # Get the last item
            item = self.activity_layout.itemAt(self.activity_layout.count() - 1)
            if item:
                # Remove and delete the widget
                widget = item.widget()
                if widget:
                    self.activity_layout.removeWidget(widget)
                    widget.deleteLater()
    
    def clear_activities(self):
        """Clear all activity items."""
        # Remove all widgets from the layout
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def update_statistics(self, total_files=None, organized_files=None, duplicate_files=None):
        """
        Update the statistics cards.
        
        Args:
            total_files: Number of total files
            organized_files: Number of organized files
            duplicate_files: Number of duplicate files
        """
        if total_files is not None:
            self.total_files.value_label.setText(str(total_files))
            
        if organized_files is not None:
            self.organized_files.value_label.setText(str(organized_files))
            
        if duplicate_files is not None:
            self.duplicate_files.value_label.setText(str(duplicate_files)) 