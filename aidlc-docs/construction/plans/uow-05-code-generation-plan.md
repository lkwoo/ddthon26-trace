# UOW-05 (MCP 서버 인터페이스) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (UOW-05)
**작성일**: 2026-09-09
**입력**: nfr-requirements(IF/RUN/REL/UX/SEC/TST), nfr-design(P1~P8), logical-components
**앞 단계 반영**: 얇은 어댑터·오류 격리 무크래시·핵심 우선 직렬화·mcp>=2.0(MCPServer)·mcp 지연임포트.
**기존 계약 소비**: `scan_project/analyze_project/get_conflicts/analyze_task_impact`(engine), `Result/build_result/error_to_result`(result/errors),
`KnowledgeStore`(리소스), `sanitize_error`. 설치 `mcp` 2.x `from mcp.server.mcpserver import MCPServer`.

---

## 생성/수정 파일

### 코드
- [ ] C1. `trace/engine/analyze.py` **[수정]** — `list_features(*, path=".")`, `get_feature_knowledge(feature_id, *, path=".")` (store 위임·Result·부재→error_to_result).
- [ ] C2. `trace/engine/__init__.py` **[수정]** — 위 2함수 export.
- [ ] C3. `trace/mcp_server/__init__.py` **[신설]** — 패키지 docstring(지연 임포트 주석).
- [ ] C4. `trace/mcp_server/serialize.py` **[신설]** — `serialize_result(Result) -> dict` (model_dump(exclude_none)·핵심 우선 키 순서).
- [ ] C5. `trace/mcp_server/server.py` **[신설]** — `build_server() -> MCPServer`(5 도구·리소스·프롬프트 등록), `_root()`(TRACE_PROJECT_ROOT/cwd). 각 도구 try/except→serialize_result(error_to_result).
- [ ] C6. `trace/mcp_server/__main__.py` **[신설]** — `main()`: `build_server().run("stdio")`.
- [ ] C7. `pyproject.toml` **[수정]** — `mcp>=1.2.0` → `mcp>=2.0`.

### 테스트
- [ ] T1. `tests/test_serialize_result.py` — 키 순서(summary→…→meta)·None/빈 제외·conflicts/impact 포함.
- [ ] T2. `tests/test_core_wrappers.py` — list_features/get_feature_knowledge Result(tmp 지식·부재→오류 Result).
- [ ] T3. `tests/test_mcp_server.py` — `importorskip("mcp")`: build_server 5 도구 등록 목록, 리소스/프롬프트 등록, 도구 핸들러 오류→구조화 Result.

### DoD 검증
- [ ] V1. `pytest -q` 전체 green(기존 131 pass 유지 + 신규), `llm_integration` skip.
- [ ] V2. 신규 모듈 mypy-clean(server.py는 mcp 동적 타입 — 필요한 최소 ignore만).
- [ ] V3. build_server()가 5 도구 + 리소스 템플릿 + 프롬프트 등록, `main` import 가능.
- [ ] V4. code-summary.md 작성.

---

## 핵심 구현 (nfr-design 반영)

**serialize_result** (C4): `d = result.model_dump(exclude_none=True)`; 핵심 우선 키 순서로 재조립(summary·data·conflicts·impact·evidence·warnings·meta); 빈 리스트/dict 생략.

**list_features / get_feature_knowledge** (C1): `KnowledgeStore(path)` 위임 → build_result(요약/구조화). load 실패 → error_to_result.

**build_server** (C5): `MCPServer(name="trace", version="0.1.0")`. `@server.tool()` 5개(analyze_project/list_features/get_feature_knowledge/get_conflicts/analyze_task_impact) — 각기 `try: serialize_result(core(...)) except Exception: serialize_result(error_to_result(exc))`. `@server.resource("trace://feature/{feature_id}")` → store.read_resource. `@server.prompt()` review_before_implementation(task).

**main** (C6): `build_server().run("stdio")`.

---

## 결정/제약
- `mcp`는 server.py/__main__.py에서만 임포트(지연) — 코어·T1/T2는 mcp 불필요.
- 신규 런타임 의존성 없음(mcp는 기정의, 버전만 상향). 도구 핸들러 비즈니스 로직 금지(코어 위임).
- 오류 메시지 sanitize_error(절대경로·시크릿 비노출).

## Part 2 (승인 후 실행)
C1~C7 + T1~T3 생성 → V1~V4 검증 → `aidlc-docs/construction/uow-05/code/code-summary.md` 작성.
