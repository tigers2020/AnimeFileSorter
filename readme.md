# Anime File Sorter

애니메이션 미디어 파일을 정리하고 관리하는 애플리케이션입니다.

## 기능

- 애니메이션 파일 자동 스캔
- 메타데이터 추출 및 관리
- 태깅 및 분류 기능
- 사용자 친화적인 UI

## 설치 방법

### 필수 요구 사항

- Python 3.9 이상
- Qt 라이브러리 (PyQt6)
- SQLite 데이터베이스

### 설치

1. 저장소 복제:
   ```
   git clone https://github.com/yourusername/anime-file-sorter.git
   cd anime-file-sorter
   ```

2. 가상 환경 생성 및 활성화:
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 의존성 설치:
   ```
   pip install -r requirements.txt
   ```

4. 개발 모드로 설치:
   ```
   pip install -e .
   ```

## 사용 방법

애플리케이션을 실행하는 방법:

```
python -m anime_file_sorter
```

또는 설치 후:

```
anime-file-sorter
```

## 개발 가이드

### 디렉토리 구조

```
anime-file-sorter/
├── src/
│   └── anime_file_sorter/
│       ├── core/        # 코어 비즈니스 로직
│       ├── db/          # 데이터베이스 모듈
│       ├── ui/          # 사용자 인터페이스
│       └── utils/       # 유틸리티 함수
├── tests/
│   ├── unit/            # 단위 테스트
│   └── integration/     # 통합 테스트
├── docs/                # 문서
├── setup.py             # 패키지 설정
└── requirements.txt     # 의존성 관리
```

### 테스트 실행

테스트를 실행하는 방법:

```
pytest
```

## 라이선스

MIT License

## AniDB API 접근 문제 해결 방법

현재 프로젝트에서 AniDB UDP API 연결 시 "505 - ILLEGAL_INPUT_OR_ACCESS_DENIED" 오류가 발생할 수 있습니다. 이는 다음과 같은 원인들이 있을 수 있습니다:

1. **API 정책 제한**: AniDB는 API에 대한 엄격한 정책을 갖고 있으며, 공식적으로 등록되지 않은 클라이언트는 접근이 제한될 수 있습니다.

2. **클라이언트 정보**: 현재 다음 클라이언트 설정을 사용하고 있습니다:
   - UDP 클라이언트: `animerenamerpython`
   - UDP 클라이언트 버전: 3
   - API 버전: 3

3. **요청 제한**: AniDB는 요청 속도를 제한하며, 특히 AUTH 명령은 30초 간격을 유지해야 합니다.

4. **명령 형식 제약**: 2025-05-06 업데이트 - AUTH 명령의 형식을 수정했습니다. 공백으로 태그 분리 대신 파라미터 형식으로 변경하고, 불필요한 파라미터(`enc=UTF-8`)를 제거했습니다.

### 해결 방법

1. **개발 모드 사용**:
   현재 코드는 AniDB 연결 실패 시 개발 모드로 전환됩니다. 따라서 API 접근 없이도 애플리케이션의 기본 기능을 테스트할 수 있습니다.

2. **클라이언트 등록**:
   프로젝트를 공개적으로 배포할 계획이 있다면, AniDB에 클라이언트를 등록해야 합니다:
   - [AniDB Wiki - Client Registration](https://wiki.anidb.net/UDP_Clients)

3. **대체 API 사용**:
   UDP API 접근이 계속 문제가 된다면, 아래 대안을 고려할 수 있습니다:
   - HTTP API (이미 일부 구현됨)
   - 다른 애니메이션 메타데이터 API (예: TheTVDB, AniList 등)
   - 로컬 메타데이터 처리

4. **설정 조정**:
   다음 설정을 추가로 조정할 수 있습니다:
   - `src/api/anime_service.py`: 재시도 횟수, 대기 시간, 타임아웃 증가
   - `src/api/anidb_client.py`: 요청 간격 (현재 AUTH 30초, 일반 명령 4초)

## 개발 중 테스트 방법

AniDB API 접속 문제가 해결될 때까지, 다음과 같이 테스트를 진행할 수 있습니다:

1. **애플리케이션 실행**: `python main.py`
2. **로그인 시도**: 로그인 창에서 아무 ID/비밀번호나 입력 (개발 모드로 전환됨)
3. **파일 선택 및 해시 계산**: 애니메이션 파일 선택 후 해시 계산
4. **파일 식별**: 식별 버튼을 클릭하면 개발 모드에서 테스트 데이터가 생성됨

## AniDB API 문서

- [UDP API 문서](https://wiki.anidb.net/UDP_API_Definition)
- [HTTP API 문서](https://wiki.anidb.net/HTTP_API_Definition)

## 버전 정보

- 버전: 0.1.0-dev
- 마지막 업데이트: 2025-05-06
