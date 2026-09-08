# Logical Components — U4 CLI & Assembly

> **단계**: CONSTRUCTION – NFR Design · **Unit: U4 CLI & Assembly** · 2026-09-08

## 1. 논리 컴포넌트 맵

| 컴포넌트 | 계층 | 책임 | NFR 패턴 |
|---|---|---|---|
| config (AppConfig, assemble, AssembledApp) | assembly root | 설정 + 구현체 바인딩·주입 | Composition Root |
| __main__ (main, build_parser) | entry point | argparse → config → assemble → dispatch | Humble Object, Boundary error handling |
| adapters.inbound.cli.commands | inbound adapter | 서브커맨드 핸들러(ingest/sync/serve-mcp/serve-web) | Command dispatch, Lazy import, Delegation |

## 2. 의존 방향
- `__main__` → `config` → U1 서비스/어댑터 + U2 `ProviderBundle`/`StdioServer` + U3 `WebApp`/`WebServer`.
- `commands` → 조립된 `AssembledApp`. 단방향(U4 → U1/U2/U3). 순환 없음.

## 3. 인프라성 논리 컴포넌트 판정
- **큐/브로커, 캐시, LB, 인증 게이트, 컨테이너 오케스트레이션**: 전부 **N/A** — 로컬 CLI 진입점, 배포 인프라 없음(Infrastructure Design SKIP 사유와 정합).

## 4. 배치(파일)
```
src/agentic_kb/
├── config.py       # AppConfig + assemble() + AssembledApp
├── __main__.py     # main(argv), build_parser()
└── adapters/inbound/cli/
    ├── __init__.py
    └── commands.py # cmd_ingest/cmd_sync/cmd_serve_mcp/cmd_serve_web/print_report
tests/unit/cli/     # main(argv)/assemble 예제 테스트
```
