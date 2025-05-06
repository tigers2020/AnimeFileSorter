#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLAlchemy 모델을 분석하여 ERD 다이어그램을 생성하는 스크립트입니다.
이 스크립트는 sadisplay 라이브러리를 사용합니다.
"""

import os
import sys
from pathlib import Path
import argparse
import importlib

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 인자 파서 설정
parser = argparse.ArgumentParser(description='SQLAlchemy 모델의 ERD 다이어그램 생성')
parser.add_argument('--format', choices=['dot', 'png', 'svg'], default='png',
                    help='출력 파일 형식 (기본값: png)')
parser.add_argument('--output', default='docs/database_erd',
                    help='출력 파일 경로 (확장자 제외, 기본값: docs/database_erd)')
args = parser.parse_args()

# 모델 가져오기
from src.models import Base, AnimeFile, Series, Episode, WatchHistory

try:
    import sadisplay
except ImportError:
    print("sadisplay 라이브러리가 필요합니다. 다음 명령으로 설치하세요:")
    print("pip install sadisplay")
    sys.exit(1)

# 출력 디렉토리 생성
output_dir = Path(args.output).parent
os.makedirs(output_dir, exist_ok=True)

# 모델 목록
models = [AnimeFile, Series, Episode, WatchHistory]
model_names = [model.__name__ for model in models]

print(f"ERD 생성 중: {', '.join(model_names)}")

# ERD 설명 생성
desc = sadisplay.describe(models)

# DOT 파일 생성
if args.format in ('dot', 'png', 'svg'):
    dot_file = f"{args.output}.dot"
    with open(dot_file, 'w') as f:
        f.write(sadisplay.dot(desc))
    print(f"DOT 파일 생성 완료: {dot_file}")

# 이미지 파일 생성
if args.format in ('png', 'svg'):
    try:
        import subprocess
        output_file = f"{args.output}.{args.format}"
        subprocess.run(['dot', '-T' + args.format, dot_file, '-o', output_file], check=True)
        print(f"{args.format.upper()} 파일 생성 완료: {output_file}")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"이미지 변환 실패: {e}")
        print("이미지 생성을 위해 GraphViz가 필요합니다. 설치 후 다시 시도하세요.")
        print("- Windows: https://graphviz.org/download/")
        print("- macOS: brew install graphviz")
        print("- Ubuntu/Debian: apt-get install graphviz")

print("ERD 생성 완료!") 