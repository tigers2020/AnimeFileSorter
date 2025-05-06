#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AniDB API와 통신하기 위한 클라이언트 모듈입니다.
UDP 및 HTTP API를 모두 지원합니다.
"""

import os
import time
import socket
import hashlib
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlencode, quote
import requests

# 로거 설정
logger = logging.getLogger(__name__)


class AniDBUDPClient:
    """
    AniDB UDP API 클라이언트 클래스.
    
    AniDB UDP API 문서: https://wiki.anidb.net/UDP_API_Definition
    """
    
    # API 상수
    DEFAULT_SERVER = "api.anidb.net"
    DEFAULT_PORT = 9000
    API_VERSION = 3
    
    # 응답 코드
    RESPONSE_CODES = {
        # 정상 응답
        200: "OK",
        201: "CREATED",
        202: "ACCEPTED",
        203: "NOT_AUTHORITATIVE",
        204: "NO_CONTENT",
        205: "RESET_CONTENT",
        206: "PARTIAL_CONTENT",
        
        # 클라이언트 오류
        500: "ILLEGAL_INPUT_OR_ACCESS_DENIED",
        501: "BANNED",
        502: "SERVER_BUSY",
        503: "TIMEOUT",
        504: "INVALID_SESSION",
        505: "ILLEGAL_INPUT_OR_ACCESS_DENIED",
        506: "INVALID_SESSION",
        509: "ENCODING_NOT_SUPPORTED",
        519: "NO_SUCH_FILE",
        555: "BANNED",
        598: "UNKNOWN_COMMAND",
        600: "INTERNAL_SERVER_ERROR",
        601: "ANIDB_OUT_OF_SERVICE",
        602: "SERVER_BUSY",
        666: "API_VIOLATION",
    }
    
    def __init__(
        self, 
        client_name: str, 
        client_version: int, 
        server: str = DEFAULT_SERVER, 
        port: int = DEFAULT_PORT,
        local_port: int = 0,
        session_keep_alive: bool = True,
        retry_count: int = 2,
        retry_wait: int = 5,
        timeout: int = 20
    ):
        """
        AniDB UDP 클라이언트 초기화.
        
        Args:
            client_name: API 접근용 클라이언트 이름 (등록된 이름이어야 함)
            client_version: 클라이언트 버전
            server: AniDB API 서버 주소
            port: AniDB API 서버 포트
            local_port: 로컬 포트 (0이면 시스템이 자동 할당)
            session_keep_alive: 세션 유지 활성화 여부
            retry_count: 통신 실패 시 재시도 횟수
            retry_wait: 재시도 간 대기 시간 (초)
            timeout: 소켓 타임아웃 (초)
        """
        self.client_name = client_name
        self.client_version = client_version
        self.server = server
        self.port = port
        self.local_port = local_port
        
        self.socket = None
        self.session = None
        self.last_command_time = 0
        self.session_keep_alive = session_keep_alive
        
        self.retry_count = retry_count
        self.retry_wait = retry_wait
        self.timeout = timeout
        
        self.logged_in = False
        self.handle = None  # 사용자 핸들
        self.tag = 0  # 요청 태그
        
    def _connect(self) -> None:
        """소켓 연결 초기화."""
        if self.socket:
            self.socket.close()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.local_port))
        self.socket.settimeout(self.timeout)
    
    def _disconnect(self) -> None:
        """소켓 연결 종료."""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def _new_tag(self) -> str:
        """
        새로운 요청 태그 생성.
        
        Returns:
            요청 태그
        """
        self.tag = (self.tag + 1) % 100000
        return str(self.tag)
    
    def _send_receive(self, command: str) -> Tuple[int, str]:
        """
        명령 전송 및 응답 수신.
        
        Args:
            command: 전송할 명령
            
        Returns:
            (응답 코드, 응답 데이터) 튜플
        """
        # 속도 제한을 위한 대기 (AniDB 정책: 최소 30초 간격으로 AUTH 요청)
        current_time = time.time()
        time_since_last = current_time - self.last_command_time
        
        # AUTH 명령은 더 긴 간격 적용 (30초), 다른 명령은 4초
        is_auth_cmd = command.startswith("AUTH ")
        min_interval = 30 if is_auth_cmd else 4
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"AniDB 속도 제한: {wait_time:.1f}초 대기 중...")
            time.sleep(wait_time)
        
        if not self.socket:
            self._connect()
        
        # 재시도 로직
        for attempt in range(self.retry_count + 1):
            try:
                command_bytes = command.encode('utf-8')
                # 민감한 정보 로깅 방지
                if command.startswith("AUTH "):
                    logger.debug("AniDB 전송: AUTH [인증 정보 생략]")
                else:
                    logger.debug(f"AniDB 전송: {command}")
                
                self.socket.sendto(command_bytes, (self.server, self.port))
                data, addr = self.socket.recvfrom(1400)  # UDP 패킷 크기
                
                self.last_command_time = time.time()
                data_str = data.decode('utf-8')
                
                # 응답 분석
                code, response = self._parse_response(data_str)
                
                if 200 <= code < 300:  # 성공
                    return code, response
                elif code in [501, 506]:  # 재인증 필요
                    self.logged_in = False
                    self.session = None
                    if attempt < self.retry_count:
                        logger.warning(f"재인증 필요: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
                        time.sleep(self.retry_wait)  # 재시도 전 대기 추가
                        continue
                elif code == 555:  # BANNED - 재시도하지 않음
                    logger.error(f"AniDB 차단됨 (IP BAN): {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
                    return code, response
                elif code in [500, 502, 503, 504, 505]:  # 재시도 가능한 오류 (505는 첫 시도 외에만 재시도)
                    if attempt < self.retry_count and (code != 505 or attempt > 0):
                        wait_time = self.retry_wait * (2 ** attempt)  # 지수 백오프
                        logger.warning(f"재시도: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')} (대기: {wait_time}초)")
                        time.sleep(wait_time)
                        continue
                
                # 치명적인 오류 또는 재시도 횟수 초과
                logger.error(f"AniDB 오류: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
                return code, response
            
            except socket.timeout:
                logger.warning(f"AniDB 타임아웃 발생 (시도 {attempt+1}/{self.retry_count+1})")
                if attempt >= self.retry_count:
                    return 503, "Timeout"  # 타임아웃 오류
            
            except Exception as e:
                logger.error(f"AniDB 통신 오류: {e}")
                return 600, str(e)  # 내부 오류
        
        return 503, "Maximum retries exceeded"
    
    def _parse_response(self, response: str) -> Tuple[int, str]:
        """
        API 응답 파싱.
        
        Args:
            response: API 응답 문자열
            
        Returns:
            (응답 코드, 응답 데이터) 튜플
        """
        parts = response.strip().split(' ', 1)
        code = int(parts[0])
        
        if len(parts) > 1:
            return code, parts[1]
        else:
            return code, ""
    
    def ping(self) -> bool:
        """
        서버 연결 확인 (PING).
        
        Returns:
            성공 여부
        """
        # PING 명령은 태그가 공백으로 분리됨 (공식 문서 참조)
        command = f"PING {self._new_tag()}"
        logger.debug("AniDB 서버 연결 확인 중...")
        code, _ = self._send_receive(command)
        success = 200 <= code < 300
        if success:
            logger.debug("AniDB 서버 연결 확인 성공")
        else:
            logger.warning(f"AniDB 서버 연결 확인 실패: {code}")
        return success
    
    def login(self, username: str, password: str) -> bool:
        """
        AniDB 로그인.
        
        Args:
            username: 사용자 이름
            password: 비밀번호
            
        Returns:
            로그인 성공 여부
        """
        if self.logged_in:
            return True
            
        # 먼저 서버 연결 확인
        if not self.ping():
            logger.error("AniDB 서버 연결 실패. 로그인을 시도할 수 없습니다.")
            return False
        
        # 비밀번호 해시 계산
        passhash = hashlib.md5(password.encode()).hexdigest()
        
        # 로그인 명령 구성 - 잘못된 형식 수정
        params = (
            f"user={username}&pass={passhash}"
            f"&protover={self.API_VERSION}&client={self.client_name}"
            f"&clientver={self.client_version}&nat=1&comp=1"
            # 태그는 선택적으로 파라미터로 추가 가능
            # f"&tag={self._new_tag()}"
        )
        command = f"AUTH {params}"
        
        code, response = self._send_receive(command)
        
        if 200 <= code < 300:
            response_parts = response.split(' ')
            self.session = response_parts[0]
            if len(response_parts) > 1:
                self.handle = response_parts[1]
            self.logged_in = True
            logger.info(f"AniDB 로그인 성공: {username}")
            return True
        else:
            logger.error(f"AniDB 로그인 실패: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
            return False
    
    def logout(self) -> bool:
        """
        AniDB 로그아웃.
        
        Returns:
            로그아웃 성공 여부
        """
        if not self.logged_in:
            return True
        
        command = f"LOGOUT {self._new_tag()}"
        code, _ = self._send_receive(command)
        
        if 200 <= code < 300:
            self.logged_in = False
            self.session = None
            self.handle = None
            self._disconnect()
            logger.info("AniDB 로그아웃 성공")
            return True
        else:
            logger.error(f"AniDB 로그아웃 실패: {code}")
            return False
    
    def get_file_info(self, size: int, ed2k_hash: str) -> Optional[Dict[str, Any]]:
        """
        파일 정보 조회.
        
        Args:
            size: 파일 크기 (바이트)
            ed2k_hash: ED2K 해시
            
        Returns:
            파일 정보 딕셔너리 또는 None
        """
        if not self.logged_in:
            logger.error("AniDB에 로그인되어 있지 않습니다.")
            return None
        
        command = f"FILE {self._new_tag()} size={size}&ed2k={ed2k_hash}&fmask=7FF8FEF8&amask=F2FCF0F0"
        code, response = self._send_receive(command)
        
        if code == 220:  # 파일 정보 응답
            parts = response.split('|')
            headers = [
                "fid", "aid", "eid", "gid", "lid", "status", "size", "ed2k", "md5", "sha1", "crc32",
                "video_color_depth", "quality", "source", "audio_langs", "subtitle_langs", "dub_langs",
                "length", "description", "aired", "filename", "type", "group_name", "group_short",
                "video_resolution", "video_codec", "audio_codec", "audio_bitrate", "video_bitrate",
                "censored", "version", "ep_english", "ep_romaji", "ep_kanji", "ep_number", "ep_name",
                "ep_total", "anime_english", "anime_romaji", "anime_kanji", "anime_year", "anime_type",
                "category", "reserved", "date_added"
            ]
            
            data = {}
            for i, value in enumerate(parts):
                if i < len(headers):
                    data[headers[i]] = value if value != "" else None
            
            return data
        else:
            logger.error(f"파일 정보 조회 실패: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
            return None
    
    def get_anime_info(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """
        애니메이션 정보 조회.
        
        Args:
            anime_id: 애니메이션 ID
            
        Returns:
            애니메이션 정보 딕셔너리 또는 None
        """
        if not self.logged_in:
            logger.error("AniDB에 로그인되어 있지 않습니다.")
            return None
        
        command = f"ANIME {self._new_tag()} aid={anime_id}&amask=F2FCF0F0"
        code, response = self._send_receive(command)
        
        if code == 230:  # 애니메이션 정보 응답
            parts = response.split('|')
            headers = [
                "aid", "dateflags", "year", "type", "related_aid_list", "related_aid_type",
                "romaji", "kanji", "english", "other", "short_names", "synonyms", "category",
                "episodes", "special_ep_count", "air_date", "end_date", "url", "picname", "category_list",
                "rating", "vote_count", "temp_rating", "temp_vote_count", "average_review_rating",
                "review_count", "award_list", "is_18_restricted", "anime_planet_id", "ANN_id",
                "allcinema_id", "AnimeNfo_id", "tag_name_list", "tag_id_list", "tag_weight_list",
                "date_record_updated", "character_id_list", "creator_id_list", "creator_name_list",
                "creator_type_list", "main_creator_id_list", "main_creator_name_list", "main_creator_type_list"
            ]
            
            data = {}
            for i, value in enumerate(parts):
                if i < len(headers):
                    data[headers[i]] = value if value != "" else None
            
            return data
        else:
            logger.error(f"애니메이션 정보 조회 실패: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
            return None
    
    def get_episode_info(self, episode_id: int) -> Optional[Dict[str, Any]]:
        """
        에피소드 정보 조회.
        
        Args:
            episode_id: 에피소드 ID
            
        Returns:
            에피소드 정보 딕셔너리 또는 None
        """
        if not self.logged_in:
            logger.error("AniDB에 로그인되어 있지 않습니다.")
            return None
        
        command = f"EPISODE {self._new_tag()} eid={episode_id}"
        code, response = self._send_receive(command)
        
        if code == 240:  # 에피소드 정보 응답
            parts = response.split('|')
            headers = [
                "eid", "aid", "length", "rating", "votes", "english", "romaji", "kanji", "aired", "type"
            ]
            
            data = {}
            for i, value in enumerate(parts):
                if i < len(headers):
                    data[headers[i]] = value if value != "" else None
            
            return data
        else:
            logger.error(f"에피소드 정보 조회 실패: {code} - {self.RESPONSE_CODES.get(code, 'Unknown')}")
            return None
    
    def close(self) -> None:
        """클라이언트 세션 종료."""
        if self.logged_in:
            self.logout()
        self._disconnect()


class AniDBHTTPClient:
    """
    AniDB HTTP API 클라이언트 클래스.
    주로 이미지 및 XML 데이터 검색에 사용됩니다.
    
    AniDB HTTP API 문서: https://wiki.anidb.net/HTTP_API_Definition
    """
    
    # API 상수
    BASE_URL = "http://api.anidb.net"
    HTTP_CLIENT_NAME = "animerenamerpython"
    CLIENT_VERSION = 3
    
    def __init__(self, client_name: str, client_version: int, cache_dir: Optional[str] = None):
        """
        AniDB HTTP 클라이언트 초기화.
        
        Args:
            client_name: API 접근용 클라이언트 이름 (등록된 이름이어야 함)
            client_version: 클라이언트 버전
            cache_dir: 캐시 디렉토리 경로 (None이면 사용자 홈/.animefilesorter/cache)
        """
        self.client_name = client_name
        self.client_version = client_version
        
        if cache_dir is None:
            cache_dir = str(Path.home() / '.animefilesorter' / 'cache' / 'anidb')
        
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 캐시 하위 디렉토리 생성
        self.poster_cache_dir = os.path.join(self.cache_dir, 'posters')
        self.xml_cache_dir = os.path.join(self.cache_dir, 'xml')
        os.makedirs(self.poster_cache_dir, exist_ok=True)
        os.makedirs(self.xml_cache_dir, exist_ok=True)
        
        # 세션 생성
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{client_name}/{client_version}',
        })
        
        # 요청 간격 제어를 위한 타임스탬프
        self.last_request_time = 0
    
    def _request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        HTTP 요청 전송.
        
        Args:
            url: 요청 URL
            params: URL 파라미터
            
        Returns:
            HTTP 응답 객체
        """
        # 속도 제한을 위한 대기
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 2:  # 최소 2초 간격으로 요청
            time.sleep(2 - time_since_last)
        
        response = self.session.get(url, params=params)
        self.last_request_time = time.time()
        
        return response
    
    def get_anime_xml(self, anime_id: int, force_refresh: bool = False) -> Optional[ET.ElementTree]:
        """
        애니메이션 XML 데이터 조회.
        
        Args:
            anime_id: 애니메이션 ID
            force_refresh: 강제로 캐시 갱신 여부
            
        Returns:
            XML ElementTree 객체 또는 None
        """
        cache_file = os.path.join(self.xml_cache_dir, f'anime_{anime_id}.xml')
        
        # 캐시된 데이터 확인
        if not force_refresh and os.path.exists(cache_file):
            # 캐시 파일이 일주일 이내면 사용
            if time.time() - os.path.getmtime(cache_file) < 7 * 24 * 60 * 60:
                try:
                    tree = ET.parse(cache_file)
                    return tree
                except ET.ParseError:
                    logger.warning(f"캐시된 XML 파싱 실패: {cache_file}")
        
        # 새 데이터 요청
        params = {
            'client': self.client_name,
            'clientver': self.client_version,
            'request': 'anime',
            'aid': anime_id
        }
        
        url = f"{self.BASE_URL}/httpapi"
        
        try:
            response = self._request(url, params)
            if response.status_code == 200:
                # XML 응답 확인
                content = response.text
                if not content.strip().startswith('<?xml'):
                    logger.error(f"XML 응답이 아닙니다: {content[:100]}")
                    return None
                
                # 캐시에 저장
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # XML 파싱
                try:
                    tree = ET.ElementTree(ET.fromstring(content))
                    return tree
                except ET.ParseError as e:
                    logger.error(f"XML 파싱 오류: {e}")
                    return None
            else:
                logger.error(f"HTTP API 오류: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"애니메이션 XML 조회 중 오류 발생: {e}")
            return None
    
    def get_anime_title(self, anime_id: int, preferred_lang: str = 'ko') -> Optional[str]:
        """
        애니메이션 타이틀 조회.
        
        Args:
            anime_id: 애니메이션 ID
            preferred_lang: 선호하는 언어 코드 (ko, en, ja, x-jat)
            
        Returns:
            애니메이션 제목 또는 None
        """
        tree = self.get_anime_xml(anime_id)
        if tree is None:
            return None
        
        root = tree.getroot()
        anime = root.find('anime')
        if anime is None:
            return None
        
        # 타이틀 요소에서 선호 언어 검색
        titles = anime.findall('titles/title')
        
        # 선호 언어로 타이틀 찾기
        for title in titles:
            lang = title.get('xml:lang') or title.get('lang')
            if lang == preferred_lang:
                return title.text
        
        # 선호 언어 없으면 영어 > 로마자 > 일본어 > 아무 언어 순으로 선택
        langs = ['en', 'x-jat', 'ja']
        for lang in langs:
            for title in titles:
                title_lang = title.get('xml:lang') or title.get('lang')
                if title_lang == lang:
                    return title.text
        
        # 그래도 없으면 첫 번째 타이틀 반환
        if titles:
            return titles[0].text
        
        return None
    
    def get_poster_url(self, anime_id: int) -> Optional[str]:
        """
        애니메이션 포스터 URL 조회.
        
        Args:
            anime_id: 애니메이션 ID
            
        Returns:
            포스터 URL 또는 None
        """
        tree = self.get_anime_xml(anime_id)
        if tree is None:
            return None
        
        root = tree.getroot()
        anime = root.find('anime')
        if anime is None:
            return None
        
        picture = anime.find('picture')
        if picture is not None and picture.text:
            return f"https://cdn.anidb.net/images/main/{picture.text}"
        
        return None
    
    def download_poster(self, anime_id: int, force_refresh: bool = False) -> Optional[str]:
        """
        애니메이션 포스터 다운로드.
        
        Args:
            anime_id: 애니메이션 ID
            force_refresh: 강제로 캐시 갱신 여부
            
        Returns:
            로컬 이미지 파일 경로 또는 None
        """
        cache_file = os.path.join(self.poster_cache_dir, f'anime_{anime_id}.jpg')
        
        # 캐시된 이미지 확인
        if not force_refresh and os.path.exists(cache_file):
            return cache_file
        
        # 포스터 URL 조회
        poster_url = self.get_poster_url(anime_id)
        if not poster_url:
            logger.warning(f"애니메이션 {anime_id}의 포스터를 찾을 수 없습니다.")
            return None
        
        # 이미지 다운로드
        try:
            response = self._request(poster_url)
            if response.status_code == 200:
                with open(cache_file, 'wb') as f:
                    f.write(response.content)
                return cache_file
            else:
                logger.error(f"포스터 다운로드 실패: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"포스터 다운로드 중 오류 발생: {e}")
            return None
    
    def search_anime(self, query: str) -> List[Dict[str, Any]]:
        """
        애니메이션 검색. (참고: HTTP API는 직접 검색을 지원하지 않으므로
        UDP API 또는 외부 서비스를 사용해야 할 수 있습니다. 이 구현은 예시입니다.)
        
        Args:
            query: 검색어
            
        Returns:
            검색 결과 목록
        """
        # 실제 AniDB HTTP API에는 이러한 검색 기능이 없습니다.
        # 실제 구현에서는 UDP API 또는 웹 스크래핑을 사용해야 합니다.
        logger.warning("AniDB HTTP API는 직접 검색을 지원하지 않습니다.")
        return []
    
    def close(self) -> None:
        """HTTP 세션 종료."""
        self.session.close() 