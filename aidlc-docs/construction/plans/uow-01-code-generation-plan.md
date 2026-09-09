# UOW-01 (스캐너 & 파서) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (per-unit: UOW-01)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-PATH/EXCLUDE/CLASSIFY/PARSE/SIZE/FAIL/DET/SEC) +
NFR Requirements(성능 5MB/200MB·PBT 4속성) + NFR Design(P1~P9 패턴, logical-components 모듈/시그니처)를
실제 코드로 구현한다. UOW-0F 계약(Result/Warning/build_result/EvidenceType/errors/logging) 재사용.

---

## 생성/수정 대상 (체크박스)

### A. 도메인 모델 & 설정
- [ ] A1. `trace/models/asset.py` — `AssetType`(EvidenceType 정렬)·`ParseStatus`·`Asset`(+`to_meta()` content 제외)
- [ ] A2. `trace/config/scan_settings.py` — `ScanSettings(max_file_bytes=5_000_000, max_total_bytes=200_000_000)` + `get_scan_settings()`(env override 지점)

### B. 엔진 (engine/, C2 스캔 구간)
- [ ] B1. `trace/engine/__init__.py`
- [ ] B2. `trace/engine/classifier.py` — `classify()`(BR-CLASSIFY, test 우선→확장자→openapi 판별), 순수 함수
- [ ] B3. `trace/engine/parsers.py` — 파서 레지스트리(P3), `_parse_text`(utf-8→latin-1), `_parse_pdf`(pypdf 페이지별), 크기상한 처리(P4)
- [ ] B4. `trace/engine/scanner.py` — `validate_root`(P1)·`walk_files`(followlinks=False, prune)·`is_within_root`·`is_binary`
- [ ] B5. `trace/engine/scan.py` — `scan_project_assets()`(내부, content 포함, 실패격리 P5, 총량상한, 결정 정렬) + `scan_project()`(공개, 메타만 Q5=A, build_result)

### C. 오류 타입
- [ ] C1. `trace/common/errors.py` 에 `PathValidationError` 추가(없으면). 메시지 위생(P5 sanitize 유틸 포함)

### D. 테스트
- [ ] D1. `tests/test_classifier.py` — 분류 규칙 예제(각 유형·test 우선·openapi vs config)
- [ ] D2. `tests/test_scanner_scan.py` — `scan_project("demo")` → 6종 유형·PDF parsed·failed 0·결정적 순서; 무효/비디렉터리 경로 → 오류 Result; 제외규칙(.git 등) 순회 생략
- [ ] D3. `tests/test_scanner_properties.py` — PBT 4속성(hypothesis): A 분류 전결정성 / B 경로 안전성 / C 부분실패 격리 / D 결정성·멱등

### E. 의존성 & 마무리
- [ ] E1. `pyproject.toml` — `pypdf>=4.0`를 [dev]에서 [project.dependencies]로 이동(런타임 승격)
- [ ] E2. 로컬 `pytest` 전체 실행 → 전부 pass 확인(기존 43 + UOW-01 신규)
- [ ] E3. `aidlc-docs/construction/uow-01/code/code-summary.md` 작성
- [ ] E4. 계획 체크박스 전부 [x], 커밋

---

## 준수 사항
- **경계**: 스캔+텍스트화+분류까지만. 구조 파싱(AST/스키마)·Feature/Claim 추출 금지(UOW-02/03).
- **결정성(BR-DET)**: assets rel_path 정렬, data에 절대경로/타임스탬프 미포함. PBT는 재현 가능하게(seed/derandomize 고려).
- **보안(P1/P5/BR-SEC)**: 경로검증 게이트, 트래버설/심볼릭 탈출 차단, 메시지 시크릿 비노출, 읽기 전용.
- **오케스트레이션 훅**: `analyze_project` 완성은 UOW-02+; 이번엔 `scan_project(_assets)`만 실구현(호출 훅만 남김).
- **타입/린트**: mypy(disallow_untyped_defs) 통과하도록 타입 힌트 완비(기존 정책).

## 실행 순서 (Part 2)
A1→A2→C1→B2(classifier)→B3(parsers)→B4(scanner)→B5(scan)→D1→D2→D3→E1→E2(pytest)→E3→E4
