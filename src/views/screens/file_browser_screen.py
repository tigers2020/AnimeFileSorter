#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File browser screen for AnimeFileSorter.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTreeView,
    QFileDialog,
    QSplitter,
    QComboBox,
    QToolBar,
    QStyle,
    QFrame
)


class FileTreeView(QTreeView):
    """A customized tree view for displaying files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setSelectionMode(QTreeView.SingleSelection)
        
        # Setup model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["이름", "크기", "타입", "수정일"])
        self.setModel(self.model)
        
        # Adjust column widths
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)


class FileInfoPanel(QFrame):
    """Panel showing details of the selected file."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # File name
        self.name_label = QLabel("파일 이름")
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)
        
        self.name_value = QLabel("")
        
        # File path
        self.path_label = QLabel("경로")
        self.path_label.setFont(font)
        
        self.path_value = QLabel("")
        self.path_value.setWordWrap(True)
        
        # File size
        self.size_label = QLabel("크기")
        self.size_label.setFont(font)
        
        self.size_value = QLabel("")
        
        # File type
        self.type_label = QLabel("타입")
        self.type_label.setFont(font)
        
        self.type_value = QLabel("")
        
        # Modified date
        self.modified_label = QLabel("수정일")
        self.modified_label.setFont(font)
        
        self.modified_value = QLabel("")
        
        # Add labels to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_value)
        layout.addSpacing(10)
        
        layout.addWidget(self.path_label)
        layout.addWidget(self.path_value)
        layout.addSpacing(10)
        
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_value)
        layout.addSpacing(10)
        
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_value)
        layout.addSpacing(10)
        
        layout.addWidget(self.modified_label)
        layout.addWidget(self.modified_value)
        
        layout.addStretch()


class FileBrowserScreen(QWidget):
    """File browser screen for exploring and managing files."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Folder selection
        folder_label = QLabel("폴더:")
        toolbar.addWidget(folder_label)
        
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.folder_path.setMinimumWidth(400)
        toolbar.addWidget(self.folder_path)
        
        browse_button = QPushButton("찾아보기")
        toolbar.addWidget(browse_button)
        
        toolbar.addSeparator()
        
        # Filter
        filter_label = QLabel("필터:")
        toolbar.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["모든 파일", "비디오 파일", "이미지 파일", "자막 파일"])
        toolbar.addWidget(self.filter_combo)
        
        toolbar.addSeparator()
        
        # Refresh button
        refresh_button = QPushButton("새로고침")
        toolbar.addWidget(refresh_button)
        
        # Add toolbar to layout
        layout.addWidget(toolbar)
        
        # Splitter for file tree and info panel
        splitter = QSplitter(Qt.Horizontal)
        
        # File tree view
        self.file_tree = FileTreeView()
        splitter.addWidget(self.file_tree)
        
        # File info panel
        self.info_panel = FileInfoPanel()
        splitter.addWidget(self.info_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([700, 300])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Button row
        button_layout = QHBoxLayout()
        
        organize_button = QPushButton("파일 정리")
        organize_button.setMinimumSize(120, 30)
        button_layout.addWidget(organize_button)
        
        preview_button = QPushButton("정리 미리보기")
        preview_button.setMinimumSize(120, 30)
        button_layout.addWidget(preview_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect signals
        browse_button.clicked.connect(self.on_browse_clicked)
        refresh_button.clicked.connect(self.on_refresh_clicked)
        organize_button.clicked.connect(self.on_organize_clicked)
        preview_button.clicked.connect(self.on_preview_clicked)
        self.file_tree.selectionModel().selectionChanged.connect(self.on_file_selected)
    
    def on_browse_clicked(self):
        """Handle browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "폴더 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.folder_path.setText(directory)
            self.load_directory(directory)
    
    def on_refresh_clicked(self):
        """Handle refresh button click."""
        if self.folder_path.text():
            self.load_directory(self.folder_path.text())
    
    def on_organize_clicked(self):
        """Handle organize button click."""
        print("Organize button clicked")
    
    def on_preview_clicked(self):
        """Handle preview button click."""
        print("Preview button clicked")
    
    def on_file_selected(self, selected, deselected):
        """Handle file selection change."""
        # This would update the info panel with the selected file's details
        pass
    
    def load_directory(self, directory_path):
        """Load the directory structure into the tree view."""
        # Clear the model
        self.file_tree.model.clear()
        self.file_tree.model.setHorizontalHeaderLabels(["이름", "크기", "타입", "수정일"])
        
        # This is just a placeholder - we'd actually scan the directory
        # and populate the tree with real data
        root_item = QStandardItem("루트 폴더")
        self.file_tree.model.appendRow(root_item)
        
        # For demonstration only
        for i in range(5):
            folder_item = QStandardItem(f"폴더 {i+1}")
            root_item.appendRow(folder_item)
            
            for j in range(3):
                file_item = QStandardItem(f"파일 {j+1}.mp4")
                folder_item.appendRow(file_item) 