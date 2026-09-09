# UOW-01 (스캐너 & 파서) — 비즈니스 규칙 (business-rules)

**단계**: CONSTRUCTION / Functional Design (UOW-01)
**작성일**: 2026-09-09
**출처 요구사항**: FR-PROJECT-001/002/003, FR-ANALYSIS-003, NFR-SEC-004

---

## BR-PATH — 경로 검증 (NFR-SEC-004, FR-PROJECT-001)
- **BR-PATH-001**: 스캔 전 대상 경로가 **존재**하고 **디렉터리**인지 확인. 아니면 즉시 오류 Result
  (스캔 진행 안 함). summary에 사유, data 비움, meta.error_code 설정.
- **BR-PATH-002**: 경로를 절대경로로 **정규화(realpath)** 후 기준 루트로 고정. 이후 모든 자산은
  이 루트의 하위여야 한다(루트 밖으로 나가는 심볼릭 링크 대상은 **따라가지 않음** — 트래버설 차단).
- **BR-PATH-003**: 심볼릭 링크는 기본적으로 따라가지 않는다(순환·탈출 방지). 링크 발견 시 skipped + warning.
- **BR-PATH-004**: 접근 불가(권한) 디렉터리/파일은 해당 항목만 skipped + warning, 전체는 계속.

## BR-EXCLUDE — 제외 규칙 (FR-PROJECT-003, C7 소비)
- **BR-EXCLUDE-001**: 디렉터리 제외 집합은 `config.get_exclusions()`(UOW-0F)에서 가져온다.
  기본: `.git`, `node_modules`, `build`, `dist`, `target`, `.venv`, `__pycache__`, `.idea`, `.vscode`,
  `.trace`(자체 산출물). 제외 디렉터리는 **하위 순회 자체를 생략**(성능).
- **BR-EXCLUDE-002**: 바이너리로 판정된 파일(널바이트 포함/디코드 불가, 단 .pdf 예외)은 skipped.
- **BR-EXCLUDE-003**: 제외/스킵은 오류가 아니라 정상 흐름 — warning은 남기되(선택) counts.skipped로 집계.

## BR-CLASSIFY — 자산 분류 (FR-PROJECT-002, Q3=A)
- **BR-CLASSIFY-001 (우선순위)**: (1) 테스트 판별 → test, (2) 확장자 매핑 → source/sql/markdown/pdf/config,
  (3) YAML/JSON 내용 판별 → openapi vs config, (4) 그 외 텍스트 → text.
- **BR-CLASSIFY-002 (테스트 판별)**: 경로에 `/test/`·`/tests/` 세그먼트가 있거나 파일명이
  `*Test*`·`*Tests*`·`test_*`·`*_test.*` 패턴이면 asset_type=test(원 언어 무관).
- **BR-CLASSIFY-003 (openapi 판별)**: .yaml/.yml/.json 을 파싱 시도해 최상위에 `openapi` 또는
  `swagger` 키가 있으면 openapi, 없으면 config. 파싱 실패 시 config로 폴백(+warning).

## BR-PARSE — 파싱/텍스트 추출 (Q1=A, Q2=A)
- **BR-PARSE-001 (텍스트류)**: source/sql/markdown/config/text/openapi 는 UTF-8(실패 시 latin-1 폴백)로
  파일 텍스트를 그대로 읽어 `content`에 저장. 구조 파싱은 하지 않는다(Q2=A).
- **BR-PARSE-002 (PDF)**: pypdf로 페이지별 `extract_text()`를 이어붙여 content 생성. 페이지 일부 실패 시
  가능한 페이지만 추출하고 parse_status=partial + warning.
- **BR-PARSE-003 (openapi 내용)**: 분류를 위해 파싱은 하되(BR-CLASSIFY-003), content에는 원문 텍스트를 저장
  (구조 dict를 저장하지 않음 — Q2=A). 하위 AI가 원문을 그라운딩.
- **BR-PARSE-004 (정규화)**: content의 개행은 `\n`으로 정규화(결정성). 후행 공백 정리는 하지 않음(원문 보존).

## BR-SIZE — 크기 상한 (Q4=A)
- **BR-SIZE-001**: 파일당 최대 바이트 상한(기본 예: 1_000_000). 초과 시 상한까지만 읽고
  `truncated=True`, parse_status=partial, warning(code=`file_truncated`).
- **BR-SIZE-002**: 상한은 config에서 조정 가능(get_llm_settings와 별개의 스캔 설정). 기본값은 상수.

## BR-FAIL — 부분 실패 허용 (FR-ANALYSIS-003)
- **BR-FAIL-001**: 개별 파일의 읽기/추출 예외는 포착하여 해당 Asset을 parse_status=failed +
  error 요약(민감정보·전체 트레이스백 제외)으로 기록하고 **다음 파일로 계속**. 전체 스캔은 중단하지 않는다.
- **BR-FAIL-002**: 모든 실패는 `Warning(code, message, source=rel_path)`로 수집되어 Result.warnings에 합류.
- **BR-FAIL-003**: 자산이 0건이어도 오류가 아니다(빈 프로젝트) — counts=0, 안내 summary.

## BR-DET — 결정성 (재현성)
- **BR-DET-001**: assets는 `rel_path` 사전순으로 정렬해 반환(플랫폼 무관 동일 순서).
- **BR-DET-002**: 절대경로·타임스탬프 등 환경 의존 값은 data.assets에 넣지 않는다(rel_path만).
  (meta.scanned_at은 넣더라도 테스트에서 제외하거나 생략 가능.)

## BR-SEC — 보안 위생
- **BR-SEC-001**: error/warning 메시지에 파일 내용·시크릿·전체 절대경로를 노출하지 않는다(rel_path·코드만).
- **BR-SEC-002**: 스캔은 읽기 전용 — 대상 프로젝트 파일을 수정/생성하지 않는다(.trace 산출물은 별도 단위 소관).
