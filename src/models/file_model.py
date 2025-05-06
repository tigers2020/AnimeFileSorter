#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애니메이션 파일 모델 클래스를 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models.database import Base


class AnimeFile(Base):
    """애니메이션 파일 정보를 저장하는 모델."""
    
    __tablename__ = 'anime_files'
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'))  # 에피소드 연결
    path = Column(String(1024), unique=True, nullable=False)
    filename = Column(String(512), nullable=False)
    directory = Column(String(1024), nullable=False)
    
    # 파일 속성
    size = Column(Integer, nullable=False)  # 파일 크기 (바이트)
    extension = Column(String(20), nullable=False)
    ed2k_hash = Column(String(32))  # ED2K 해시
    crc32 = Column(String(8))  # CRC32 체크섬
    md5 = Column(String(32))  # MD5 해시
    
    # 비디오 속성
    video_codec = Column(String(50))  # 비디오 코덱
    audio_codec = Column(String(50))  # 오디오 코덱
    resolution = Column(String(20))  # 해상도 (예: 1080p, 720p)
    duration = Column(Float)  # 영상 길이 (초)
    fps = Column(Float)  # 프레임 레이트
    
    # 자막 정보
    subtitle_languages = Column(String(255))  # 포함된 자막 언어 목록
    audio_languages = Column(String(255))  # 포함된 오디오 언어 목록
    
    # 시간 정보
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime)
    last_checked = Column(DateTime, default=datetime.now)
    
    # 메타데이터
    anime_title = Column(String(512))
    episode_number = Column(Integer)
    anime_year = Column(Integer)
    source = Column(String(50))  # 출처 (TV, BD, DVD 등)
    
    # 상태 정보
    is_verified = Column(Boolean, default=False)
    tags = Column(Text)  # 쉼표로 구분된 태그 목록
    notes = Column(Text)
    
    # 관계
    episode = relationship("Episode", back_populates="files")
    
    def __init__(self, path, filename, directory, size, extension, modified_date=None, **kwargs):
        """
        애니메이션 파일 모델 초기화.
        
        Args:
            path: 파일 전체 경로
            filename: 파일 이름
            directory: 디렉토리 경로
            size: 파일 크기
            extension: 파일 확장자
            modified_date: 파일 수정 날짜
            **kwargs: 추가 속성
        """
        self.path = path
        self.filename = filename
        self.directory = directory
        self.size = size
        self.extension = extension
        self.modified_date = modified_date or datetime.now()
        
        # 추가 속성 설정
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """모델 문자열 표현."""
        return f"<AnimeFile(id={self.id}, filename='{self.filename}')>"
        
    def update_media_info(self, video_codec=None, audio_codec=None, resolution=None, 
                         duration=None, fps=None, subtitle_langs=None, audio_langs=None):
        """
        미디어 정보를 업데이트합니다.
        
        Args:
            video_codec: 비디오 코덱
            audio_codec: 오디오 코덱
            resolution: 해상도
            duration: 재생 시간
            fps: 프레임 레이트
            subtitle_langs: 자막 언어 목록
            audio_langs: 오디오 언어 목록
        """
        if video_codec:
            self.video_codec = video_codec
        if audio_codec:
            self.audio_codec = audio_codec
        if resolution:
            self.resolution = resolution
        if duration:
            self.duration = duration
        if fps:
            self.fps = fps
        if subtitle_langs:
            self.subtitle_languages = ','.join(subtitle_langs) if isinstance(subtitle_langs, list) else subtitle_langs
        if audio_langs:
            self.audio_languages = ','.join(audio_langs) if isinstance(audio_langs, list) else audio_langs
        
        self.last_checked = datetime.now() 