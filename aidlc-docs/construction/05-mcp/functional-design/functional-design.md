# UOW-05 MCP 어댑터 — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: component-methods.md(C1), unit-of-work.md(UOW-05), 요구사항 §13(MCP 노출)·§4(Q1 MCP SDK)
**스토리**: FR-MCP-001(도구 노출), FR-MCP-002(리소스), NFR-CORE-001/002(얇은 어댑터), NFR-MCP-UX-002
**의존**: UOW-02~04(코어 함수 5종), UOW-0F(Result 직렬화)

## 1. 설계 원칙 — 얇은 어댑터

어댑터는 비즈니스 로직을 갖지 않는다. 5개 MCP 도구가 엔진 코어 함수와 **1:1**로 매핑되고,
공통 Result를 `to_dict()`(summary 우선 키 순서)로 직렬화만 한다. 향후 CLI(UOW-06)도 동일 코어를
호출하므로 로직 중복이 없다(NFR-CORE-001/002).

## 2. 도구 (코어 함수 1:1)

| MCP 도구 | 코어 함수 | 반환 |
|---|---|---|
| `analyze_project(path, refresh)` | engine.analyze_project | features·conflicts_count·assets_count |
| `list_features()` | engine.list_features | Feature 요약 목록 |
| `get_feature_knowledge(feature_id)` | engine.get_feature_knowledge | 지식 상세 |
| `get_conflicts(feature_id?)` | conflict.get_conflicts | 충돌 목록 |
| `analyze_task_impact(task, feature_id?)` | impact.analyze_task_impact | Must/Likely/Review + plan |

## 3. 리소스 (지식 노출)

- `trace://features` — Feature 인덱스(id·제목·충돌 수, Markdown).
- `trace://feature/{feature_id}` — 단일 Feature 지식 문서(MD+YAML) 템플릿 리소스.

## 4. 비즈니스 규칙

1. **전송/로깅 분리**: stdio 전송. 로그는 stderr로만(common.get_logger) → stdout(MCP 프레이밍) 무오염.
2. **입력 검증**: MCP SDK가 타입 힌트 기반 JSON 스키마로 인자 검증. 경로·빈 작업 등 도메인 검증은
   코어 함수가 Result.error로 처리(어댑터는 그대로 전달).
3. **키 순서 보존**(NFR-MCP-UX-002): 반환 JSON 첫 키가 항상 `summary` → 에이전트가 바로 설명.
4. **지연 임포트**: `mcp`는 서버 기동 시에만 임포트 → 코어/테스트는 오프라인.
5. **환경 기반 설정**: `load_config(".")`로 백엔드(live/replay)·키를 env에서 결정(NFR-SEC-001).

## 5. 기술 메모 — mcp 2.x

설치된 SDK는 mcp 2.x(FastMCP→`MCPServer`). `@mcp.tool()`/`@mcp.resource(uri)` 데코레이터 +
`run(transport="stdio")` 사용. pyproject 핀을 `mcp>=2,<3`로 갱신.

## 6. 검증

`tests/test_mcp_server.py` 4개 통과: 5개 도구 등록·리소스/템플릿 노출·Hero 디스패치(충돌·영향)·
리소스 읽기. 부수로 UOW-03 `normalize_value` 멱등성 결함(속성 테스트가 검출: `". 0"`)을 수정.
전체 56개 통과.
