# UOW-01 (스캐너 & 파서) — NFR Design Patterns

**단계**: CONSTRUCTION / NFR Design (UOW-01)
**작성일**: 2026-09-09
**입력**: nfr-requirements.md(NFR-01-PERF/REL/SEC/MAINT, PBT-01-A~D), functional-design(BR-*)
**참고**: 추가 질문 없음 — 패턴이 앞 단계 결정에서 일의적으로 도출됨(모호성 없음).

> 각 NFR을 "코드에서 어떻게 실현할지"의 패턴으로 전개한다. 기술 비종속 규칙(BR-*)을
> Python 구현 패턴으로 구체화하되, 구현 코드는 Code Generation에서 작성한다.

---

## P1. 경로 검증 게이트 (NFR-01-SEC-1/2, BR-PATH)
- **패턴**: *Guard Clause + Canonicalization*. `scan_project` 진입 즉시 `validate_root(path)`:
  `Path(path).resolve()` → `exists()` and `is_dir()` 확인, 실패 시 `PathValidationError`(common/errors) 발생 →
  상위에서 오류 Result로 변환(스캔 미실행).
- **트래버설 차단**: 각 후보 경로를 `resolve()` 후 `is_relative_to(root)` 검사. False면 skip+warning.
- **심볼릭**: `os.walk(root, followlinks=False)`. 파일 심볼릭은 `Path.is_symlink()`면 대상 resolve 후
  루트 내 여부 확인, 탈출 시 skip.

## P2. 순회 + 제외 (NFR-01-PERF-1, BR-EXCLUDE)
- **패턴**: *Prune-on-descent*. `os.walk` 중 `dirnames[:] = [d for d in dirnames if d not in exclusions]`로
  제외 디렉터리의 하위 순회 자체를 생략(성능). `exclusions = config.get_exclusions()`.
- **결정적 순회**: 각 디렉터리의 `filenames`를 `sorted()`로 처리, 최종 assets도 `rel_path` 정렬(BR-DET-001).

## P3. 파서 레지스트리 (NFR-01-MAINT-2, BR-PARSE)
- **패턴**: *Strategy/Registry map*. `AssetType → parser 함수` 매핑 딕셔너리.
  ```
  _PARSERS = {AssetType.PDF: _parse_pdf, ... default: _parse_text}
  ```
  새 유형 추가 = 매핑 1줄 + 함수 1개(국소 변경). 텍스트류는 공통 `_parse_text` 재사용.
- **텍스트 디코드**: `bytes.decode("utf-8")` 실패 시 `latin-1` 폴백(BR-PARSE-001).
- **PDF**: `pypdf.PdfReader`, 페이지별 `extract_text()` 이어붙임. 페이지 예외는 건너뛰고 partial.

## P4. 크기 상한 스트리밍 (NFR-01-PERF-3/4, BR-SIZE)
- **파일당(5MB)**: 읽기 전 `stat().st_size` 확인, 초과면 `open().read(MAX_FILE_BYTES)`로 상한까지만 →
  `truncated=True`, status=partial, warning(code=`file_truncated`).
- **총량(200MB)**: 러닝 카운터 `total_read`. 다음 파일이 상한을 넘기면 그 파일부터 skip +
  warning(code=`total_size_cap`) 후 순회 계속(자산은 메타만 skipped로 기록).

## P5. 실패 격리 (NFR-01-REL-1/2, BR-FAIL)
- **패턴**: *Per-item try/except + accumulate*. 파일 루프의 각 반복을 try로 감싸고, 예외는
  `Asset(parse_status=failed, error=sanitize(exc))` + `Warning(code="parse_failed", source=rel_path)`로
  적립 후 `continue`. 스캔 함수는 예외를 밖으로 던지지 않는다(무효 루트 제외).
- **sanitize**: 예외 메시지에서 절대경로·바이트 내용 제거, `type(exc).__name__` + 안전 요약만.

## P6. Warning 코드 체계 (NFR-01-REL-2, 관측 가능성)
| code | 상황 |
|---|---|
| `path_invalid` | 루트 경로 무효(오류 Result meta) |
| `symlink_skipped` | 루트 밖 심볼릭 대상 |
| `binary_skipped` | 바이너리(비 PDF) |
| `file_truncated` | 파일당 상한 초과 |
| `total_size_cap` | 총량 상한 초과로 이후 skip |
| `parse_failed` | 파일 파싱 예외 |
| `openapi_parse_fallback` | YAML/JSON 파싱 실패 → config 폴백 |
- 모든 Warning은 `Warning(code, message, source=rel_path)`(UOW-0F) 형식. message는 사람이 읽는 한국어 요약.

## P7. 설정 분리 (NFR-01-MAINT-1, Q4=A)
- `trace/config`에 스캔 설정 추가: `get_scan_settings() -> ScanSettings(max_file_bytes=5_000_000,
  max_total_bytes=200_000_000)`. 기본은 상수, 필요 시 env/override 지점 남김(기존 config 패턴 준수).

## P8. PBT 배치 (PBT-01-A~D)
- **패턴**: *Property test module* `tests/test_scanner_properties.py`(hypothesis).
  | 속성 | 전략 |
  |---|---|
  | A 분류 전결정성 | `st.text()` 파일명/`st.sampled_from(exts)` → classify가 AssetType 반환, 예외 없음 |
  | B 경로 안전성 | `tmp_path`에 트리 생성 + 루트 밖 타깃 심볼릭/`..` 경로 → 결과 rel_path 전부 루트 내 |
  | C 부분 실패 격리 | 무작위 파일 일부를 손상(디코드 불가 바이트/삭제) → scan 예외 없이 완료, 손상만 failed |
  | D 결정성/멱등 | 무작위 트리 2회 scan → assets 리스트(순서 포함) 동일 |
- 결정적 재현: hypothesis `derandomize` 또는 고정 seed 고려(테스트 안정성).

## P9. 결정성 (BR-DET)
- data.assets는 `rel_path` 오름차순. 절대경로·타임스탬프 미포함. `root`는 표시용 프로젝트명/상대 표기.
