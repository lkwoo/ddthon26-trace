# UOW-06 (통합·신뢰성·시연) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (UOW-06, 수렴)
**작성일**: 2026-09-09
**Functional Design·NFR**: **SKIP**(수렴/통합 유닛 — 기존 계약 재사용, 신규 비즈니스 로직 없음. 보안/신뢰성은 per-unit 확립).
**책임**: Hero E2E(DoD 앵커)·실패/캐시·폴백 CLI(C9)·보안 위생·README(.mcp.json·예제 프롬프트)·페르소나 사용 여정·`result/` 시연 증거.
**스토리**: US-06.1(Hero E2E)·US-06.2(실패/폴백)·US-06.3(턴키 시연·스크린샷)·US-06.4(보안 위생).
**요구사항**: NFR-REL-001/002, NFR-AI-004, FR-DEMO-001/002, NFR-SEC-001/002/005, NFR-LOG-001.
**기존 계약 소비**: 코어 5함수(engine), FakeLLM(conftest), demo/ 데이터셋(13자산 parsed, PDF 포함).

---

## 생성/수정 파일

### 코드 (C9 폴백 CLI)
- [x] C1. `trace/cli/__init__.py` **[신설]** — 패키지 docstring.
- [x] C2. `trace/cli/__main__.py` **[신설]** — argparse CLI(FR-DEMO-002): 서브커맨드
      `analyze`, `features`, `knowledge <id>`, `conflicts [--feature]`, `impact <task> [--feature]` →
      코어 함수 호출 → 사람이 읽는 요약 + `--json` 시 구조화 출력. `--path`(기본 cwd/TRACE_PROJECT_ROOT). 엔트리 `trace`.
      코어와 동일 함수 재사용(NFR-CORE-001), 오류는 error_to_result로 사람이 읽게.

### 데모 하니스 (결정적 실행 증거)
- [x] C3. `demo/run_demo.py` **[신설]** — Hero 하니스: demo/ 스캔 → 실제 rel_path 기반 **스크립트 FakeLLM 응답**(3충돌 재현)
      주입 → analyze_project→list_features→get_conflicts→analyze_task_impact 전 흐름 출력. API 키 불필요·결정적(NFR-AI-004).

### 테스트 (Hero E2E)
- [x] C4. `tests/test_hero_e2e.py` **[신설]** — demo/에 스크립트 FakeLLM 주입 E2E: 3충돌(유형 정확)·충돌 경고·Must/Likely/Review·Change Plan,
      2회 실행 동일(반복 가능, NFR-REL-001/AI-004), get_feature_knowledge/list_features 연동.

### 문서 · 시연 산출물
- [x] C5. `README.md` **[갱신]** — 상태 갱신, `.mcp.json` 복붙 스니펫(trace-mcp·TRACE_PROJECT_ROOT), 설치·키, 5도구/CLI 사용, Hero 예제 프롬프트, 페르소나 여정 링크(FR-DEMO-001, US-06.3-AC1).
- [x] C6. `result/usage-walkthrough.md` **[신설]** — P1/P2/P3 3페르소나 각 [언제·빈도 → 자연어 요청 → 호출 MCP 도구 → 실행 증거 → 이점(TRACE 부재 대비)] 형식.
- [x] C7. `result/hero-demo-output.txt` **[신설]** — `run_demo.py` 실제 실행 콘솔 출력 캡처(결정적 실행 증거).
- [x] C8. `result/README.md` **[신설]** — 증거 인덱스 + **GUI 스크린샷 생성 가이드**(Claude Code + API 키로 캡처하는 절차).

### 보안 위생 & 검증
- [x] C9. 보안 위생 점검 — 소스 내 하드코딩 시크릿 없음(grep), .gitignore(.env/.trace) 확인, 키 late-lookup 재확인(US-06.4).
- [x] V1. `pytest -q` 전체 green(기존 142 pass 유지 + Hero E2E), `llm_integration` skip.
- [x] V2. `python demo/run_demo.py` 무키 실행 성공 → 출력 result/hero-demo-output.txt 저장.
- [x] V3. `trace --help` 및 `trace conflicts`(캐시 기반) 동작 확인.
- [x] V4. code-summary.md 작성.

---

## 스크린샷 한계(정직 고지)
- GUI(Claude Code) 스크린샷은 **실제 Anthropic API 키 + Claude Code 실행 환경**이 필요해 이 자동화 환경에서 직접 캡처 불가.
- 대체·보완: (1) `run_demo.py`의 **결정적 CLI 실행 출력**을 `result/hero-demo-output.txt`로 실증 저장(무키),
  (2) `result/README.md`에 GUI 스크린샷 캡처 절차 제공. 사용자가 키 주입 후 캡처하면 `result/`에 PNG 추가.

## 결정/제약
- 신규 런타임 의존성 없음. CLI·데모는 기존 코어·FakeLLM 재사용.
- 시크릿은 env/.env(gitignore)만. 스크린샷·출력에 키 비노출.

## Part 2 (승인 후 실행)
C1~C9 생성 → V1~V4 검증 → `aidlc-docs/construction/uow-06/code/code-summary.md` 작성.
