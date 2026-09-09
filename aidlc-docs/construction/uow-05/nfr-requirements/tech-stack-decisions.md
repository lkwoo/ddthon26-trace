# UOW-05 (MCP 서버 인터페이스) — Tech Stack Decisions

**단계**: CONSTRUCTION / NFR Requirements (UOW-05)
**작성일**: 2026-09-09

---

## 상속 (변경 없음)
- **코어 함수**: `scan_project`, `analyze_project`, `get_conflicts`, `analyze_task_impact`(engine), `KnowledgeStore`(리소스).
- **Result/직렬화**: `Result`, `build_result`, `error_to_result`, `sanitize_error`(UOW-0F).
- **엔트리포인트**: `trace-mcp = trace.mcp_server.__main__:main`(pyproject 기정의).

## 신규 / 변경 결정 (UOW-05)
| 항목 | 결정 | 근거 |
|---|---|---|
| MCP SDK | **`mcp>=2.0`** — 설치 환경 2.x, `from mcp.server.mcpserver import MCPServer`(구 FastMCP) | Q1=A. pyproject `mcp>=1.2.0` → `>=2.0` 상향 |
| 서버 구성 | `MCPServer(name, version)` + `.tool()`/`.resource()`/`.prompt()` 데코레이터, `run("stdio")` | Q1=A, 타입힌트 스키마·간결 |
| 코어 래퍼 | `list_features()`, `get_feature_knowledge(feature_id)` → Result (engine, store 위임) | 5 도구 완비(FR-MCP-001) |
| 직렬화 | `serialize_result(Result) -> dict` — 핵심 우선 순서·None 제외 | NFR-05-UX-1/MAINT-2 |
| 루트 주입 | cwd 기본 + `TRACE_PROJECT_ROOT` env | Q2=A |
| 프롬프트(P1) | "구현 전 검토" MCP 프롬프트 등록 | Q4=A, FR-MCP-003 |
| 지연 임포트 | `mcp`는 서버 모듈에서만 임포트(코어·테스트는 불필요) | NFR-05-TST-3 |

## 배치
```text
trace/mcp_server/
├── __init__.py
├── __main__.py       # main(): MCPServer 구성 + run("stdio")
├── server.py         # build_server(): 도구·리소스·프롬프트 등록
└── serialize.py      # serialize_result
trace/engine/analyze.py   # [수정] list_features, get_feature_knowledge 추가
pyproject.toml            # mcp>=2.0
```

## 비결정 / 유지
- 원격 전송(sse/http)·인증은 범위 밖(로컬 stdio 단일 프로세스, NFR-05-SEC-1).
- PBT는 어댑터 계층 N/A — 직렬화·오류 매핑은 예제 기반 단위로 검증.
