#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File browser screen for AnimeFileSorter.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QAction, QIcon, QPixmap, QStandardItemModel, QStandardItem
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
    QFrame,
    QProgressBar,
    QMessageBox,
    QMenu,
    QHeaderView
)

from src.controllers.file_controller import FileController
from src.models.media_item import MediaItem, MediaType
from src.utils.logger import log_info, log_error, log_debug, log_warning


class FileTreeView(QTreeView):
    """A customized tree view for displaying files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Setup model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["이름", "크기", "타입", "수정일"])
        self.setModel(self.model)
        
        # Adjust column widths and header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 150)
        
        # File extension to icon mapping
        self.file_icons = {}
        self._init_icons()
    
    def _init_icons(self):
        """Initialize file icons."""
        # This can be improved with actual icons later
        style = self.style()
        
        # Folder icon
        self.folder_icon = style.standardIcon(QStyle.SP_DirIcon)
        
        # Video file icon
        self.file_icons['.mp4'] = style.standardIcon(QStyle.SP_FileIcon)
        self.file_icons['.mkv'] = style.standardIcon(QStyle.SP_FileIcon)
        self.file_icons['.avi'] = style.standardIcon(QStyle.SP_FileIcon)
        
        # Subtitle file icon
        self.file_icons['.srt'] = style.standardIcon(QStyle.SP_FileIcon)
        self.file_icons['.ass'] = style.standardIcon(QStyle.SP_FileIcon)
        
        # Default file icon
        self.default_icon = style.standardIcon(QStyle.SP_FileIcon)


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
        
        # Media info section
        self.media_title_label = QLabel("미디어 제목")
        self.media_title_label.setFont(font)
        self.media_title_label.setVisible(False)
        
        self.media_title_value = QLabel("")
        self.media_title_value.setWordWrap(True)
        self.media_title_value.setVisible(False)
        
        # Series-specific info
        self.series_info_layout = QVBoxLayout()
        
        self.season_label = QLabel("시즌")
        self.season_label.setFont(font)
        
        self.season_value = QLabel("")
        
        self.episode_label = QLabel("에피소드")
        self.episode_label.setFont(font)
        
        self.episode_value = QLabel("")
        
        self.series_info_layout.addWidget(self.season_label)
        self.series_info_layout.addWidget(self.season_value)
        self.series_info_layout.addSpacing(5)
        self.series_info_layout.addWidget(self.episode_label)
        self.series_info_layout.addWidget(self.episode_value)
        
        # Hide series info by default
        self.season_label.setVisible(False)
        self.season_value.setVisible(False)
        self.episode_label.setVisible(False)
        self.episode_value.setVisible(False)
        
        # Movie-specific info
        self.movie_info_layout = QVBoxLayout()
        
        self.year_label = QLabel("개봉 연도")
        self.year_label.setFont(font)
        
        self.year_value = QLabel("")
        
        self.movie_info_layout.addWidget(self.year_label)
        self.movie_info_layout.addWidget(self.year_value)
        
        # Hide movie info by default
        self.year_label.setVisible(False)
        self.year_value.setVisible(False)
        
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
        layout.addSpacing(20)
        
        # Media info
        layout.addWidget(self.media_title_label)
        layout.addWidget(self.media_title_value)
        layout.addSpacing(10)
        
        # Add specific layouts
        layout.addLayout(self.series_info_layout)
        layout.addLayout(self.movie_info_layout)
        
        layout.addStretch()
    
    def update_info(self, file_details: Dict[str, Any]):
        """
        Update the panel with file details.
        
        Args:
            file_details: Dictionary with file details
        """
        # Reset visibility
        self.media_title_label.setVisible(False)
        self.media_title_value.setVisible(False)
        self.season_label.setVisible(False)
        self.season_value.setVisible(False)
        self.episode_label.setVisible(False)
        self.episode_value.setVisible(False)
        self.year_label.setVisible(False)
        self.year_value.setVisible(False)
        
        # Update basic info
        self.name_value.setText(file_details.get("name", ""))
        self.path_value.setText(file_details.get("path", ""))
        self.size_value.setText(file_details.get("size_formatted", ""))
        self.type_value.setText(file_details.get("extension", "").upper())
        self.modified_value.setText(file_details.get("modified_formatted", ""))
        
        # Update media info if available
        if "title" in file_details:
            self.media_title_label.setVisible(True)
            self.media_title_value.setVisible(True)
            self.media_title_value.setText(file_details.get("title", ""))
            
            # Series-specific info
            if file_details.get("media_type") == "series" and "season" in file_details and "episode" in file_details:
                self.season_label.setVisible(True)
                self.season_value.setVisible(True)
                self.season_value.setText(f"시즌 {file_details.get('season', '')}")
                
                self.episode_label.setVisible(True)
                self.episode_value.setVisible(True)
                episode_text = f"에피소드 {file_details.get('episode', '')}"
                if "episode_title" in file_details:
                    episode_text += f" - {file_details.get('episode_title', '')}"
                self.episode_value.setText(episode_text)
            
            # Movie-specific info
            if file_details.get("media_type") == "movie" and "year" in file_details:
                self.year_label.setVisible(True)
                self.year_value.setVisible(True)
                self.year_value.setText(str(file_details.get("year", "")))
    
    def clear(self):
        """Clear all information in the panel."""
        self.name_value.setText("")
        self.path_value.setText("")
        self.size_value.setText("")
        self.type_value.setText("")
        self.modified_value.setText("")
        self.media_title_value.setText("")
        self.season_value.setText("")
        self.episode_value.setText("")
        self.year_value.setText("")
        
        # Hide media-specific sections
        self.media_title_label.setVisible(False)
        self.media_title_value.setVisible(False)
        self.season_label.setVisible(False)
        self.season_value.setVisible(False)
        self.episode_label.setVisible(False)
        self.episode_value.setVisible(False)
        self.year_label.setVisible(False)
        self.year_value.setVisible(False)


class FileBrowserScreen(QWidget):
    """File browser screen for exploring and managing files."""
    
    def __init__(self, file_controller: Optional[FileController] = None):
        super().__init__()
        
        # Create a controller if not provided
        self.file_controller = file_controller or FileController()
        
        # Track current directory
        self.current_directory = ""
        
        # Connect controller signals
        self.file_controller.scan_started.connect(self.on_scan_started)
        self.file_controller.scan_progress.connect(self.on_scan_progress)
        self.file_controller.scan_completed.connect(self.on_scan_completed)
        self.file_controller.scan_error.connect(self.on_scan_error)
        
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
        self.refresh_button = QPushButton("새로고침")
        toolbar.addWidget(self.refresh_button)
        
        # Cancel button (initially hidden)
        self.cancel_button = QPushButton("취소")
        self.cancel_button.setVisible(False)
        toolbar.addWidget(self.cancel_button)
        
        # Add toolbar to layout
        layout.addWidget(toolbar)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
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
        
        self.organize_button = QPushButton("파일 정리")
        self.organize_button.setMinimumSize(120, 30)
        self.organize_button.setEnabled(False)  # Disabled until files are loaded
        button_layout.addWidget(self.organize_button)
        
        self.preview_button = QPushButton("정리 미리보기")
        self.preview_button.setMinimumSize(120, 30)
        self.preview_button.setEnabled(False)  # Disabled until files are loaded
        button_layout.addWidget(self.preview_button)
        
        button_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("준비됨")
        button_layout.addWidget(self.status_label)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        browse_button.clicked.connect(self.on_browse_clicked)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.organize_button.clicked.connect(self.on_organize_clicked)
        self.preview_button.clicked.connect(self.on_preview_clicked)
        self.file_tree.selectionModel().selectionChanged.connect(self.on_file_selected)
        self.file_tree.customContextMenuRequested.connect(self.on_context_menu)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
    
    def on_browse_clicked(self):
        """Handle browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "폴더 선택", "", QFileDialog.ShowDirsOnly
        )
        if directory:
            self.folder_path.setText(directory)
            self.current_directory = directory
            self.load_directory(directory)
    
    def on_refresh_clicked(self):
        """Handle refresh button click."""
        if self.current_directory:
            self.load_directory(self.current_directory)
    
    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.file_controller.cancel_scan()
        self.status_label.setText("스캔 취소 중...")
    
    def on_organize_clicked(self):
        """Handle organize button click."""
        # Prompt for output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "출력 폴더 선택", "", QFileDialog.ShowDirsOnly
        )
        
        if output_dir:
            # Check if it's the same as input directory
            if output_dir == self.current_directory:
                reply = QMessageBox.question(
                    self,
                    "출력 폴더 확인",
                    "출력 폴더가 입력 폴더와 동일합니다. 계속하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            try:
                # Set output directory and organize files
                self.file_controller.set_directories(self.current_directory, output_dir)
                operations = self.file_controller.organize_files(preview_only=False)
                
                # Show success message
                QMessageBox.information(
                    self,
                    "정리 완료",
                    f"{len(operations)}개의 파일이 성공적으로 정리되었습니다."
                )
                
                # Refresh current directory
                self.load_directory(self.current_directory)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "오류",
                    f"파일 정리 중 오류가 발생했습니다: {str(e)}"
                )
    
    def on_preview_clicked(self):
        """Handle preview button click."""
        # Prompt for output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "출력 폴더 선택", "", QFileDialog.ShowDirsOnly
        )
        
        if output_dir:
            try:
                # Set output directory and get preview
                self.file_controller.set_directories(self.current_directory, output_dir)
                operations = self.file_controller.organize_files(preview_only=True)
                
                if operations:
                    # Show preview dialog
                    preview_text = "다음 작업이 수행될 예정입니다:\n\n"
                    
                    # Limit to 20 items for display clarity
                    display_operations = operations[:20]
                    for src, dest in display_operations:
                        preview_text += f"- {os.path.basename(src)} → {os.path.basename(dest)}\n"
                    
                    if len(operations) > 20:
                        preview_text += f"\n... 외 {len(operations) - 20}개 파일"
                    
                    QMessageBox.information(
                        self,
                        "정리 미리보기",
                        preview_text
                    )
                else:
                    QMessageBox.information(
                        self,
                        "미리보기",
                        "정리할 작업이 없습니다."
                    )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "오류",
                    f"미리보기 생성 중 오류가 발생했습니다: {str(e)}"
                )
    
    def on_file_selected(self, selected, deselected):
        """Handle file selection change."""
        indexes = selected.indexes()
        if indexes:
            # Get the first column index (filename)
            index = indexes[0]
            if index.isValid():
                # Get the file path from the model's data
                item = self.file_tree.model.itemFromIndex(index)
                if item and hasattr(item, 'file_path'):
                    try:
                        # Get file details and update the info panel
                        file_details = self.file_controller.get_file_details(item.file_path)
                        self.info_panel.update_info(file_details)
                    except Exception as e:
                        log_error(f"Error getting file details: {e}")
                        self.info_panel.clear()
                else:
                    self.info_panel.clear()
    
    def on_context_menu(self, position):
        """Handle context menu request."""
        index = self.file_tree.indexAt(position)
        if index.isValid():
            item = self.file_tree.model.itemFromIndex(index)
            if hasattr(item, 'file_path'):
                menu = QMenu(self)
                
                # Add actions to the menu
                open_action = QAction("열기", self)
                open_action.triggered.connect(lambda: self.open_file(item.file_path))
                menu.addAction(open_action)
                
                open_folder_action = QAction("폴더 열기", self)
                open_folder_action.triggered.connect(lambda: self.open_containing_folder(item.file_path))
                menu.addAction(open_folder_action)
                
                menu.addSeparator()
                
                copy_path_action = QAction("경로 복사", self)
                copy_path_action.triggered.connect(lambda: self.copy_path_to_clipboard(item.file_path))
                menu.addAction(copy_path_action)
                
                # Show the menu
                menu.exec_(self.file_tree.viewport().mapToGlobal(position))
    
    def open_file(self, file_path):
        """Open the selected file with the default application."""
        import subprocess
        import os
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            QMessageBox.critical(
                self,
                "파일 열기 오류",
                f"파일을 열 수 없습니다: {str(e)}"
            )
    
    def open_containing_folder(self, file_path):
        """Open the folder containing the file."""
        import subprocess
        import os
        
        try:
            folder_path = os.path.dirname(file_path)
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', folder_path])
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(('xdg-open', folder_path))
        except Exception as e:
            QMessageBox.critical(
                self,
                "폴더 열기 오류",
                f"폴더를 열 수 없습니다: {str(e)}"
            )
    
    def copy_path_to_clipboard(self, file_path):
        """Copy the file path to clipboard."""
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)
    
    def load_directory(self, directory_path):
        """Load the directory structure into the tree view."""
        self.current_directory = directory_path
        self.file_controller.set_directories(directory_path)
        
        # Start async scanning
        try:
            self.file_controller.scan_directory_async(directory_path)
        except Exception as e:
            log_error(f"Error starting directory scan: {e}")
            QMessageBox.critical(
                self,
                "스캔 오류",
                f"디렉토리 스캔 중 오류가 발생했습니다: {str(e)}"
            )
    
    @Slot()
    def on_scan_started(self):
        """Handle scan started signal."""
        # Update UI to show scanning state
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.refresh_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.organize_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.file_tree.model.clear()
        self.file_tree.model.setHorizontalHeaderLabels(["이름", "크기", "타입", "수정일"])
        self.status_label.setText("디렉토리 스캔 중...")
    
    @Slot(int, int, str)
    def on_scan_progress(self, current, total, filename):
        """
        Handle scan progress signal.
        
        Args:
            current: Current progress value
            total: Total progress value
            filename: Current filename being processed
        """
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"스캔 중... {current}/{total} ({os.path.basename(filename)})")
        else:
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self.status_label.setText(f"스캔 중... ({os.path.basename(filename)})")
    
    @Slot(list)
    def on_scan_completed(self, media_items: List[MediaItem]):
        """
        Handle scan completed signal.
        
        Args:
            media_items: List of media items found
        """
        # Update UI to show normal state
        self.progress_bar.setVisible(False)
        self.refresh_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.organize_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        
        # Update status
        self.status_label.setText(f"{len(media_items)}개 파일 발견")
        
        # Display the files in the tree view
        self.populate_tree_view(media_items)
    
    @Slot(str)
    def on_scan_error(self, error_message: str):
        """
        Handle scan error signal.
        
        Args:
            error_message: Error message
        """
        # Update UI to show normal state
        self.progress_bar.setVisible(False)
        self.refresh_button.setVisible(True)
        self.cancel_button.setVisible(False)
        
        # Show error message
        QMessageBox.critical(
            self,
            "스캔 오류",
            f"디렉토리 스캔 중 오류가 발생했습니다: {error_message}"
        )
        
        self.status_label.setText("오류 발생")
    
    def populate_tree_view(self, media_items: List[MediaItem]):
        """
        Populate the tree view with media items.
        
        Args:
            media_items: List of media items to display
        """
        # Clear the model
        self.file_tree.model.clear()
        self.file_tree.model.setHorizontalHeaderLabels(["이름", "크기", "타입", "수정일"])
        
        # Group files by directory
        file_groups = {}
        for item in media_items:
            dir_path = os.path.dirname(item.file_path)
            rel_dir = os.path.relpath(dir_path, self.current_directory)
            
            if rel_dir not in file_groups:
                file_groups[rel_dir] = []
            
            file_groups[rel_dir].append(item)
        
        # Sort directories for consistent display
        sorted_dirs = sorted(file_groups.keys())
        
        # Add root item for the main directory
        root_item = QStandardItem(os.path.basename(self.current_directory))
        root_item.setIcon(self.file_tree.folder_icon)
        self.file_tree.model.appendRow(root_item)
        
        # Fill the tree
        for dir_path in sorted_dirs:
            # Skip the root directory (.)
            if dir_path == ".":
                parent_item = root_item
            else:
                # Create folder items for the directory path
                parent_item = self._create_folder_structure(root_item, dir_path)
            
            # Add files to the parent directory
            for media_item in sorted(file_groups[dir_path], key=lambda x: x.file_name):
                # Create a row for the file
                file_name_item = QStandardItem(media_item.file_name)
                
                # Store the full path for selection handling
                file_name_item.file_path = media_item.file_path
                
                # Set icon based on file type
                if media_item.file_extension.lower() in self.file_tree.file_icons:
                    file_name_item.setIcon(self.file_tree.file_icons[media_item.file_extension.lower()])
                else:
                    file_name_item.setIcon(self.file_tree.default_icon)
                
                # Create additional columns
                size_item = QStandardItem(self._format_file_size(media_item.file_size))
                type_item = QStandardItem(media_item.file_extension.upper().lstrip('.'))
                date_item = QStandardItem(media_item.file_modified.strftime("%Y-%m-%d %H:%M"))
                
                # Add the row to the parent
                parent_item.appendRow([file_name_item, size_item, type_item, date_item])
        
        # Expand the root item
        self.file_tree.expand(root_item.index())
        
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} PB"
    
    def _create_folder_structure(self, root_item: QStandardItem, dir_path: str) -> QStandardItem:
        """
        Create the folder structure in the tree view.
        
        Args:
            root_item: Root item in the tree
            dir_path: Directory path relative to the root
            
        Returns:
            The item representing the last directory in the path
        """
        parts = dir_path.split(os.sep)
        parent_item = root_item
        
        # Create folder items for each part of the path
        current_path = []
        for part in parts:
            if not part:  # Skip empty parts
                continue
                
            current_path.append(part)
            
            # Check if this folder already exists
            folder_item = None
            for row in range(parent_item.rowCount()):
                child = parent_item.child(row, 0)
                if child and child.text() == part:
                    folder_item = child
                    break
            
            # If not, create it
            if folder_item is None:
                folder_item = QStandardItem(part)
                folder_item.setIcon(self.file_tree.folder_icon)
                # Store the full path for the folder
                rel_path = os.path.join(*current_path)
                folder_item.file_path = os.path.join(self.current_directory, rel_path)
                parent_item.appendRow([folder_item])
            
            parent_item = folder_item
        
        return parent_item
    
    def apply_filter(self, index: int):
        """
        Apply filter to the current view.
        
        Args:
            index: Index of the selected filter
        """
        # This will be implemented when filtering is needed
        pass 