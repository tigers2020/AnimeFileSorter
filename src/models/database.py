#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스 연결 및 세션 관리를 담당하는 모듈입니다.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


# ORM 기본 클래스 정의
Base = declarative_base()

# 기본 경로 설정 - 사용자 홈 디렉토리 내 .animefilesorter 폴더
default_db_path = Path.home() / '.animefilesorter' / 'anime_files.db'
os.makedirs(default_db_path.parent, exist_ok=True)

# 엔진 생성
engine = create_engine(f"sqlite:///{default_db_path}", echo=False)

# 세션 팩토리 생성
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """
    데이터베이스 스키마를 초기화합니다.
    """
    # 모델 가져오기
    from src.models.file_model import AnimeFile
    from src.models.series_model import Series
    from src.models.episode_model import Episode
    from src.models.watch_history_model import WatchHistory
    
    # 모든 모델 테이블 생성
    Base.metadata.create_all(engine)


def get_session():
    """
    데이터베이스 세션을 반환합니다.
    
    Returns:
        SQLAlchemy 세션 객체
    """
    return Session()


def close_session():
    """
    현재 스레드의 세션을 닫습니다.
    """
    Session.remove()


def reset_db():
    """
    데이터베이스를 초기화합니다. 주의: 모든 데이터가 삭제됩니다.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine) 