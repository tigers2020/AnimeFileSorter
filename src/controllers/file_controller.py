#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File controller for AnimeFileSorter.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot, QMetaObject, Qt, Q_ARG

from src.services.scanner_service import ScannerService
from src.services.organizer_service import OrganizerService
from src.models.media_item import MediaItem
from src.utils.logger import log_info, log_error, log_warning, log_debug


class WorkerSignals(QObject):
    """Signals for the worker thread."""
    
    started = Signal()
    finished = Signal()
    error = Signal(str)
    progress = Signal(int, int, str)  # current, total, filename
    result = Signal(object)


class ScanWorker(QRunnable):
    """Worker thread for scanning files."""
    
    def __init__(self, scanner_service: ScannerService, directory: str):
        """
        Initialize the worker.
        
        Args:
            scanner_service: Service for scanning files
            directory: Directory to scan
        """
        super().__init__()
        self.scanner_service = scanner_service
        self.directory = directory
        self.signals = WorkerSignals()
    
    @Slot()
    def run(self):
        """Run the scan operation."""
        self.signals.started.emit()
        try:
            # Run the scan with progress reporting
            result = self.scanner_service.scan_directory(
                self.directory,
                progress_callback=self._progress_callback
            )
            self.signals.result.emit(result)
        except Exception as e:
            log_error(f"Error scanning directory: {e}")
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
    
    def _progress_callback(self, current: int, total: int, filename: str):
        """Report progress to the UI."""
        self.signals.progress.emit(current, total, filename)


class FileController(QObject):
    """Controller for handling file operations."""
    
    # Signals
    scan_started = Signal()
    scan_progress = Signal(int, int, str)  # current, total, filename
    scan_completed = Signal(list)
    scan_error = Signal(str)
    organize_completed = Signal(list)
    organize_error = Signal(str)
    
    def __init__(self, setting_service=None):
        """
        Initialize the file controller.
        
        Args:
            setting_service: Service for managing settings
        """
        super().__init__()
        
        # 설정 서비스 저장
        self.setting_service = setting_service
        
        # 서비스 초기화 (설정 서비스 전달)
        self.scanner_service = ScannerService(setting_service)
        self.organizer_service = OrganizerService(setting_service)
        
        # 기본 디렉토리 설정
        if setting_service:
            self.input_directory = setting_service.get_input_directory()
            self.output_directory = setting_service.get_output_directory()
        else:
            self.input_directory = ""
            self.output_directory = ""
            
        self.scanned_files: List[MediaItem] = []
        
        # Thread pool for background operations
        self.thread_pool = QThreadPool()
        log_info(f"Using maximum {self.thread_pool.maxThreadCount()} threads")
    
    def set_directories(self, input_dir: str, output_dir: Optional[str] = None) -> None:
        """
        Set the input and output directories.
        
        Args:
            input_dir: Path to the input directory
            output_dir: Path to the output directory. If None, defaults to input_dir/organized
        """
        self.input_directory = input_dir
        
        if output_dir is None:
            # Default output directory is a subdirectory named 'organized' in the parent of input_dir
            parent_dir = str(Path(input_dir).parent)
            self.output_directory = os.path.join(parent_dir, "organized")
        else:
            self.output_directory = output_dir
            
        log_info(f"Directories set - Input: {self.input_directory}, Output: {self.output_directory}")
    
    def scan_directory_async(self, directory: Optional[str] = None) -> None:
        """
        Scan a directory for media files asynchronously.
        
        Args:
            directory: Directory to scan. If None, uses the previously set input_directory.
        """
        if directory is not None:
            self.input_directory = directory
            
        if not self.input_directory:
            raise ValueError("Input directory not set.")
        
        # Create and configure the worker
        worker = ScanWorker(self.scanner_service, self.input_directory)
        
        # Connect signals
        worker.signals.started.connect(self.scan_started)
        worker.signals.progress.connect(self.scan_progress)
        worker.signals.result.connect(self._handle_scan_result)
        worker.signals.error.connect(self.scan_error)
        
        log_info(f"Starting async scan of directory: {self.input_directory}")
        self.thread_pool.start(worker)
    
    def scan_directory(self, directory: Optional[str] = None) -> List[MediaItem]:
        """
        Scan a directory for media files synchronously.
        
        Args:
            directory: Directory to scan. If None, uses the previously set input_directory.
            
        Returns:
            List of media items found
        """
        if directory is not None:
            self.input_directory = directory
            
        if not self.input_directory:
            raise ValueError("Input directory not set.")
        
        log_info(f"Starting sync scan of directory: {self.input_directory}")
        self.scanned_files = self.scanner_service.scan_directory(self.input_directory)
        return self.scanned_files
    
    def cancel_scan(self) -> None:
        """Cancel the current scan operation."""
        self.scanner_service.cancel_scanning()
        log_info("Scan cancellation requested")
    
    @Slot(object)
    def _handle_scan_result(self, result: List[MediaItem]):
        """
        Handle the scan result.
        
        Args:
            result: List of media items found
        """
        self.scanned_files = result
        self.scan_completed.emit(result)
        log_info(f"Scan completed with {len(result)} files")
    
    def organize_files(self, preview_only: bool = False) -> List[Tuple[str, str]]:
        """
        Organize the scanned files according to settings.
        
        Args:
            preview_only: If True, returns the operations that would be performed without actually doing them
            
        Returns:
            List of (source, destination) paths for each file
        """
        if not self.scanned_files:
            raise ValueError("No files scanned. Run scan_directory first.")
            
        if not self.output_directory:
            raise ValueError("Output directory not set.")
            
        log_info(f"Organizing files to: {self.output_directory} (preview: {preview_only})")
        
        try:
            result = self.organizer_service.organize_files(
                self.scanned_files,
                self.output_directory,
                preview_only
            )
            self.organize_completed.emit(result)
            return result
        except Exception as e:
            log_error(f"Error organizing files: {e}")
            self.organize_error.emit(str(e))
            raise
    
    def organize_files_async(self, preview_only: bool = False) -> None:
        """
        Organize the scanned files according to settings asynchronously.
        
        Args:
            preview_only: If True, returns the operations that would be performed without actually doing them
        """
        # This will be implemented in the next sprint
        pass
    
    def get_file_details(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file details
        """
        # Find the media item if it's in our scanned files
        for item in self.scanned_files:
            if item.file_path == file_path:
                return self._media_item_to_details(item)
        
        # If not in scanned files, get basic info
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        stats = file.stat()
        
        # Format size
        size_str = self._format_file_size(stats.st_size)
        
        # Format date
        import datetime
        modified_date = datetime.datetime.fromtimestamp(stats.st_mtime)
        date_str = modified_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "name": file.name,
            "path": str(file),
            "size": stats.st_size,
            "size_formatted": size_str, 
            "modified": stats.st_mtime,
            "modified_formatted": date_str,
            "extension": file.suffix.lower(),
            "is_video": file.suffix.lower() in self.scanner_service.VIDEO_EXTENSIONS,
            "is_subtitle": file.suffix.lower() in self.scanner_service.SUBTITLE_EXTENSIONS,
        }
    
    def _media_item_to_details(self, item: MediaItem) -> Dict[str, Any]:
        """
        Convert a MediaItem to a dictionary of details.
        
        Args:
            item: The MediaItem to convert
            
        Returns:
            Dictionary with file details
        """
        # Format size
        size_str = self._format_file_size(item.file_size)
        
        # Format date
        date_str = item.file_modified.strftime("%Y-%m-%d %H:%M:%S")
        
        details = {
            "name": item.file_name,
            "path": item.file_path,
            "size": item.file_size,
            "size_formatted": size_str,
            "modified": item.file_modified.timestamp(),
            "modified_formatted": date_str,
            "extension": item.file_extension,
            "is_video": item.file_extension in self.scanner_service.VIDEO_EXTENSIONS,
            "is_subtitle": item.file_extension in self.scanner_service.SUBTITLE_EXTENSIONS,
            "media_type": item.media_type.value,
            "title": item.title,
        }
        
        # Add series-specific details
        if "season" in item.metadata:
            details["season"] = item.metadata["season"]
        
        if "episode" in item.metadata:
            details["episode"] = item.metadata["episode"]
            
        if "episode_title" in item.metadata:
            details["episode_title"] = item.metadata["episode_title"]
            
        # Add movie-specific details
        if item.year:
            details["year"] = item.year
            
        return details
    
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
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} PB" 