#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter의 핵심 모듈 패키지입니다.
이 패키지는 애니메이션 파일 처리와 관련된 핵심 기능을 포함합니다.
"""

__version__ = "0.1.0"

from src.core.file_utils import (
    calculate_ed2k_hash, 
    calculate_ed2k_hash_parallel,
    get_file_info,
    ED2K_CHUNK_SIZE
)

__all__ = [
    'calculate_ed2k_hash',
    'calculate_ed2k_hash_parallel',
    'get_file_info',
    'ED2K_CHUNK_SIZE'
] 