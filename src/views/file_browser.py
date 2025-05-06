#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파일 브라우저 컴포넌트 구현입니다.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QListView, 
    QFileSystemModel, QLabel, QPushButton, QComboBox, QLineEdit,
    QSplitter, QFileDialog, QMenu, QHeaderView
)
from PySide6.QtCore import Qt, QDir, QModelIndex, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QAction


class FileBrowser(QWidget):
    """
    파일 브라우저 컴포넌트.
    
    애니메이션 파일 탐색 및 선택을 위한 UI 컴포넌트입니다.
    """
    
    # 시그널 정의
    file_selected = Signal(str)  # 파일 선택 시 발생하는 시그널
    directory_changed = Signal(str)  # 디렉토리 변경 시 발생하는 시그널
    
    def __init__(self, parent=None):
        """파일 브라우저 컴포넌트 초기화."""
        super().__init__(parent)
        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 도구 모음 위젯
        self._setup_toolbar()
        
        # 스플리터 위젯 (트리뷰 + 목록뷰)
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # 파일 시스템 모델 생성
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.homePath())
        
        # 필터 설정 (비디오 파일 형식)
        self.fs_model.setNameFilters(["*.mkv", "*.mp4", "*.avi", "*.mov", "*.wmv"])
        self.fs_model.setNameFilterDisables(False)  # 비일치 항목 숨기기
        
        # 트리뷰 설정 (폴더 구조)
        self._setup_folder_tree()
        
        # 목록뷰 설정 (파일 목록)
        self._setup_file_list()
        
        # 상태 레이블
        self.status_label = QLabel("준비")
        self.layout.addWidget(self.status_label)
    
    def _setup_toolbar(self):
        """도구 모음 위젯 설정."""
        toolbar_layout = QHBoxLayout()
        
        # 홈 버튼
        self.home_button = QPushButton("홈")
        self.home_button.clicked.connect(self._go_to_home)
        toolbar_layout.addWidget(self.home_button)
        
        # 상위 폴더 버튼
        self.up_button = QPushButton("상위 폴더")
        self.up_button.clicked.connect(self._go_up)
        toolbar_layout.addWidget(self.up_button)
        
        # 경로 선택기
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMinimumWidth(300)
        self.path_combo.addItem(QDir.homePath())
        self.path_combo.activated.connect(self._on_path_changed)
        toolbar_layout.addWidget(self.path_combo)
        
        # 검색창
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("파일 검색...")
        self.search_input.textChanged.connect(self._on_search)
        toolbar_layout.addWidget(self.search_input)
        
        # 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self._refresh)
        toolbar_layout.addWidget(self.refresh_button)
        
        # 레이아웃에 추가
        self.layout.addLayout(toolbar_layout)
    
    def _setup_folder_tree(self):
        """폴더 트리뷰 설정."""
        self.folder_tree = QTreeView()
        self.folder_tree.setModel(self.fs_model)
        self.folder_tree.setRootIndex(self.fs_model.index(QDir.homePath()))
        
        # 폴더만 표시
        self.folder_tree.setAnimated(True)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setSortingEnabled(True)
        
        # 열 숨기기 (크기, 타입, 수정일 등)
        for i in range(1, self.fs_model.columnCount()):
            self.folder_tree.hideColumn(i)
        
        # 선택 이벤트 연결
        self.folder_tree.clicked.connect(self._on_folder_selected)
        
        # 컨텍스트 메뉴 설정
        self.folder_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self._show_folder_context_menu)
        
        # 스플리터에 추가
        self.splitter.addWidget(self.folder_tree)
    
    def _setup_file_list(self):
        """파일 목록뷰 설정."""
        self.file_list = QListView()
        self.file_list.setModel(self.fs_model)
        self.file_list.setRootIndex(self.fs_model.index(QDir.homePath()))
        
        # 아이콘 크기 설정
        self.file_list.setIconSize(QSize(32, 32))
        self.file_list.setSpacing(5)
        
        # 선택 이벤트 연결
        self.file_list.clicked.connect(self._on_file_selected)
        self.file_list.doubleClicked.connect(self._on_file_activated)
        
        # 컨텍스트 메뉴 설정
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_file_context_menu)
        
        # 스플리터에 추가
        self.splitter.addWidget(self.file_list)
    
    def _on_folder_selected(self, index):
        """폴더 선택 이벤트 핸들러."""
        path = self.fs_model.filePath(index)
        if os.path.isdir(path):
            self.file_list.setRootIndex(index)
            self._update_path_combo(path)
            self.directory_changed.emit(path)
    
    def _on_file_selected(self, index):
        """파일 선택 이벤트 핸들러."""
        path = self.fs_model.filePath(index)
        if os.path.isfile(path):
            self.status_label.setText(f"선택된 파일: {os.path.basename(path)}")
            self.file_selected.emit(path)
    
    def _on_file_activated(self, index):
        """파일 더블클릭 이벤트 핸들러."""
        path = self.fs_model.filePath(index)
        if os.path.isfile(path):
            # 여기에 파일 열기 기능 구현
            self.status_label.setText(f"파일 활성화: {os.path.basename(path)}")
    
    def _on_path_changed(self, index):
        """경로 콤보박스 변경 이벤트 핸들러."""
        path = self.path_combo.itemText(index)
        if os.path.exists(path) and os.path.isdir(path):
            model_index = self.fs_model.index(path)
            self.folder_tree.setCurrentIndex(model_index)
            self.file_list.setRootIndex(model_index)
            self.directory_changed.emit(path)
    
    def _go_to_home(self):
        """홈 디렉토리로 이동."""
        home_path = QDir.homePath()
        home_index = self.fs_model.index(home_path)
        self.folder_tree.setCurrentIndex(home_index)
        self.file_list.setRootIndex(home_index)
        self._update_path_combo(home_path)
        self.directory_changed.emit(home_path)
    
    def _go_up(self):
        """상위 폴더로 이동."""
        current_index = self.file_list.rootIndex()
        parent_index = current_index.parent()
        if parent_index.isValid():
            self.folder_tree.setCurrentIndex(parent_index)
            self.file_list.setRootIndex(parent_index)
            path = self.fs_model.filePath(parent_index)
            self._update_path_combo(path)
            self.directory_changed.emit(path)
    
    def _refresh(self):
        """파일 시스템 모델 새로고침."""
        current_path = self.fs_model.filePath(self.file_list.rootIndex())
        self.fs_model.setRootPath(self.fs_model.rootPath())  # 모델 갱신
        
        # 현재 경로 유지
        index = self.fs_model.index(current_path)
        self.file_list.setRootIndex(index)
        self.status_label.setText("새로고침 완료")
    
    def _on_search(self, text):
        """검색 기능 구현."""
        if text:
            filters = [f"*{text}*"]
        else:
            filters = ["*.mkv", "*.mp4", "*.avi", "*.mov", "*.wmv"]
        
        self.fs_model.setNameFilters(filters)
    
    def _update_path_combo(self, path):
        """경로 콤보박스 업데이트."""
        # 중복 방지
        if self.path_combo.findText(path) == -1:
            self.path_combo.addItem(path)
        
        self.path_combo.setCurrentText(path)
    
    def _show_folder_context_menu(self, position):
        """폴더 트리뷰 컨텍스트 메뉴."""
        index = self.folder_tree.indexAt(position)
        if not index.isValid():
            return
        
        menu = QMenu(self)
        
        # 새로운 스캔 항목으로 추가
        add_action = QAction("스캔 폴더로 추가", self)
        add_action.triggered.connect(lambda: self._add_scan_folder(index))
        menu.addAction(add_action)
        
        # 새로고침
        refresh_action = QAction("새로고침", self)
        refresh_action.triggered.connect(self._refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.folder_tree.viewport().mapToGlobal(position))
    
    def _show_file_context_menu(self, position):
        """파일 목록뷰 컨텍스트 메뉴."""
        index = self.file_list.indexAt(position)
        if not index.isValid():
            return
        
        path = self.fs_model.filePath(index)
        if not os.path.isfile(path):
            return
        
        menu = QMenu(self)
        
        # 파일 처리
        process_action = QAction("파일 처리", self)
        process_action.triggered.connect(lambda: self._process_file(path))
        menu.addAction(process_action)
        
        # 메타데이터 보기
        metadata_action = QAction("메타데이터 보기", self)
        metadata_action.triggered.connect(lambda: self._view_metadata(path))
        menu.addAction(metadata_action)
        
        menu.exec_(self.file_list.viewport().mapToGlobal(position))
    
    def _add_scan_folder(self, index):
        """스캔 폴더로 추가."""
        path = self.fs_model.filePath(index)
        self.status_label.setText(f"폴더 추가됨: {path}")
        # 실제 기능은 나중에 구현
    
    def _process_file(self, path):
        """파일 처리."""
        self.status_label.setText(f"파일 처리 중: {os.path.basename(path)}")
        # 실제 기능은 나중에 구현
    
    def _view_metadata(self, path):
        """메타데이터 보기."""
        self.status_label.setText(f"메타데이터 로드 중: {os.path.basename(path)}")
        # 실제 기능은 나중에 구현
    
    @Slot(str)
    def set_directory(self, path):
        """외부에서 디렉토리 설정 메서드."""
        if os.path.exists(path) and os.path.isdir(path):
            index = self.fs_model.index(path)
            self.folder_tree.setCurrentIndex(index)
            self.file_list.setRootIndex(index)
            self._update_path_combo(path)
    
    def get_current_directory(self):
        """현재 디렉토리 경로 반환."""
        return self.fs_model.filePath(self.file_list.rootIndex())
        
    def select_directory(self):
        """디렉토리 선택 대화상자 표시."""
        path = QFileDialog.getExistingDirectory(
            self,
            "스캔할 디렉토리 선택",
            self.get_current_directory(),
            QFileDialog.ShowDirsOnly
        )
        
        if path:
            self.set_directory(path)
            return path
        
        return None 