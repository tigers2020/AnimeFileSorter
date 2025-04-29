아래는 AnimeFileSorter 프로젝트를 Python 3.12, MVC/SRP 원칙에 맞춰 완전 리팩토링하고, 모던한 GUI 및 추가 기능을 단계별로 구성하기 위한 제안 로드맵입니다.

---

## 1. 아키텍처 재설계  
- **Model**  
  - Pydantic 기반 데이터 모델 (`MediaItem`, `Series`, `Episode`, `Movie` 등)  
  - 파일 메타데이터(파일명, 크기, 해시), 외부 API 응답 스키마 분리  
- **View**  
  - 프론트엔드: React + TypeScript + Tailwind CSS + daisyUI + Headless UI  
    - Atomic Design(Methodology) 적용 (atoms, molecules, organisms, templates)  
    - Sidebar 내비게이션, 검색/필터 컴포넌트, 카드형 결과물 UI  
  - 또는 PySide6 + QML  
    - Qt Quick Controls 2를 이용한 모던 테마  
    - MVC 패턴에 맞춰 View 전용 모듈 분리  
- **Controller**  
  - FastAPI 서버 (or Flask)  
    - CRUD 엔드포인트(API): 파일 스캔, 메타데이터 조회, 리네이밍, 태그 관리 등  
    - 의존성 주입(DI)으로 SRP 보장: 각 서비스(`ScannerService`, `MetadataService`, `RenameService` 등) 분리  
- **Service / Repository**  
  - 파일 시스템 접근, 데이터베이스(SQLite/Postgres), 외부 API 통신을 담당하는 계층  

## 2. 핵심 기능 확장 제안  
1. **파일 관리**  
   - 대시보드: 디렉토리 상태, 처리 현황  
   - 일괄 스캔·분류(카테고리, 시리즈별 폴더 구조 자동 생성)  
   - 중복 파일 검출 및 정리(해시 기반)  
2. **메타데이터 연동**  
   - AniList·TMDB·IMDb API 연동 → 제목, 줄거리, 포스터, 방영/개봉일 자동 불러오기  
   - 사용자 정의 템플릿에 따른 파일명 일괄 리네이밍  
3. **검색·필터·태깅**  
   - 다중 조건 필터(장르, 제작년도, 평점 등)  
   - 즐겨찾기·보고싶어요 목록  
4. **자막 관리**  
   - OpenSubtitles API 연동 → 자막 다운로드·동기화  
   - 자막 내장화 옵션  
5. **플러그인 시스템**  
   - 추가 기능(예: Plex 서버 등록, 토렌트 검색) 쉽게 확장 가능  
6. **알림·로그**  
   - 작업 완료·오류 알림(데스크탑 알림, 이메일)  
   - 로그 레벨별 파일 저장 및 UI 출력  

## 3. 개발 환경 및 도구  
- **언어/런타임**: Python 3.12, Node 18+ / npm  
- **패키징/배포**: Poetry, GitHub Actions(CI: lint, type-check, 테스트)  
- **테스트**: pytest, FastAPI TestClient, React Testing Library  
- **코딩 표준**: black, isort, mypy(strict)  
- **문서화**: MkDocs + Material for MkDocs, API 문서 자동화(OpenAPI)  

## 4. GUI 구현 옵션 비교  
| 옵션                   | 장점                                              | 단점                         |
|----------------------|-------------------------------------------------|----------------------------|
| React + Tauri        | 최신 웹 UI, 풍부한 컴포넌트, 크로스플랫폼, 경량 배포 가능     | 초기 셋업 복잡                 |
| PySide6 + QML        | 네이티브 성능, Qt 생태계 활용, 꾸준한 유지보수            | UI 커스터마이징 시 Web만큼 자유롭지 않음 |

> **선호 방식**을 알려주시면 세부 설계·예제 코드 포함하여 진행 계획을 구체화하겠습니다.

---

위 로드맵을 바탕으로,  
1. 우선 프로젝트 구조(폴더·모듈) 설계  
2. 핵심 서비스 및 데이터 모델 구현  
3. UI 프로토타입 개발  
4. 기능별 단계적 통합 및 테스트  

순으로 진행할 것을 권장드립니다.  
추가로 반영하고 싶은 기능이나 선호 GUI 스택이 있다면 알려주세요.