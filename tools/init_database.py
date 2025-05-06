#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스를 초기화하고 기본 데이터를 삽입하는 스크립트입니다.
"""

import os
import sys
from pathlib import Path
import argparse
import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 모델 가져오기
from src.models import Base, AnimeFile, Series, Episode, WatchHistory
from src.models.database import init_db, reset_db, get_session, close_session

# 인자 파서 설정
parser = argparse.ArgumentParser(description='AnimeFileSorter 데이터베이스 초기화')
parser.add_argument('--reset', action='store_true',
                    help='기존 데이터베이스 초기화 (주의: 모든 데이터가 삭제됩니다)')
parser.add_argument('--sample-data', action='store_true',
                    help='샘플 데이터 추가')
args = parser.parse_args()

# 데이터베이스 초기화
if args.reset:
    print("데이터베이스를 초기화합니다...")
    reset_db()
    print("데이터베이스 초기화 완료!")
else:
    print("데이터베이스 스키마를 생성합니다...")
    init_db()
    print("데이터베이스 스키마 생성 완료!")

# 샘플 데이터 추가
if args.sample_data:
    print("샘플 데이터를 추가합니다...")
    session = get_session()
    
    try:
        # 샘플 시리즈 추가
        series1 = Series(
            title="나루토",
            title_korean="나루토",
            title_japanese="ナルト",
            anidb_id=239,
            type="TV",
            episodes_count=220,
            status="완료",
            start_date=datetime.datetime(2002, 10, 3),
            end_date=datetime.datetime(2007, 2, 8),
            genres="액션,모험,코미디,슈퍼파워",
            description="12년 전, 아홉 개의 꼬리를 가진 여우 괴물 '구미'가 나뭇잎 마을을 공격했다. 마을의 지도자 4대 호카게는 자신의 생명을 희생해 이 괴물을 갓 태어난 아기 나루토의 몸에 봉인했다. 고아가 된 나루토는 마을 사람들의 증오와 냉대 속에 외롭게 자랐지만, 호카게가 되겠다는 꿈을 키우며 닌자로서의 훈련을 시작한다.",
            rating=7.8,
            age_rating="12세",
            poster_url="https://cdn.anidb.net/images/main/224460.jpg"
        )
        
        series2 = Series(
            title="원피스",
            title_korean="원피스",
            title_japanese="ワンピース",
            anidb_id=69,
            type="TV",
            episodes_count=1000,
            status="방영 중",
            start_date=datetime.datetime(1999, 10, 20),
            genres="액션,모험,코미디,판타지",
            description="해적왕 골드 로저가 남긴 전설의 보물 '원피스'를 찾기 위해 밀짚모자 해적단의 선장 몽키 D. 루피와 그의 동료들이 거대한 바다를 모험하는 이야기.",
            rating=8.2,
            age_rating="12세",
            poster_url="https://cdn.anidb.net/images/main/235575.jpg"
        )
        
        session.add_all([series1, series2])
        session.flush()  # ID 할당을 위해 플러시
        
        # 샘플 에피소드 추가
        episodes = []
        
        # 나루토 에피소드
        for i in range(1, 6):
            episode = Episode(
                series_id=series1.id,
                number=i,
                type="일반",
                title=f"에피소드 {i}",
                title_korean=f"나루토 {i}화",
                air_date=datetime.datetime(2002, 10, 3) + datetime.timedelta(days=i*7),
                duration=24,
                description=f"나루토 시리즈의 {i}번째 에피소드입니다."
            )
            episodes.append(episode)
        
        # 원피스 에피소드
        for i in range(1, 6):
            episode = Episode(
                series_id=series2.id,
                number=i,
                type="일반",
                title=f"Episode {i}",
                title_korean=f"원피스 {i}화",
                air_date=datetime.datetime(1999, 10, 20) + datetime.timedelta(days=i*7),
                duration=24,
                description=f"원피스 시리즈의 {i}번째 에피소드입니다."
            )
            episodes.append(episode)
        
        session.add_all(episodes)
        session.flush()
        
        # 샘플 파일 추가
        files = []
        
        for i, episode in enumerate(episodes):
            # 각 에피소드마다 파일 추가
            file = AnimeFile(
                path=f"/anime/{episode.series.title}/Season 1/{episode.series.title} - S01E{episode.number:02d}.mkv",
                filename=f"{episode.series.title} - S01E{episode.number:02d}.mkv",
                directory=f"/anime/{episode.series.title}/Season 1",
                size=1500000000 + (i * 100000000),  # 크기 변경
                extension="mkv",
                episode_id=episode.id,
                video_codec="H.264",
                audio_codec="AAC",
                resolution="1080p",
                duration=episode.duration * 60,  # 분을 초로 변환
                fps=23.976,
                subtitle_languages="ko,en,ja",
                audio_languages="ja,en",
                modified_date=datetime.datetime.now() - datetime.timedelta(days=i),
                anime_title=episode.series.title,
                episode_number=episode.number,
                anime_year=episode.series.start_date.year if episode.series.start_date else None,
                source="BD",
                is_verified=True
            )
            files.append(file)
        
        session.add_all(files)
        session.flush()
        
        # 샘플 시청 기록 추가
        watch_history = []
        
        for i, episode in enumerate(episodes[:5]):  # 처음 5개 에피소드만
            history = WatchHistory(
                episode_id=episode.id,
                watched_date=datetime.datetime.now() - datetime.timedelta(days=10-i),
                position=episode.duration * 60,  # 완료된 상태
                completed=True,
                rating=8 + (i % 3),  # 8-10 사이 평점
                play_count=1 + (i % 3)  # 1-3 사이 재생 횟수
            )
            watch_history.append(history)
        
        session.add_all(watch_history)
        
        # 변경사항 커밋
        session.commit()
        print(f"샘플 데이터 추가 완료: 시리즈 {len([series1, series2])}개, 에피소드 {len(episodes)}개, 파일 {len(files)}개, 시청기록 {len(watch_history)}개")
    
    except Exception as e:
        session.rollback()
        print(f"샘플 데이터 추가 실패: {e}")
    
    finally:
        close_session()

print("데이터베이스 초기화 스크립트 완료!") 