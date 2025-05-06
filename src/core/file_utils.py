#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
파일 처리와 관련된 유틸리티 함수들을 제공합니다.
"""

import os
import hashlib
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple, BinaryIO

# 상수 정의
ED2K_CHUNK_SIZE = 9728000  # 9.28MB (AniDB에서 사용하는 크기)
MD4_DIGEST_LENGTH = 16  # MD4 다이제스트 길이 (바이트)


def is_video_file(file_path: str) -> bool:
    """
    주어진 파일이 비디오 파일인지 확인합니다.
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        비디오 파일이면 True, 아니면 False
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in video_extensions


def scan_directory(directory_path: str, recursive: bool = True) -> List[str]:
    """
    지정된 디렉토리에서 비디오 파일을 스캔합니다.
    
    Args:
        directory_path: 스캔할 디렉토리 경로
        recursive: 하위 디렉토리까지 재귀적으로 스캔할지 여부
        
    Returns:
        비디오 파일 경로 목록
    """
    video_files = []
    
    if recursive:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_video_file(file_path):
                    video_files.append(file_path)
    else:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path) and is_video_file(file_path):
                video_files.append(file_path)
    
    return video_files


def calculate_ed2k_hash(file_path: str, callback: Optional[Callable[[int, int], None]] = None) -> str:
    """
    파일의 ED2K 해시값을 계산합니다.
    
    Args:
        file_path: 파일 경로
        callback: 진행 상황 콜백 함수 (현재 바이트, 전체 바이트)
        
    Returns:
        ED2K 해시값 (16진수 문자열)
        
    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
        PermissionError: 파일 접근 권한이 없을 경우
        IOError: 파일 읽기 오류 발생시
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    file_size = os.path.getsize(file_path)
    
    # 빈 파일인 경우 특수 처리
    if file_size == 0:
        return "31d6cfe0d16ae931b73c59d7e0c089c0"
    
    with open(file_path, 'rb') as f:
        return _calculate_ed2k_from_fileobj(f, file_size, callback)


def _calculate_ed2k_from_fileobj(f: BinaryIO, file_size: int, 
                                callback: Optional[Callable[[int, int], None]] = None) -> str:
    """
    파일 객체로부터 ED2K 해시값을 계산합니다.
    
    Args:
        f: 파일 객체
        file_size: 파일 크기
        callback: 진행 상황 콜백 함수
        
    Returns:
        ED2K 해시값 (16진수 문자열)
    """
    chunks = []
    bytes_read = 0
    
    # 청크별로 파일 읽기
    while True:
        chunk = f.read(ED2K_CHUNK_SIZE)
        if not chunk:
            break
        
        bytes_read += len(chunk)
        if callback:
            callback(bytes_read, file_size)
        
        # 청크 해시 계산 (MD4)
        md4_hash = hashlib.new('md4')
        md4_hash.update(chunk)
        chunks.append(md4_hash.digest())
    
    # 파일이 하나의 청크보다 작은 경우
    if len(chunks) == 1:
        return chunks[0].hex()
    
    # 청크가 여러 개인 경우 메타 해시 계산
    md4_hash = hashlib.new('md4')
    for chunk_hash in chunks:
        md4_hash.update(chunk_hash)
    
    return md4_hash.hexdigest()


def calculate_ed2k_hash_parallel(file_path: str, 
                                num_threads: int = 4, 
                                callback: Optional[Callable[[int, int], None]] = None) -> str:
    """
    멀티스레딩을 사용하여 파일의 ED2K 해시값을 계산합니다.
    
    Args:
        file_path: 파일 경로
        num_threads: 사용할 스레드 수
        callback: 진행 상황 콜백 함수 (현재 바이트, 전체 바이트)
        
    Returns:
        ED2K 해시값 (16진수 문자열)
        
    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
        PermissionError: 파일 접근 권한이 없을 경우
        IOError: 파일 읽기 오류 발생시
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    file_size = os.path.getsize(file_path)
    
    # 빈 파일인 경우 특수 처리
    if file_size == 0:
        return "31d6cfe0d16ae931b73c59d7e0c089c0"
    
    # 단일 청크 파일은 병렬 계산 의미가 없음
    if file_size <= ED2K_CHUNK_SIZE:
        return calculate_ed2k_hash(file_path, callback)
    
    # 각 스레드별 청크 범위 계산
    chunk_count = (file_size + ED2K_CHUNK_SIZE - 1) // ED2K_CHUNK_SIZE
    chunk_ranges = _split_chunks_for_threads(chunk_count, num_threads)
    
    completed_bytes = 0
    chunk_hashes = []
    
    # 병렬 처리를 위한 ThreadPoolExecutor 사용
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 청크 범위별로 태스크 제출
        futures = {
            executor.submit(
                _calculate_chunks, 
                file_path, 
                start_chunk, 
                end_chunk,
                lambda bytes_read: _update_progress(callback, bytes_read, file_size, completed_bytes)
            ): (start_chunk, end_chunk) 
            for start_chunk, end_chunk in chunk_ranges
        }
        
        # 결과 수집
        for future in concurrent.futures.as_completed(futures):
            start_chunk, end_chunk = futures[future]
            try:
                result = future.result()
                # 계산된 청크의 바이트 수 추가
                completed_bytes += min(ED2K_CHUNK_SIZE * (end_chunk - start_chunk), 
                                     file_size - (start_chunk * ED2K_CHUNK_SIZE))
                
                # 결과 저장
                for i, chunk_hash in enumerate(result):
                    chunk_index = start_chunk + i
                    while len(chunk_hashes) <= chunk_index:
                        chunk_hashes.append(None)
                    chunk_hashes[chunk_index] = chunk_hash
            
            except Exception as e:
                raise IOError(f"파일 {file_path}의 청크 {start_chunk}-{end_chunk} 처리 중 오류 발생: {e}")
    
    # 누락된 청크가 있는지 확인
    if None in chunk_hashes or len(chunk_hashes) != chunk_count:
        raise IOError(f"파일 {file_path}의 일부 청크가 처리되지 않았습니다.")
    
    # 메타 해시 계산
    md4_hash = hashlib.new('md4')
    for chunk_hash in chunk_hashes:
        md4_hash.update(chunk_hash)
    
    return md4_hash.hexdigest()


def _split_chunks_for_threads(chunk_count: int, num_threads: int) -> List[Tuple[int, int]]:
    """
    청크를 여러 스레드에 분배하기 위한 범위를 계산합니다.
    
    Args:
        chunk_count: 총 청크 수
        num_threads: 스레드 수
        
    Returns:
        각 스레드가 처리할 청크 범위 목록 [(시작 청크, 끝 청크), ...]
    """
    chunks_per_thread = max(1, chunk_count // num_threads)
    ranges = []
    
    for i in range(num_threads):
        start_chunk = i * chunks_per_thread
        if start_chunk >= chunk_count:
            break
        
        end_chunk = min((i + 1) * chunks_per_thread, chunk_count)
        ranges.append((start_chunk, end_chunk))
    
    return ranges


def _calculate_chunks(file_path: str, start_chunk: int, end_chunk: int,
                     progress_callback: Optional[Callable[[int], None]] = None) -> List[bytes]:
    """
    파일의 특정 청크 범위에 대한 MD4 해시를 계산합니다.
    
    Args:
        file_path: 파일 경로
        start_chunk: 시작 청크 인덱스
        end_chunk: 끝 청크 인덱스 (미포함)
        progress_callback: 진행 상황 콜백 함수
    
    Returns:
        청크 해시 목록
    """
    chunk_hashes = []
    
    with open(file_path, 'rb') as f:
        # 시작 위치로 이동
        f.seek(start_chunk * ED2K_CHUNK_SIZE)
        
        # 할당된 청크 계산
        for _ in range(end_chunk - start_chunk):
            chunk = f.read(ED2K_CHUNK_SIZE)
            if not chunk:
                break
            
            # 청크 해시 계산
            md4_hash = hashlib.new('md4')
            md4_hash.update(chunk)
            chunk_hashes.append(md4_hash.digest())
            
            if progress_callback:
                progress_callback(len(chunk))
    
    return chunk_hashes


def _update_progress(callback: Optional[Callable[[int, int], None]], 
                    bytes_read: int, file_size: int, base_bytes: int) -> None:
    """
    진행 상황 콜백 도우미 함수입니다.
    
    Args:
        callback: 원본 콜백 함수
        bytes_read: 현재 스레드에서 읽은 바이트 수
        file_size: 총 파일 크기
        base_bytes: 이미 처리된 바이트 수
    """
    if callback:
        callback(base_bytes + bytes_read, file_size)


def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    파일의 기본 메타데이터를 수집합니다.
    
    Args:
        file_path: 메타데이터를 수집할 파일 경로
        
    Returns:
        파일 메타데이터를 포함하는 딕셔너리
    """
    file_stat = os.stat(file_path)
    file_path_obj = Path(file_path)
    
    return {
        'path': file_path,
        'name': file_path_obj.name,
        'size': file_stat.st_size,
        'created_time': file_stat.st_ctime,
        'modified_time': file_stat.st_mtime,
        'extension': file_path_obj.suffix.lower(),
        'directory': str(file_path_obj.parent)
    }


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    파일의 기본 정보를 반환합니다.
    
    Args:
        file_path: 파일 경로
        
    Returns:
        파일 정보 딕셔너리
    """
    path = Path(file_path)
    
    return {
        'path': str(path.absolute()),
        'filename': path.name,
        'directory': str(path.parent.absolute()),
        'size': path.stat().st_size if path.exists() else 0,
        'extension': path.suffix.lower().lstrip('.'),
        'modified_date': path.stat().st_mtime if path.exists() else None
    } 