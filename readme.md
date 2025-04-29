# AnimeFileSorter

PySide6로 개발된 모던한 아니메 파일 관리 및 정리 도구입니다.

## 주요 기능

- 비디오 파일 스캔 및 자동 분류
- 시리즈/영화/OVA 등 다양한 미디어 타입 지원
- 메타데이터 기반 지능형 파일명 정리
- 중복 파일 검출 및 관리
- 자막 파일 자동 연결
- 외부 API (TMDB, AniList) 연동
- 사용자 정의 파일명 템플릿

## 설치 방법

### 요구 사항

- Python 3.12 이상
- Poetry (의존성 관리)

### 설치 과정

```bash
# 저장소 클론
git clone https://github.com/yourusername/animefilesorter.git
cd animefilesorter

# Poetry로 의존성 설치
poetry install

# 실행
poetry run animefilesorter
```

### Poetry 없이 설치

```bash
pip install -r requirements.txt
python -m src.main
```

## 사용 방법

1. 프로그램 실행 후 상단 메뉴에서 폴더 스캔 또는 파일 정리 탭 이동
2. 정리할 비디오 파일이 있는 폴더 선택
3. 스캔 후 파일 목록 확인
4. 정리 버튼을 눌러 파일 정리 시작
5. 정리 진행 상황 모니터링

## 개발 환경 설정

```bash
# 개발 의존성 포함 설치
poetry install --with dev

# 테스트 실행
poetry run pytest

# 린트 검사
poetry run black src tests
poetry run isort src tests
poetry run mypy src
```

## 프로젝트 구조

```
animefilesorter/
├── docs/                     # 문서화
├── src/
│   ├── models/               # 데이터 모델
│   ├── views/                # GUI 관련
│   ├── controllers/          # 컨트롤러
│   ├── services/             # 비즈니스 로직
│   ├── repositories/         # 외부 데이터 접근
│   ├── utils/                # 유틸리티 기능
│   └── main.py               # 애플리케이션 시작점
├── tests/                    # 테스트
├── config/                   # 설정 파일
└── pyproject.toml            # 프로젝트 메타데이터
```

## 기여하기

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add some feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 라이선스

MIT 라이선스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
