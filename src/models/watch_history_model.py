#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
시청 기록 모델 클래스를 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models.database import Base


class WatchHistory(Base):
    """사용자의 애니메이션 시청 기록을 저장하는 모델."""
    
    __tablename__ = 'watch_history'
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'), nullable=False)
    
    # 시청 정보
    watched_date = Column(DateTime, default=datetime.now)  # 시청 날짜
    position = Column(Integer, default=0)  # 마지막 시청 위치 (초)
    completed = Column(Boolean, default=False)  # 시청 완료 여부
    
    # 사용자 상호작용
    rating = Column(Integer)  # 사용자 평점 (1-10)
    notes = Column(Text)  # 메모
    
    # 재생 횟수
    play_count = Column(Integer, default=1)  # 총 재생 횟수
    
    # 시스템 정보
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    episode = relationship("Episode", back_populates="watch_history")
    
    def __init__(self, episode_id, **kwargs):
        """
        시청 기록 모델 초기화.
        
        Args:
            episode_id: 에피소드 ID
            **kwargs: 추가 속성
        """
        self.episode_id = episode_id
        
        # 추가 속성 설정
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """모델 문자열 표현."""
        return f"<WatchHistory(id={self.id}, episode_id={self.episode_id}, watched_date={self.watched_date})>"
        
    def update_position(self, position, duration=None):
        """
        시청 위치를 업데이트하고 필요시 완료 상태를 갱신합니다.
        
        Args:
            position: 현재 시청 위치 (초)
            duration: 총 재생 시간 (초), 제공되면 완료 여부 판단에 사용
        """
        self.position = position
        self.updated_date = datetime.now()
        
        # 총 길이의 90% 이상 시청했으면 완료로 표시
        if duration and position >= duration * 0.9:
            self.completed = True
            
    def increment_play_count(self):
        """재생 횟수를 증가시킵니다."""
        self.play_count += 1
        self.updated_date = datetime.now() 