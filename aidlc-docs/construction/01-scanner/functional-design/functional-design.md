# UOW-01 스캐너 & 파서 — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: unit-of-work.md(UOW-01), components.md(C2), services.md(S1 스캔 단계), 요구사항 §5·§6
**스토리**: US-01.1(로컬 로딩), US-01.2(자산 탐색·분류), US-01.3(제외 규칙)
**의존**: UOW-0F (Result, Config)

## 1. 도메인 (`trace/engine/assets.py`)

- `Asset(path, abspath, type, filename, parse_status, content, error)` — 발견된 분석 대상 1개.
- 유형: source/markdown/text/pdf/openapi/sql/config/test/unknown.

## 2. 비즈니스 로직

- **`scan_project(path) -> Result`** (코어 함수): 재귀 스캔 → 제외 → 분류 → 파싱 → 요약.
  data: `{project_name, project_path, assets[요약], counts_by_type}`.
- **`collect_assets(path, config) -> (assets, warnings)`**: 파싱된 Asset(콘텐츠 포함) — 파이프라인 소비용(UOW-02).
- 파서(`parsers.py`): text 계열은 utf-8(errors=replace), **PDF는 pypdf**(P0). 파일 상한 2MB.

## 3. 비즈니스 규칙

1. **경로 검증**(NFR-SEC-004): 미존재/비디렉터리 → `Result.error`(사람이 읽는 오류), 예외 누출 없음.
2. **제외 규칙**(FR-PROJECT-003): 경로 파트에 제외어(.git/node_modules/target/.trace…) 포함 시 스킵.
3. **부분 실패 허용**(FR-ANALYSIS-003): 개별 파싱 실패 → parse_status="error" + warning, 전체 계속.
4. **OpenAPI 판별**: .yaml/.yml/.json 은 콘텐츠 스니핑(`openapi:`/`swagger:`)으로 openapi vs config 구분.
5. **테스트 판별**: 경로(test/tests) 또는 파일명(test_*/*_test/*Tests) 규칙.

## 4. 확장 준수

- **PBT**: 분류 함수 무크래시(임의 확장자), 경로 검증 오류 처리 속성 테스트.
- **Resiliency**: 부분 실패·사용자 친화 오류·warning 누적(RESILIENCY-05 관측성 = 로깅).

## 5. 검증

- `tests/test_engine_scanner.py` 9개 통과: 분류/제외/경로검증/부분실패 + **실제 demo 스캔**
  (source·sql·openapi·test·pdf 전 범주 발견, PDF 파싱 성공).
