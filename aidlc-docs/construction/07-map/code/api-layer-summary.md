# UOW-07 온보딩 맵 — API Layer 요약 (Step 8~12)

어댑터는 얇게 유지(NFR-CORE-001/002): 코어 함수 `generate_onboarding_map`만 호출, 비즈니스 로직 없음.

| 계층 | 배선 | 내용 |
|---|---|---|
| C8 프롬프트 | `traceki/prompts/templates/onboarding_map.md` | 정적 사실 주입 + JSON 스키마(`narrative`·`relation_notes`·`key_flow`) + 근거 인용/불확실성 규칙 |
| C2 엔진 | `traceki/engine/__init__.py` | `__all__` 추가 + `__getattr__` 지연 재노출(순환 방지) |
| C1 MCP | `traceki/mcp_server/__init__.py` | `@mcp.tool generate_onboarding_map(path, feature_id, refresh)` + `@mcp.resource("trace://overview")` (도구 6·리소스 3), INSTRUCTIONS 갱신 |
| C9 CLI | `traceki/cli/__init__.py` | `trace map [path] [--feature] [--refresh] [--json]` (사람이 읽는 출력 + `--json` 원시 Result) |

**계약 준수**: 모든 진입점이 동일 코어 함수를 호출 → MCP·CLI·테스트 간 동작 일치. replay step_key `describe_relations`로 API 키 없이 결정적 재현.
