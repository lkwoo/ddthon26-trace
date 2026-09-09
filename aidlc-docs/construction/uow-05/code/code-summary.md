# UOW-05 (MCP 서버 인터페이스) — Code Summary

**단계**: CONSTRUCTION / Code Generation (UOW-05)
**작성일**: 2026-09-09
**결과**: `pytest` **142 passed, 3 skipped**(옵트인 `llm_integration`), 신규 모듈 **mypy-clean**.

---

## 생성/수정 파일

### 코드 (trace/)
| 파일 | 내용 |
|---|---|
| `engine/analyze.py` **수정** | `list_features(*, path=".")`, `get_feature_knowledge(feature_id, *, path=".")` — store 위임·Result, 부재/손상→error_to_result. |
| `engine/__init__.py` **수정** | 위 2함수 export. |
| `mcp_server/__init__.py` **신설** | 패키지 docstring(지연 임포트 방침). |
| `mcp_server/serialize.py` **신설** | `serialize_result(Result) -> dict` — model_dump(exclude_none) + 핵심 우선 키 순서. |
| `mcp_server/server.py` **신설** | `build_server() -> MCPServer`(5 도구·리소스·프롬프트), `_root()`(TRACE_PROJECT_ROOT/cwd), 핸들러 오류 격리. |
| `mcp_server/__main__.py` **신설** | `main()`: `build_server().run("stdio")`. |
| `common/errors.py` **수정** | `error_to_result`가 임의 예외도 안전 흡수(getattr code·sanitize) — 어댑터 무크래시. |
| `pyproject.toml` **수정** | `mcp>=1.2.0` → `mcp>=2.0`. |

### 테스트 (tests/)
| 파일 | 내용 |
|---|---|
| `test_serialize_result.py` | 키 순서(summary→…→meta)·None/빈 제외·impact 포함. |
| `test_core_wrappers.py` | list_features/get_feature_knowledge Result·부재→오류 Result. |
| `test_mcp_server.py` | `importorskip("mcp")`: 5 도구·프롬프트 등록, `_root()` env 우선, main import. |

---

## 앞 단계 결정의 반영

- **5 도구 = 코어함수 1:1**: `trace_analyze_project`/`trace_list_features`/`trace_get_feature_knowledge`/
  `trace_get_conflicts`/`trace_analyze_task_impact` — 타입힌트가 입력 스키마(FR-MCP-001).
- **얇은 어댑터 + 오류 격리**: 각 핸들러는 `try: serialize_result(core(...)) except Exception: serialize_result(error_to_result(exc))`
  — 비즈니스 로직 없음, 예외 흡수로 **서버 무크래시**(NFR-05-REL-1).
- **핵심 우선 직렬화**: `serialize_result`가 summary→conflicts→impact→evidence 순, 빈 값 생략(NFR-MCP-UX-002).
- **리소스·프롬프트**: `trace://feature/{id}` 리소스(본문 Markdown), `review_before_implementation` 프롬프트(P1, FR-MCP-003).
- **루트 주입**: cwd 기본 + `TRACE_PROJECT_ROOT`(NFR-05-RUN-3). **mcp 지연 임포트** — 코어·대다수 테스트 무의존.

## 구현 중 결정/발견

- **error_to_result 견고화**: MCP 핸들러가 임의 예외를 흡수할 수 있도록 `error_to_result`를 TraceError 외
  예외에도 안전(getattr(code)·sanitize_error)하게 확장 — 무크래시 보장의 실제 근거.
- **mcp 2.x 확인**: 설치 SDK가 2.x(`MCPServer`, 구 FastMCP)임을 검증하고 `.tool/.resource/.prompt`+`run("stdio")`로 배선.
  pyproject `mcp>=2.0`로 상향.
- **사전 존재 mypy 경고**: `llm/client.py`(UOW-0F)의 `_sdk_client` None→Anthropic 할당 경고는 이번 범위 밖으로 유지(신규 모듈은 clean).

## DoD
- [x] 5 도구 노출·입력 스키마·구조화 결과. build_server 등록 확인(테스트).
- [x] 지식 리소스(trace://feature/{id})·구현전검토 프롬프트.
- [x] stdio 엔트리포인트 `trace-mcp`(main import 가능).
- [x] 도구 오류 격리(무크래시), 핵심 우선 직렬화.
- [x] pytest 142 pass·3 skip, 신규 모듈 mypy-clean.

## 다음(UOW-06)
- Hero E2E·README(.mcp.json 스니펫·예제 프롬프트)·페르소나 사용 여정·`result/` 스크린샷·CLI 폴백(C9)·보안 위생 점검.
