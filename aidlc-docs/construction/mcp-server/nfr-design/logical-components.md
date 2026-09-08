# Logical Components — U2 MCP Server

> **단계**: CONSTRUCTION – NFR Design · **Unit: U2 MCP Server** · 2026-09-08

## 1. 논리 컴포넌트 맵

| 컴포넌트 | 계층 | 책임 | NFR 패턴 |
|---|---|---|---|
| adapters.inbound.mcp.resources (ResourcesProvider) | inbound adapter | URI 파싱 → U1 read 서비스 위임 → to_dict | Adapter/Delegation, Null→not-found, Measure |
| adapters.inbound.mcp.tools (ToolsProvider) | inbound adapter | query/snippet/update_note/sync 디스패치·인자 검증 | Delegation, Error translation, Measure |
| adapters.inbound.mcp.prompts (PromptsProvider) | inbound adapter | onboarding/task 템플릿 조합 | Pure function(정적) |
| adapters.inbound.mcp.server (StdioServer) | inbound adapter (binding) | mcp SDK 등록 + stdio 기동 | Humble Object, SDK 격리 |

## 2. 의존 방향
- `mcp.resources/tools/prompts` → U1 `application.*` 서비스 인터페이스(포트 방향 안쪽). SDK 미의존.
- `mcp.server` → SDK + provider. 조립 시 U4 `config.py`가 U1 서비스 구현을 주입.
- 순환 없음: U2 → U1 (단방향). U1은 U2를 참조하지 않음.

## 3. 인프라성 논리 컴포넌트 판정
- **큐/브로커, 분산캐시, 서킷브레이커, LB/오토스케일, 인증 게이트**: 전부 **N/A** — 로컬 stdio 단일 프로세스·단일 사용자, 외부 호출 없음(NFR-E1, NFR-C3).

## 4. 관측성
- Measurement 훅(U1 재사용)으로 표면 지연 로깅. 별도 지표 저장소 없음.
- `sync` Tool은 SyncReport를 그대로 노출(US-N7 규모·소요 가시성).

## 5. 배치(파일)
```
src/agentic_kb/adapters/inbound/mcp/
├── __init__.py
├── resources.py   # ResourcesProvider (SDK 독립)
├── tools.py       # ToolsProvider (SDK 독립)
├── prompts.py     # PromptsProvider (SDK 독립)
└── server.py      # StdioServer (mcp SDK 바인딩)
tests/unit/mcp/    # provider 단위/예제 테스트 (목 U1 서비스)
```
