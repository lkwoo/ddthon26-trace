# UOW-05 (MCP 서버 인터페이스) — Logical Components

**단계**: CONSTRUCTION / NFR Design (UOW-05)
**작성일**: 2026-09-09

> Code Generation의 파일 청사진. 얇은 어댑터 — 코어(engine)와 Result에만 의존.

---

## 모듈 배치
```text
trace/
├── mcp_server/
│   ├── __init__.py
│   ├── __main__.py       # [신설] main(): build_server().run("stdio")
│   ├── server.py         # [신설] build_server(): MCPServer + 5 도구·리소스·프롬프트 등록
│   └── serialize.py      # [신설] serialize_result(Result) -> dict (핵심 우선)
└── engine/
    └── analyze.py        # [수정] list_features, get_feature_knowledge 추가
pyproject.toml            # [수정] mcp>=2.0
tests/
├── test_serialize_result.py   # [신설]
├── test_mcp_server.py         # [신설] importorskip("mcp")
└── test_core_wrappers.py      # [신설]
```

## 시그니처

### engine/analyze.py (추가)
```python
def list_features(*, path: str = ".") -> Result
def get_feature_knowledge(feature_id: str, *, path: str = ".") -> Result
```

### mcp_server/serialize.py
```python
def serialize_result(result: Result) -> dict   # model_dump(exclude_none) → 핵심 우선 키 순서
```

### mcp_server/server.py
```python
def build_server() -> "MCPServer":       # mcp 지연 임포트
    server = MCPServer(name="trace", version="0.1.0")
    # @server.tool(): analyze_project, list_features, get_feature_knowledge, get_conflicts, analyze_task_impact
    # @server.resource("trace://feature/{feature_id}"): 지식 본문
    # @server.prompt(): review_before_implementation
    return server

def _root() -> str:  # TRACE_PROJECT_ROOT or cwd
```

### mcp_server/__main__.py
```python
def main() -> None:   # build_server().run("stdio")
```

## 의존성 방향 (순환 없음)
```text
mcp_server/server → engine(analyze/scan 코어), knowledge/store, mcp_server/serialize, models/result, common/errors, mcp(지연)
mcp_server/serialize → models/result
engine/analyze     → knowledge/store, models/result  (list_features/get_feature_knowledge 추가분)
```
- `mcp`는 `server.py`/`__main__.py`에서만 임포트(지연) — 코어·대다수 테스트는 mcp 불필요(NFR-05-TST-3).

## 산출물 변경 (Code Generation 예정)
- `pyproject.toml`: `dependencies`의 `mcp>=1.2.0` → `mcp>=2.0`.
- 신규 코어 함수 2개는 기존 UOW-01~04 자산 재사용(신규 런타임 의존성 없음).
