# AnimeFileSorter

애니메이션 파일을 자동으로 스캔하고 정리해주는 유틸리티입니다.

## 기능

- 디렉토리 스캔 및 미디어 파일 탐색
- 파일명에서 시리즈/영화 정보 추출
- 원본 파일명을 유지하며 폴더 구조 생성
- 설정 저장 및 관리 (SQLite 데이터베이스 사용)
- 명령줄 인터페이스 (CLI)

## 설치 방법

### 필수 요구사항

- Python 3.6 이상
- SQLite3

### 설치 과정

```bash
git clone https://github.com/username/AnimeFileSorter.git
cd AnimeFileSorter
pip install -r requirements.txt
```

## 사용 방법

### 기본 명령어

```bash
python main.py <입력_디렉토리> <출력_디렉토리> [옵션]
```

### 옵션

- `--preview`, `-p`: 미리보기 모드 (실제 파일 작업 없음)
- `--operation`, `-o`: 파일 작업 유형 지정 (`COPY` 또는 `MOVE`)
- `--recursive`, `-r`: 하위 디렉토리까지 재귀적으로 스캔
- `--preserve-filename`: 원본 파일명 유지 (기본값: 유지)
- `--show-settings`: 현재 설정 표시 후 종료
- `--reset-settings`: 설정을 기본값으로 초기화

### 예제

```bash
# 기본 사용법
python main.py D:\Downloads\Anime E:\Media\Organized

# 미리보기 모드
python main.py D:\Downloads\Anime E:\Media\Organized --preview

# 파일 이동 모드
python main.py D:\Downloads\Anime E:\Media\Organized --operation MOVE

# 설정 보기
python main.py --show-settings

# 설정 초기화
python main.py --reset-settings
```

## 폴더 구조

정리된 파일은 다음과 같은 폴더 구조로 저장됩니다:

```
<출력_디렉토리>/
├── Series/
│   ├── <시리즈명>/
│   │   ├── Season 01/
│   │   │   ├── <원본_파일명>.mkv
│   │   │   └── <원본_자막_파일명>.srt
│   │   └── Season 02/
│   │       └── ...
│   └── <다른_시리즈>/
│       └── ...
├── Movies/
│   ├── <영화_제목> (연도)/
│   │   ├── <원본_파일명>.mkv
│   │   └── <원본_자막_파일명>.srt
│   └── ...
└── Unsorted/
    └── <분류할_수_없는_파일>.mkv
```

## 설정 옵션

다음 설정들을 변경할 수 있습니다:

| 설정 | 설명 | 기본값 |
|------|------|--------|
| operation_type | 파일 작업 유형 | COPY |
| preserve_original_filename | 원본 파일명 유지 | True |
| create_series_folders | 시리즈 폴더 생성 | True |
| create_season_folders | 시즌 폴더 생성 | True |
| scan_recursive | 하위 디렉토리 포함 스캔 | True |
| move_subtitles | 자막 파일도 함께 이동 | True |
| organize_by_type | 시리즈와 영화 분리 | True |

## 라이선스

MIT

## 기여 방법

이슈나 PR을 통해 기여해주세요.
