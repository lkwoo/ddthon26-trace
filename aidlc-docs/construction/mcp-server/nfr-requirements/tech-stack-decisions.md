# Tech Stack Decisions — U2 MCP Server

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U2 MCP Server** · 2026-09-08

## 1. 프로토콜 / SDK
- **공식 `mcp` Python SDK** (Model Context Protocol) — stdio 서버 구현 (Q3=A).
  - 근거: 표준 준수(Resources/Tools/Prompts, 핸드셰이크), 유지보수성, Claude Desktop/Claude Code 즉시 연결(US-A6).
  - `pyproject.toml` optional-extra **`[mcp]`** 로 격리(코어 U1은 mcp 미의존).
- **provider 로직은 SDK 독립**: `resources.py`/`tools.py`/`prompts.py`는 순수 매핑(테스트 가능). SDK 바인딩은 `server.py`에만(NFR-C2, NFR-U2-M1).

## 2. 전송 / 동시성
- **stdio 전송** (US-A6, NFR-E1). 로컬 단일 클라이언트 순차 처리(NFR-U2-C1).
- SDK 기본 async 이벤트 루프 사용. provider는 무상태 → 동시성 위험 없음.

## 3. 직렬화
- U1 도메인 모델 `to_dict()`(결정적, sort_keys 정합) 재사용. 별도 직렬화 라이브러리 불필요.

## 4. 계측
- U1 `application.measurement.measure()` 재사용(US-N1). 추가 의존성 없음.

## 5. 테스트
- **pytest** — provider 단위/예제 테스트(목 U1 서비스). SDK 없이 provider 검증.
- Hypothesis는 U1 도메인에 집중(U2 신규 PBT 대상 얕음, NFR-U2-T2).

## 6. 의존성 (pyproject.toml)
| 의존성 | 범위 | 용도 |
|---|---|---|
| mcp | optional-extra `[mcp]` | MCP stdio 서버 SDK |
| (U1 재사용) agentic_kb.application.* | runtime | 위임 대상 서비스 |
| pytest | dev | provider 테스트 |

> 참고: `[mcp]` extra는 이미 `pyproject.toml`에 optional dependency로 선언됨(U1 단계). 실제 버전 핀은 Code Generation에서 확정.
