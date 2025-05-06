#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
애니메이션 시리즈 모델 클래스를 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models.database import Base


class Series(Base):
    """애니메이션 시리즈 정보를 저장하는 모델."""
    
    __tablename__ = 'series'
    
    id = Column(Integer, primary_key=True)
    anidb_id = Column(Integer, unique=True)  # AniDB ID
    
    # 기본 정보
    title = Column(String(512), nullable=False)  # 주 제목 (영어/로마자)
    title_japanese = Column(String(512))  # 일본어 제목
    title_korean = Column(String(512))  # 한국어 제목
    synonyms = Column(Text)  # 다른 이름들 (JSON 형식)
    
    # 시리즈 메타데이터
    type = Column(String(50))  # TV, 영화, OVA 등
    episodes_count = Column(Integer, default=0)  # 총 에피소드 수
    status = Column(String(50))  # 방영 중, 완료, 예정 등
    start_date = Column(DateTime)  # 시작 방영일
    end_date = Column(DateTime)  # 종료 방영일
    
    # 컨텐츠 정보
    genres = Column(Text)  # 장르 (JSON 형식)
    description = Column(Text)  # 줄거리
    rating = Column(Float)  # 평점 (10점 만점)
    age_rating = Column(String(20))  # 시청 연령 (전체, 12세, 15세, 19세 등)
    
    # 이미지/리소스
    poster_url = Column(String(1024))  # 포스터 URL
    banner_url = Column(String(1024))  # 배너 이미지 URL
    
    # 시스템 정보
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_checked = Column(DateTime, default=datetime.now)  # 메타데이터 확인 시간
    
    # 관계
    episodes = relationship("Episode", back_populates="series", cascade="all, delete-orphan")
    
    def __init__(self, title, **kwargs):
        """
        애니메이션 시리즈 모델 초기화.
        
        Args:
            title: 시리즈 제목
            **kwargs: 추가 속성
        """
        self.title = title
        
        # 추가 속성 설정
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """모델 문자열 표현."""
        return f"<Series(id={self.id}, title='{self.title}')>" 