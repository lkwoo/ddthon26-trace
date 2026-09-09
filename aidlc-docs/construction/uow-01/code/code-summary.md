# UOW-01 (스캐너 & 파서) — Code Generation 요약

**단계**: CONSTRUCTION / Code Generation (UOW-01) Part 2
**작성일**: 2026-09-09
**결과**: `pytest` **70 passed**(기존 43 + UOW-01 27), Python 3.11.9(.venv). UOW-01 신규 모듈 mypy-clean.

## 생성/수정 파일
### 애플리케이션 코드
| 파일 | 내용 |
|---|---|
| `trace/models/asset.py` | AssetType(EvidenceType 정렬)·ParseStatus·Asset(+to_meta content 제외, Q5=A) |
| `trace/config/scan_settings.py` | ScanSettings(5MB/200MB) + get_scan_settings(env override) |
| `trace/common/errors.py` | `sanitize_error()` 추가(P5, 절대경로·시크릿·트레이스백 제거) |
| `trace/engine/__init__.py` | scan_project/scan_project_assets 노출 |
| `trace/engine/classifier.py` | classify(BR-CLASSIFY: test 우선→확장자→openapi 내용판별), 순수·전결정성 |
| `trace/engine/parsers.py` | 파서 레지스트리(P3): _parse_text(utf-8→latin-1)/_parse_pdf(pypdf 페이지별), 파일당 상한(P4) |
| `trace/engine/scanner.py` | validate_root(P1)·walk_files(followlinks=False, prune)·ExclusionMatcher(glob→regex)·is_within_root(트래버설 차단)·is_binary |
| `trace/engine/scan.py` | scan_project_assets(내부, content 포함, 실패격리 P5, 총량상한, 결정 정렬) + scan_project(공개, 메타만) |
| `pyproject.toml` | pypdf를 [dev]→[project.dependencies] 승격, types-PyYAML dev 추가 |

### 테스트
| 파일 | 내용 |
|---|---|
| `tests/test_classifier.py` | 분류 규칙 예제(확장자·test 우선·openapi vs config·폴백) |
| `tests/test_scanner_scan.py` | demo/ 스캔(7종 유형·PDF parsed·content 제외·결정성)·무효/파일 경로 오류·제외 prune·빈 프로젝트 |
| `tests/test_scanner_properties.py` | PBT 4속성(hypothesis, derandomize): A 분류 전결정성 / B 경로 안전성 / C 부분실패 격리 / D 결정성·멱등 |

## demo/ 스캔 실증 결과
- 13개 자산 전부 parsed(failed 0), by_type = source6·markdown2·config1·sql1·openapi1·pdf1·test1 (**7종**).
- PDF 텍스트 추출 성공("20 characters" 포함 확인), OpenAPI가 config와 구분됨, 테스트 파일 감지됨.
- 무효/비디렉터리 경로 → PATH_VALIDATION_ERROR 오류 Result(스캔 미실행).

## NFR/규칙 이행
- **NFR-SEC-004/P1**: 경로 검증 게이트 + realpath + is_within_root 트래버설·심볼릭 탈출 차단.
- **FR-ANALYSIS-003/P5**: 파일 단위 try/except 격리, 예외→failed+warning, 전체 계속.
- **P4/BR-SIZE**: 파일당 5MB truncate(partial+warning), 총량 200MB 초과 시 skip+warning.
- **P6**: Warning 코드 체계(file_truncated/total_size_cap/parse_failed/...).
- **BR-DET**: rel_path 정렬·절대경로 비노출·2회 스캔 동일(테스트로 검증).
- **PBT 확장**: 4속성 전부 구현(전면 정책 이행).

## 알려진 사항(범위 밖)
- mypy 잔여 2건은 UOW-0F 선재 이슈(errors.py의 Result 문자열 전방참조, llm/client.py) — UOW-01 범위 아님.
- `analyze_project`(전체 파이프라인)는 훅만; 완성은 UOW-02+ 에서 scan_project_assets 소비.

## 다음 단계 컨텍스트
- UOW-02(Feature/Knowledge)는 `scan_project_assets(path)` 로 content 포함 `list[Asset]`을 받아 LLM 그라운딩.
- Asset.asset_type → EvidenceType 1:1, Asset.rel_path → Evidence.source 표기.
