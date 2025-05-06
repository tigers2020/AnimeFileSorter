#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애니메이션 에피소드 모델 클래스를 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models.database import Base


class Episode(Base):
    """애니메이션 에피소드 정보를 저장하는 모델."""
    
    __tablename__ = 'episodes'
    
    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id'), nullable=False)
    
    # 외부 ID
    anidb_episode_id = Column(Integer, unique=True)  # AniDB 에피소드 ID
    
    # 에피소드 기본 정보
    number = Column(Integer, nullable=False)  # 에피소드 번호
    type = Column(String(20))  # 일반, SP(스페셜), OP(오프닝), ED(엔딩) 등
    title = Column(String(512))  # 에피소드 제목
    title_japanese = Column(String(512))
    title_korean = Column(String(512))
    
    # 방영 정보
    air_date = Column(DateTime)  # 방영일
    duration = Column(Integer)  # 길이 (분)
    
    # 컨텐츠 정보
    description = Column(Text)  # 줄거리
    rating = Column(Float)  # 평점 (10점 만점)
    
    # 이미지/리소스
    thumbnail_url = Column(String(1024))  # 썸네일 URL
    
    # 시스템 정보
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    series = relationship("Series", back_populates="episodes")
    files = relationship("AnimeFile", back_populates="episode", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="episode", cascade="all, delete-orphan")
    
    def __init__(self, series_id, number, **kwargs):
        """
        애니메이션 에피소드 모델 초기화.
        
        Args:
            series_id: 시리즈 ID
            number: 에피소드 번호
            **kwargs: 추가 속성
        """
        self.series_id = series_id
        self.number = number
        
        # 추가 속성 설정
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """모델 문자열 표현."""
        return f"<Episode(id={self.id}, series_id={self.series_id}, number={self.number})>" 