#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파일 시스템 변경 사항을 감시하는 모듈입니다.
이 모듈은 지정된 디렉토리에서 파일 생성, 수정, 삭제 등의 이벤트를 감지합니다.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Callable, Set, Optional
from threading import Thread, Event

try:
    from watchdog.observers import Observer
    from watchdog.events import (
        FileSystemEventHandler, 
        FileCreatedEvent, 
        FileModifiedEvent, 
        FileDeletedEvent,
        FileMovedEvent,
        DirCreatedEvent,
        DirModifiedEvent,
        DirDeletedEvent,
        DirMovedEvent
    )
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FileWatcherEventHandler(FileSystemEventHandler):
    """파일 시스템 이벤트를 처리하는 핸들러."""
    
    def __init__(self, callback: Callable[[str, str], None], file_extensions: List[str] = None):
        """
        이벤트 핸들러 초기화.
        
        Args:
            callback: 이벤트 발생 시 호출될 콜백 함수 (event_type, file_path)
            file_extensions: 감시할 파일 확장자 목록 (None이면 모든 파일)
        """
        self.callback = callback
        self.file_extensions = [ext.lower() for ext in file_extensions] if file_extensions else None
    
    def _is_valid_file(self, path: str) -> bool:
        """
        파일이 감시 대상인지 확인합니다.
        
        Args:
            path: 파일 경로
            
        Returns:
            감시 대상이면 True, 아니면 False
        """
        if not self.file_extensions:
            return True
        
        _, ext = os.path.splitext(path)
        return ext.lower() in self.file_extensions
    
    def on_created(self, event):
        """파일 생성 이벤트 처리."""
        if not event.is_directory and self._is_valid_file(event.src_path):
            self.callback("created", event.src_path)
    
    def on_modified(self, event):
        """파일 수정 이벤트 처리."""
        if not event.is_directory and self._is_valid_file(event.src_path):
            self.callback("modified", event.src_path)
    
    def on_deleted(self, event):
        """파일 삭제 이벤트 처리."""
        if not event.is_directory and self._is_valid_file(event.src_path):
            self.callback("deleted", event.src_path)
    
    def on_moved(self, event):
        """파일 이동 이벤트 처리."""
        if not event.is_directory:
            if self._is_valid_file(event.src_path):
                self.callback("moved_from", event.src_path)
            if self._is_valid_file(event.dest_path):
                self.callback("moved_to", event.dest_path)


class SimpleFileWatcher:
    """
    간단한 폴링 기반 파일 감시 클래스 (Watchdog 라이브러리 없을 때 사용).
    참고: 리소스 사용량이 높으므로 프로덕션 환경에서는 Watchdog 사용을 권장합니다.
    """
    
    def __init__(self, callback: Callable[[str, str], None], poll_interval: float = 5.0):
        """
        SimpleFileWatcher 초기화.
        
        Args:
            callback: 이벤트 발생 시 호출될 콜백 함수 (event_type, file_path)
            poll_interval: 폴링 간격 (초 단위)
        """
        self.callback = callback
        self.poll_interval = poll_interval
        self.watched_dirs: Dict[str, Dict[str, float]] = {}  # {dir_path: {file_path: mtime}}
        self.running = False
        self.stop_event = Event()
        self.watch_thread = None
    
    def start(self):
        """감시 시작."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.watch_thread = Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
    
    def stop(self):
        """감시 중지."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        if self.watch_thread:
            self.watch_thread.join(timeout=2.0)
            self.watch_thread = None
    
    def add_directory(self, path: str, file_extensions: List[str] = None):
        """
        감시할 디렉토리 추가.
        
        Args:
            path: 감시할 디렉토리 경로
            file_extensions: 감시할 파일 확장자 목록 (None이면 모든 파일)
        """
        if not os.path.isdir(path):
            raise ValueError(f"경로가 유효한 디렉토리가 아닙니다: {path}")
        
        current_files = {}
        
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 확장자 필터링
                if file_extensions:
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() not in [ext.lower() for ext in file_extensions]:
                        continue
                
                try:
                    mtime = os.path.getmtime(file_path)
                    current_files[file_path] = mtime
                except OSError:
                    # 파일 접근 중 오류 발생 시 무시
                    pass
        
        self.watched_dirs[path] = current_files
    
    def remove_directory(self, path: str):
        """
        감시 디렉토리 제거.
        
        Args:
            path: 제거할 디렉토리 경로
        """
        if path in self.watched_dirs:
            del self.watched_dirs[path]
    
    def _watch_loop(self):
        """감시 루프 실행."""
        while self.running and not self.stop_event.is_set():
            for dir_path, old_files in list(self.watched_dirs.items()):
                if not os.path.exists(dir_path):
                    continue
                
                current_files = {}
                
                # 현재 파일 상태 스캔
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(file_path)
                            current_files[file_path] = mtime
                        except OSError:
                            # 파일 접근 중 오류 발생 시 무시
                            pass
                
                # 새로운 파일 탐지
                for file_path, mtime in current_files.items():
                    if file_path not in old_files:
                        self.callback("created", file_path)
                    elif mtime > old_files[file_path]:
                        self.callback("modified", file_path)
                
                # 삭제된 파일 탐지
                for file_path in old_files:
                    if file_path not in current_files:
                        self.callback("deleted", file_path)
                
                # 파일 목록 업데이트
                self.watched_dirs[dir_path] = current_files
            
            # 다음 폴링까지 대기
            self.stop_event.wait(self.poll_interval)


class FileWatcher:
    """
    파일 시스템 변경 사항을 감시하는 클래스.
    가능한 경우 Watchdog 라이브러리를 사용하고, 없으면 자체 구현 폴링 방식으로 대체.
    """
    
    def __init__(self, callback: Callable[[str, str], None], use_watchdog: bool = True):
        """
        FileWatcher 초기화.
        
        Args:
            callback: 이벤트 발생 시 호출될 콜백 함수 (event_type, file_path)
            use_watchdog: Watchdog 라이브러리 사용 여부
        """
        self.callback = callback
        self.use_watchdog = use_watchdog and WATCHDOG_AVAILABLE
        
        if self.use_watchdog:
            self.observer = Observer()
            self.handlers = {}  # {path: event_handler}
        else:
            self.watcher = SimpleFileWatcher(callback)
    
    def start(self):
        """감시 시작."""
        if self.use_watchdog:
            self.observer.start()
        else:
            self.watcher.start()
    
    def stop(self):
        """감시 중지."""
        if self.use_watchdog:
            self.observer.stop()
            self.observer.join()
        else:
            self.watcher.stop()
    
    def add_directory(self, path: str, recursive: bool = True, file_extensions: List[str] = None):
        """
        감시할 디렉토리 추가.
        
        Args:
            path: 감시할 디렉토리 경로
            recursive: 하위 디렉토리도 감시할지 여부
            file_extensions: 감시할 파일 확장자 목록 (None이면 모든 파일)
        """
        path = os.path.abspath(path)
        
        if not os.path.isdir(path):
            raise ValueError(f"경로가 유효한 디렉토리가 아닙니다: {path}")
        
        if self.use_watchdog:
            event_handler = FileWatcherEventHandler(self.callback, file_extensions)
            self.observer.schedule(event_handler, path, recursive=recursive)
            self.handlers[path] = event_handler
        else:
            self.watcher.add_directory(path, file_extensions)
    
    def remove_directory(self, path: str):
        """
        감시 디렉토리 제거.
        
        Args:
            path: 제거할 디렉토리 경로
        """
        path = os.path.abspath(path)
        
        if self.use_watchdog:
            for watch in list(self.observer._watches.keys()):
                if watch.path == path:
                    self.observer.unschedule(watch)
            
            if path in self.handlers:
                del self.handlers[path]
        else:
            self.watcher.remove_directory(path)


def get_supported_backends() -> List[str]:
    """
    지원되는 파일 감시 백엔드 목록을 반환합니다.
    
    Returns:
        지원되는 백엔드 목록
    """
    backends = ["simple_polling"]
    
    if WATCHDOG_AVAILABLE:
        backends.insert(0, "watchdog")
    
    return backends 