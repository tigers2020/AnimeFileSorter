#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
메타데이터 표시 컴포넌트 구현입니다.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QScrollArea, QFormLayout, QLineEdit, QTextEdit,
    QTabWidget, QGridLayout, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage


class MetadataView(QWidget):
    """
    메타데이터 표시 컴포넌트.
    
    애니메이션 및 에피소드 메타데이터를 표시하는 UI 컴포넌트입니다.
    """
    
    # 시그널 정의
    metadata_updated = Signal(dict)  # 메타데이터 수정 시 발생하는 시그널
    
    def __init__(self, parent=None):
        """메타데이터 표시 컴포넌트 초기화."""
        super().__init__(parent)
        
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # 파일 정보 탭
        self.file_info_widget = QWidget()
        self.tab_widget.addTab(self.file_info_widget, "파일 정보")
        self._setup_file_info_tab()
        
        # 시리즈 정보 탭
        self.series_info_widget = QWidget()
        self.tab_widget.addTab(self.series_info_widget, "시리즈 정보")
        self._setup_series_info_tab()
        
        # 에피소드 정보 탭
        self.episode_info_widget = QWidget()
        self.tab_widget.addTab(self.episode_info_widget, "에피소드 정보")
        self._setup_episode_info_tab()
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self._refresh_metadata)
        button_layout.addWidget(self.refresh_button)
        
        # 온라인 검색 버튼
        self.search_button = QPushButton("온라인 검색")
        self.search_button.clicked.connect(self._search_online)
        button_layout.addWidget(self.search_button)
        
        # 변경사항 저장 버튼
        self.save_button = QPushButton("저장")
        self.save_button.clicked.connect(self._save_changes)
        button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(button_layout)
        
        # 현재 파일 경로
        self._current_file_path = None
        
        # 편집 가능 상태
        self._editable = False
    
    def _setup_file_info_tab(self):
        """파일 정보 탭 설정."""
        layout = QVBoxLayout(self.file_info_widget)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # 스크롤 내용 위젯
        content = QWidget()
        scroll.setWidget(content)
        
        # 폼 레이아웃
        form_layout = QFormLayout(content)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 파일 경로
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        form_layout.addRow("파일 경로:", self.file_path_edit)
        
        # 파일 크기
        self.file_size_label = QLabel()
        form_layout.addRow("파일 크기:", self.file_size_label)
        
        # 파일 확장자
        self.file_ext_label = QLabel()
        form_layout.addRow("파일 형식:", self.file_ext_label)
        
        # ED2K 해시
        self.ed2k_hash_edit = QLineEdit()
        self.ed2k_hash_edit.setReadOnly(True)
        form_layout.addRow("ED2K 해시:", self.ed2k_hash_edit)
        
        # 비디오 정보 그룹
        video_group = QGroupBox("비디오 정보")
        video_layout = QFormLayout(video_group)
        
        self.video_codec_label = QLabel()
        video_layout.addRow("코덱:", self.video_codec_label)
        
        self.video_resolution_label = QLabel()
        video_layout.addRow("해상도:", self.video_resolution_label)
        
        self.video_fps_label = QLabel()
        video_layout.addRow("프레임 레이트:", self.video_fps_label)
        
        self.video_duration_label = QLabel()
        video_layout.addRow("재생 시간:", self.video_duration_label)
        
        form_layout.addRow("", video_group)
        
        # 오디오 정보 그룹
        audio_group = QGroupBox("오디오 정보")
        audio_layout = QFormLayout(audio_group)
        
        self.audio_codec_label = QLabel()
        audio_layout.addRow("코덱:", self.audio_codec_label)
        
        self.audio_channels_label = QLabel()
        audio_layout.addRow("채널:", self.audio_channels_label)
        
        self.audio_languages_label = QLabel()
        audio_layout.addRow("언어:", self.audio_languages_label)
        
        form_layout.addRow("", audio_group)
        
        # 자막 정보 그룹
        subtitle_group = QGroupBox("자막 정보")
        subtitle_layout = QFormLayout(subtitle_group)
        
        self.subtitle_languages_label = QLabel()
        subtitle_layout.addRow("언어:", self.subtitle_languages_label)
        
        form_layout.addRow("", subtitle_group)
        
        layout.addWidget(scroll)
    
    def _setup_series_info_tab(self):
        """시리즈 정보 탭 설정."""
        layout = QHBoxLayout(self.series_info_widget)
        
        # 왼쪽 패널 (포스터 및 기본 정보)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 포스터 이미지
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setFixedSize(225, 320)  # 일반적인 포스터 비율
        self.poster_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #d0d0d0;")
        self.poster_label.setText("포스터 없음")
        left_layout.addWidget(self.poster_label, alignment=Qt.AlignCenter)
        
        # 기본 정보 그룹
        basic_group = QGroupBox("기본 정보")
        basic_layout = QFormLayout(basic_group)
        
        self.anidb_id_edit = QLineEdit()
        self.anidb_id_edit.setReadOnly(True)
        basic_layout.addRow("AniDB ID:", self.anidb_id_edit)
        
        self.series_type_label = QLabel()
        basic_layout.addRow("유형:", self.series_type_label)
        
        self.series_episodes_label = QLabel()
        basic_layout.addRow("에피소드 수:", self.series_episodes_label)
        
        self.series_status_label = QLabel()
        basic_layout.addRow("상태:", self.series_status_label)
        
        self.series_year_label = QLabel()
        basic_layout.addRow("제작년도:", self.series_year_label)
        
        self.series_rating_label = QLabel()
        basic_layout.addRow("평점:", self.series_rating_label)
        
        left_layout.addWidget(basic_group)
        left_layout.addStretch()
        
        # 오른쪽 패널 (상세 정보)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 제목 정보 그룹
        title_group = QGroupBox("제목")
        title_layout = QFormLayout(title_group)
        
        self.series_title_edit = QLineEdit()
        title_layout.addRow("기본 제목:", self.series_title_edit)
        
        self.series_title_jp_edit = QLineEdit()
        title_layout.addRow("일본어:", self.series_title_jp_edit)
        
        self.series_title_kr_edit = QLineEdit()
        title_layout.addRow("한국어:", self.series_title_kr_edit)
        
        right_layout.addWidget(title_group)
        
        # 장르 및 태그 그룹
        genre_group = QGroupBox("장르 및 태그")
        genre_layout = QVBoxLayout(genre_group)
        
        self.series_genres_edit = QLineEdit()
        genre_layout.addWidget(QLabel("장르 (쉼표로 구분):"))
        genre_layout.addWidget(self.series_genres_edit)
        
        right_layout.addWidget(genre_group)
        
        # 줄거리 그룹
        plot_group = QGroupBox("줄거리")
        plot_layout = QVBoxLayout(plot_group)
        
        self.series_plot_edit = QTextEdit()
        self.series_plot_edit.setAcceptRichText(False)
        plot_layout.addWidget(self.series_plot_edit)
        
        right_layout.addWidget(plot_group)
        
        # 스플리터에 패널 추가
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
    
    def _setup_episode_info_tab(self):
        """에피소드 정보 탭 설정."""
        layout = QVBoxLayout(self.episode_info_widget)
        
        # 기본 정보 그룹
        basic_group = QGroupBox("에피소드 정보")
        basic_layout = QFormLayout(basic_group)
        
        self.episode_number_edit = QLineEdit()
        basic_layout.addRow("에피소드 번호:", self.episode_number_edit)
        
        self.episode_type_label = QLabel()
        basic_layout.addRow("유형:", self.episode_type_label)
        
        self.episode_air_date_label = QLabel()
        basic_layout.addRow("방영일:", self.episode_air_date_label)
        
        self.episode_duration_label = QLabel()
        basic_layout.addRow("재생 시간:", self.episode_duration_label)
        
        layout.addWidget(basic_group)
        
        # 제목 그룹
        title_group = QGroupBox("에피소드 제목")
        title_layout = QFormLayout(title_group)
        
        self.episode_title_edit = QLineEdit()
        title_layout.addRow("기본 제목:", self.episode_title_edit)
        
        self.episode_title_jp_edit = QLineEdit()
        title_layout.addRow("일본어:", self.episode_title_jp_edit)
        
        self.episode_title_kr_edit = QLineEdit()
        title_layout.addRow("한국어:", self.episode_title_kr_edit)
        
        layout.addWidget(title_group)
        
        # 줄거리 그룹
        plot_group = QGroupBox("에피소드 줄거리")
        plot_layout = QVBoxLayout(plot_group)
        
        self.episode_plot_edit = QTextEdit()
        self.episode_plot_edit.setAcceptRichText(False)
        plot_layout.addWidget(self.episode_plot_edit)
        
        layout.addWidget(plot_group)
        
        # 시청 기록 그룹
        history_group = QGroupBox("시청 기록")
        history_layout = QFormLayout(history_group)
        
        self.watch_count_label = QLabel("0")
        history_layout.addRow("시청 횟수:", self.watch_count_label)
        
        self.last_watched_label = QLabel("없음")
        history_layout.addRow("최근 시청:", self.last_watched_label)
        
        self.watch_progress_label = QLabel("0%")
        history_layout.addRow("시청 진행도:", self.watch_progress_label)
        
        layout.addWidget(history_group)
        
        layout.addStretch()
    
    def set_file_info(self, file_data):
        """
        파일 정보 설정.
        
        Args:
            file_data: 파일 정보 딕셔너리
        """
        if not file_data:
            return
        
        self._current_file_path = file_data.get('path', '')
        
        # 파일 기본 정보
        self.file_path_edit.setText(self._current_file_path)
        
        size_bytes = file_data.get('size', 0)
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        self.file_size_label.setText(size_str)
        self.file_ext_label.setText(file_data.get('extension', ''))
        self.ed2k_hash_edit.setText(file_data.get('ed2k_hash', ''))
        
        # 비디오 정보
        self.video_codec_label.setText(file_data.get('video_codec', '알 수 없음'))
        self.video_resolution_label.setText(file_data.get('resolution', '알 수 없음'))
        self.video_fps_label.setText(f"{file_data.get('fps', 0):.3f} fps" if file_data.get('fps') else '알 수 없음')
        
        duration = file_data.get('duration', 0)
        if duration:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            duration_str = '알 수 없음'
        
        self.video_duration_label.setText(duration_str)
        
        # 오디오 정보
        self.audio_codec_label.setText(file_data.get('audio_codec', '알 수 없음'))
        self.audio_channels_label.setText('알 수 없음')  # 추가 정보 필요
        self.audio_languages_label.setText(file_data.get('audio_languages', '알 수 없음'))
        
        # 자막 정보
        self.subtitle_languages_label.setText(file_data.get('subtitle_languages', '알 수 없음'))
    
    def set_series_info(self, series_data):
        """
        시리즈 정보 설정.
        
        Args:
            series_data: 시리즈 정보 딕셔너리
        """
        if not series_data:
            return
        
        # 기본 정보
        self.anidb_id_edit.setText(str(series_data.get('anidb_id', '')))
        self.series_type_label.setText(series_data.get('type', '알 수 없음'))
        self.series_episodes_label.setText(str(series_data.get('episodes_count', '알 수 없음')))
        self.series_status_label.setText(series_data.get('status', '알 수 없음'))
        
        # 시작 년도 표시
        start_date = series_data.get('start_date')
        if start_date:
            self.series_year_label.setText(str(start_date.year))
        else:
            self.series_year_label.setText('알 수 없음')
        
        # 평점 표시
        rating = series_data.get('rating')
        if rating:
            self.series_rating_label.setText(f"{rating:.1f}/10.0")
        else:
            self.series_rating_label.setText('평점 없음')
        
        # 제목 정보
        self.series_title_edit.setText(series_data.get('title', ''))
        self.series_title_jp_edit.setText(series_data.get('title_japanese', ''))
        self.series_title_kr_edit.setText(series_data.get('title_korean', ''))
        
        # 장르 및 줄거리
        self.series_genres_edit.setText(series_data.get('genres', ''))
        self.series_plot_edit.setPlainText(series_data.get('description', ''))
        
        # 포스터 이미지 (URL이 아닌 로컬 경로를 가정)
        poster_url = series_data.get('poster_url', '')
        if poster_url and os.path.exists(poster_url):
            pixmap = QPixmap(poster_url)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    self.poster_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.poster_label.setPixmap(pixmap)
                self.poster_label.setText("")
        else:
            self.poster_label.setText("포스터 없음")
            self.poster_label.setPixmap(QPixmap())
    
    def set_episode_info(self, episode_data):
        """
        에피소드 정보 설정.
        
        Args:
            episode_data: 에피소드 정보 딕셔너리
        """
        if not episode_data:
            return
        
        # 기본 정보
        self.episode_number_edit.setText(str(episode_data.get('number', '')))
        self.episode_type_label.setText(episode_data.get('type', '일반'))
        
        # 방영일 표시
        air_date = episode_data.get('air_date')
        if air_date:
            self.episode_air_date_label.setText(air_date.strftime('%Y-%m-%d'))
        else:
            self.episode_air_date_label.setText('알 수 없음')
        
        # 재생 시간 표시
        duration = episode_data.get('duration', 0)
        if duration:
            self.episode_duration_label.setText(f"{duration}분")
        else:
            self.episode_duration_label.setText('알 수 없음')
        
        # 제목 정보
        self.episode_title_edit.setText(episode_data.get('title', ''))
        self.episode_title_jp_edit.setText(episode_data.get('title_japanese', ''))
        self.episode_title_kr_edit.setText(episode_data.get('title_korean', ''))
        
        # 줄거리
        self.episode_plot_edit.setPlainText(episode_data.get('description', ''))
        
        # 시청 기록 정보 (추가 데이터 필요)
        watch_history = episode_data.get('watch_history', [])
        if watch_history:
            self.watch_count_label.setText(str(watch_history[0].get('play_count', 0)))
            
            watched_date = watch_history[0].get('watched_date')
            if watched_date:
                self.last_watched_label.setText(watched_date.strftime('%Y-%m-%d %H:%M'))
            else:
                self.last_watched_label.setText('없음')
            
            if watch_history[0].get('completed', False):
                self.watch_progress_label.setText("100%")
            else:
                position = watch_history[0].get('position', 0)
                full_duration = episode_data.get('duration', 0) * 60  # 분을 초로 변환
                if full_duration > 0:
                    progress = (position / full_duration) * 100
                    self.watch_progress_label.setText(f"{progress:.1f}%")
                else:
                    self.watch_progress_label.setText("0%")
        else:
            self.watch_count_label.setText("0")
            self.last_watched_label.setText("없음")
            self.watch_progress_label.setText("0%")
    
    def set_editable(self, editable):
        """
        편집 가능 상태 설정.
        
        Args:
            editable: 편집 가능 여부
        """
        self._editable = editable
        
        # 파일 정보 탭 (항상 읽기 전용)
        self.file_path_edit.setReadOnly(True)
        self.ed2k_hash_edit.setReadOnly(True)
        
        # 시리즈 정보 탭
        self.anidb_id_edit.setReadOnly(True)  # ID는 항상 읽기 전용
        self.series_title_edit.setReadOnly(not editable)
        self.series_title_jp_edit.setReadOnly(not editable)
        self.series_title_kr_edit.setReadOnly(not editable)
        self.series_genres_edit.setReadOnly(not editable)
        self.series_plot_edit.setReadOnly(not editable)
        
        # 에피소드 정보 탭
        self.episode_number_edit.setReadOnly(not editable)
        self.episode_title_edit.setReadOnly(not editable)
        self.episode_title_jp_edit.setReadOnly(not editable)
        self.episode_title_kr_edit.setReadOnly(not editable)
        self.episode_plot_edit.setReadOnly(not editable)
        
        # 버튼 상태 업데이트
        self.save_button.setEnabled(editable)
    
    def clear(self):
        """모든 필드 초기화."""
        # 파일 정보 탭
        self.file_path_edit.clear()
        self.file_size_label.clear()
        self.file_ext_label.clear()
        self.ed2k_hash_edit.clear()
        self.video_codec_label.clear()
        self.video_resolution_label.clear()
        self.video_fps_label.clear()
        self.video_duration_label.clear()
        self.audio_codec_label.clear()
        self.audio_channels_label.clear()
        self.audio_languages_label.clear()
        self.subtitle_languages_label.clear()
        
        # 시리즈 정보 탭
        self.anidb_id_edit.clear()
        self.series_type_label.clear()
        self.series_episodes_label.clear()
        self.series_status_label.clear()
        self.series_year_label.clear()
        self.series_rating_label.clear()
        self.series_title_edit.clear()
        self.series_title_jp_edit.clear()
        self.series_title_kr_edit.clear()
        self.series_genres_edit.clear()
        self.series_plot_edit.clear()
        self.poster_label.setText("포스터 없음")
        self.poster_label.setPixmap(QPixmap())
        
        # 에피소드 정보 탭
        self.episode_number_edit.clear()
        self.episode_type_label.clear()
        self.episode_air_date_label.clear()
        self.episode_duration_label.clear()
        self.episode_title_edit.clear()
        self.episode_title_jp_edit.clear()
        self.episode_title_kr_edit.clear()
        self.episode_plot_edit.clear()
        self.watch_count_label.setText("0")
        self.last_watched_label.setText("없음")
        self.watch_progress_label.setText("0%")
        
        self._current_file_path = None
    
    def _refresh_metadata(self):
        """메타데이터 새로고침."""
        if not self._current_file_path:
            return
        
        # 실제 구현에서는 파일 경로를 기반으로 메타데이터를 다시 가져오는 로직 구현
        # 여기서는 새로고침 메시지만 표시
        self.tab_widget.setTabText(0, "파일 정보 (새로고침 중...)")
        
        # TODO: 실제 메타데이터 새로고침 로직 구현
        
        # 일정 시간 후 탭 이름 복원 (실제 구현에서는 비동기 처리 후 호출)
        import time
        time.sleep(0.5)  # 이 부분은 실제 구현에서 제거하세요
        self.tab_widget.setTabText(0, "파일 정보")
    
    def _search_online(self):
        """온라인 메타데이터 검색."""
        if not self._current_file_path:
            return
        
        # 실제 구현에서는 온라인 검색 대화상자 표시 또는 검색 로직 구현
        # 여기서는 메시지만 표시
        self.tab_widget.setTabText(1, "시리즈 정보 (검색 중...)")
        
        # TODO: 실제 온라인 검색 로직 구현
        
        # 일정 시간 후 탭 이름 복원 (실제 구현에서는 비동기 처리 후 호출)
        import time
        time.sleep(0.5)  # 이 부분은 실제 구현에서 제거하세요
        self.tab_widget.setTabText(1, "시리즈 정보")
    
    def _save_changes(self):
        """변경사항 저장."""
        if not self._current_file_path or not self._editable:
            return
        
        # 변경된 메타데이터 수집
        series_data = {
            'title': self.series_title_edit.text(),
            'title_japanese': self.series_title_jp_edit.text(),
            'title_korean': self.series_title_kr_edit.text(),
            'genres': self.series_genres_edit.text(),
            'description': self.series_plot_edit.toPlainText()
        }
        
        episode_data = {
            'number': self.episode_number_edit.text(),
            'title': self.episode_title_edit.text(),
            'title_japanese': self.episode_title_jp_edit.text(),
            'title_korean': self.episode_title_kr_edit.text(),
            'description': self.episode_plot_edit.toPlainText()
        }
        
        # 변경 사항 알림
        metadata = {
            'file_path': self._current_file_path,
            'series': series_data,
            'episode': episode_data
        }
        
        self.metadata_updated.emit(metadata)
        
        # 저장 버튼 비활성화 (변경 사항이 저장되었음을 표시)
        self.save_button.setEnabled(False)
        
        # 일정 시간 후 다시 활성화 (실제 구현에서는 적절한 시점에 활성화)
        import time
        time.sleep(0.5)  # 이 부분은 실제 구현에서 제거하세요
        self.save_button.setEnabled(self._editable)