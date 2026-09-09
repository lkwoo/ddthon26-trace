# UOW-05 (MCP 서버 인터페이스) — NFR Design Patterns

**단계**: CONSTRUCTION / NFR Design (UOW-05)
**작성일**: 2026-09-09
**입력**: nfr-requirements(IF/RUN/REL/UX/SEC/TST/MAINT), tech-stack-decisions
**참고**: 추가 질문 없음 — 패턴이 앞 단계 결정에서 일의적으로 도출됨. **설치 `mcp` 2.x(`MCPServer`) API 기준.**

---

## P1. 서버 구성 (NFR-05-IF/RUN, Q1=A)
- **패턴**: *Factory + decorator registration*. `build_server() -> MCPServer`:
  `MCPServer(name="trace", version=...)` 생성 후 5 도구·리소스·프롬프트를 데코레이터로 등록해 반환.
  `__main__.main()`은 `build_server().run("stdio")` (지연 임포트 — NFR-05-TST-3).
- 도구 함수 시그니처의 **타입힌트가 입력 스키마**가 된다(MCPServer 자동 생성, NFR-05-IF-2).

## P2. 얇은 도구 핸들러 + 오류 격리 (NFR-05-REL-1/MAINT-1, Q3=A)
- **패턴**: *Thin adapter with guard*. 각 핸들러:
  ```
  @server.tool()
  def analyze_task_impact(task: str, feature_id: str | None = None) -> dict:
      try:    return serialize_result(core.analyze_task_impact(task, feature_id, path=_root()))
      except Exception as exc:  return serialize_result(error_to_result(exc))
  ```
  비즈니스 로직 없음 — 입력·루트 주입·직렬화만. 예외는 구조화 오류 Result로 흡수(서버 무크래시).
- `_root()` = `os.environ.get("TRACE_PROJECT_ROOT") or os.getcwd()` (Q2=A, NFR-05-RUN-3).

## P3. 직렬화 (NFR-05-UX-1/MAINT-2)
- **패턴**: *Single serializer, key-ordered*. `serialize_result(r: Result) -> dict`:
  `r.model_dump(exclude_none=True)` 후 **핵심 우선 키 순서**(summary→data→conflicts→impact→evidence→warnings→meta)로
  재구성(빈 리스트/None 생략). 도구는 이 dict 반환(구조화) — summary가 사람이 읽는 앞머리.

## P4. 코어 래퍼 (NFR-05-IF-1)
- **패턴**: *Result-returning delegation*. engine에 추가:
  - `list_features(*, path=".") -> Result`: store.list_feature_summaries → data{features}, meta{count}.
  - `get_feature_knowledge(feature_id, *, path=".") -> Result`: store.load_feature → data{feature,claims,conflicts,...},
    본문은 리소스로(도구는 요약/구조화). 부재/손상은 error_to_result.
- 기존 `scan_project`(UOW-01)·`analyze_project`/`get_conflicts`/`analyze_task_impact`(UOW-03/04)와 합쳐 5 도구 완비.

## P5. 리소스 & 프롬프트 (NFR-05-UX-3, FR-MCP-002/003, Q4=A)
- **패턴**: *Resource template + prompt*.
  - `@server.resource("trace://feature/{feature_id}")` → `KnowledgeStore(_root()).read_resource(...)` (본문 Markdown).
    URI 화이트리스트·경로 방어는 store 재사용(NFR-05-SEC-2).
  - `@server.prompt()` `review_before_implementation(task)` → "구현 착수 전 analyze_task_impact·get_conflicts 검토" 안내 문자열.

## P6. 테스트 배치 (NFR-05-TST)
| 파일 | 내용 |
|---|---|
| `tests/test_serialize_result.py` | serialize_result 키 순서·None 제외·conflicts/impact 포함 |
| `tests/test_mcp_server.py` | build_server 구성: 5 도구 등록 목록, 리소스/프롬프트 등록, 도구 핸들러 오류→구조화 Result(FakeLLM/tmp 지식) |
| `tests/test_core_wrappers.py` | list_features/get_feature_knowledge Result(부재→오류 Result) |
- mcp 미설치 시 `test_mcp_server`는 importorskip("mcp")로 skip(코어 테스트는 영향 없음).

## P7. 결정성/보안
- 도구 결과는 코어 Result 결정성 상속. 직렬화는 고정 키 순서(재현).
- 로컬 stdio 단일 프로세스(NFR-05-SEC-1). 오류 메시지 sanitize_error(절대경로·시크릿 비노출).

## P8. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | P2 도구 오류 격리 무크래시, P5 리소스 실패 강등. |
| Property-Based Testing | **N/A** | 어댑터 계층 순수 불변식 부재 — 예제 기반 단위로 충분. |
| Security Baseline | **N/A(미적용)** | opt-out. P7 보안 패턴은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.
