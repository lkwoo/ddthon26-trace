# UOW-01 (스캐너 & 파서) — Logical Components

**단계**: CONSTRUCTION / NFR Design (UOW-01)
**작성일**: 2026-09-09

> 논리 컴포넌트(모듈)의 책임·의존·시그니처를 확정한다. Code Generation의 파일 청사진.

---

## 모듈 배치
```text
trace/
├── models/
│   └── asset.py            # [신설] Asset, AssetType, ParseStatus
├── config/
│   └── scan_settings.py    # [신설] ScanSettings, get_scan_settings()  (또는 settings.py에 추가)
└── engine/                 # [신설 패키지] C2 (스캔 구간)
    ├── __init__.py
    ├── scanner.py          # 순회·제외·경로검증·크기/실패 관리
    ├── classifier.py       # classify(path, root) -> AssetType
    ├── parsers.py          # 파서 레지스트리 + 유형별 텍스트 추출
    └── scan.py             # scan_project / scan_project_assets 진입점
tests/
├── test_scanner_scan.py        # [신설] 예제 기반 단위 테스트(demo/ 대상 포함)
├── test_classifier.py          # [신설] 분류 규칙 단위 테스트
└── test_scanner_properties.py  # [신설] PBT 4속성(hypothesis)
```

## 컴포넌트 책임 & 시그니처

### models/asset.py
```python
class AssetType(str, Enum): SOURCE="source"; OPENAPI="openapi"; SQL="sql";
    CONFIG="config"; TEST="test"; MARKDOWN="markdown"; PDF="pdf"; TEXT="text"
class ParseStatus(str, Enum): PARSED="parsed"; PARTIAL="partial"; SKIPPED="skipped"; FAILED="failed"
class Asset(BaseModel):
    rel_path: str; filename: str; asset_type: AssetType; parse_status: ParseStatus
    size_bytes: int; content: str | None = None; truncated: bool = False; error: str | None = None
    def to_meta(self) -> dict  # data.assets용(content 제외, Q5=A)
```
- **의존**: pydantic(기존). EvidenceType과 값 정렬(하위 매핑).

### config/scan_settings.py
```python
class ScanSettings(BaseModel):
    max_file_bytes: int = 5_000_000
    max_total_bytes: int = 200_000_000
def get_scan_settings() -> ScanSettings   # env override 지점(기존 config 패턴)
```
- **의존**: 없음(상수/env).

### engine/classifier.py
```python
def classify(rel_path: str, filename: str) -> AssetType        # BR-CLASSIFY, 순수 함수
def _is_test(rel_path, filename) -> bool
def _looks_like_openapi(text_or_doc) -> bool                   # BR-CLASSIFY-003
```
- **의존**: PyYAML/json(openapi 판별 시), models/asset.

### engine/parsers.py
```python
_PARSERS: dict[AssetType, Callable[[Path,int], ParseResult]]   # 레지스트리(P3)
def parse_asset(path: Path, atype: AssetType, size: int, settings) -> ParseResult
def _parse_text(...)   # utf-8→latin-1
def _parse_pdf(...)    # pypdf, 페이지별
# ParseResult = (content|None, ParseStatus, truncated, error, warnings)
```
- **의존**: pypdf(런타임 승격), models/asset, config/scan_settings.

### engine/scanner.py
```python
def validate_root(path: str) -> Path                           # P1, raises PathValidationError
def walk_files(root: Path, exclusions: set[str]) -> Iterator[Path]  # P2, followlinks=False
def is_within_root(candidate: Path, root: Path) -> bool        # P1 트래버설
def is_binary(path: Path) -> bool                              # BR-EXCLUDE-002
```
- **의존**: config.get_exclusions()(UOW-0F), common/errors, common/logging.

### engine/scan.py (진입점)
```python
def scan_project_assets(path: str) -> tuple[list[Asset], list[Warning]]   # 내부 API(content 포함)
def scan_project(path: str) -> Result                                     # 공개(메타만, Q5=A)
```
- **의존**: 위 모듈 전부 + UOW-0F `Result`/`Warning`/`build_result`.
- **오케스트레이션 골격**: `analyze_project`는 이후 UOW-02+에서 이 `scan_project_assets`를 호출하도록
  훅만 남긴다(이번 단위에서는 scan 구간만 실구현).

## 의존성 방향 (순환 없음)
```text
scan.py → scanner.py → config(get_exclusions)
scan.py → parsers.py → pypdf, config(scan_settings)
scan.py → classifier.py → PyYAML/json
scan.py → models/asset, models/result(UOW-0F), common/*
```
- 모두 UOW-0F(leaf)와 표준/서드파티에만 의존. 상위(UOW-02+)는 scan.py를 소비만 함.

## 테스트 배치 (검증 정합)
| 테스트 | 커버 |
|---|---|
| test_classifier.py | BR-CLASSIFY(확장자/test/openapi 판별) 예제 |
| test_scanner_scan.py | demo/ 스캔 → 6종 유형·PDF parsed·failed 0·결정적 순서; 무효경로 오류 Result |
| test_scanner_properties.py | PBT-01-A/B/C/D (hypothesis) |

## 산출물 변경(Code Generation 예정)
- `pyproject.toml`: `pypdf>=4.0`를 [project.dependencies]로 이동(런타임 승격).
