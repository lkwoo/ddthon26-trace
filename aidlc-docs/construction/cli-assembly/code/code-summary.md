# Code Generation Summary — U4 CLI & Assembly

> **단계**: CONSTRUCTION – Code Generation · **Unit: U4 CLI & Assembly** · 2026-09-08
> **결과**: `pytest` **52 passed** (U1 28 + U2 9 + U3 9 + U4 6). CLI 스모크(`python -m agentic_kb`, 콘솔 스크립트 `agentic-kb`) 정상.

## 생성 파일
- `src/agentic_kb/config.py` — **AppConfig** + **assemble(config)→AssembledApp** (Composition Root, BR-CA1). U1 서비스(sync/read/query/snippet/update) + U2 `ProviderBundle` + U3 `WebApp` 배선. 포트 추상 의존.
- `src/agentic_kb/__main__.py` — **main(argv)** + **build_parser()**: argparse 서브커맨드(ingest/sync/serve-mcp/serve-web), config→assemble→dispatch, 예외→exit 1, 사용법 오류 exit 2(Humble Object, BR-CA7).
- `src/agentic_kb/adapters/inbound/cli/commands.py` — **cmd_ingest/cmd_sync/cmd_serve_mcp/cmd_serve_web** + **print_report**(US-N7). serve-* 는 지연 import(BR-CA3/CA8). `_require_project`로 미존재 루트 fatal(exit 1).

## 테스트 (`tests/unit/cli/test_cli.py`, 6건)
- assemble 전체 배선, parser 서브커맨드 필수(exit 2), ingest 리포트/exit 0, ingest --json, sync resync(unchanged skip), 미존재 프로젝트 fatal exit 1.

## 커맨드 (진입점)
- `agentic-kb ingest --project <p> --store <kb> [--json]` (US-E1, full)
- `agentic-kb sync --project <p> --store <kb> [--full] [--json]` (US-E5, resync 기본)
- `agentic-kb serve-mcp --project <p> --store <kb>` (US-A6, stdio MCP)
- `agentic-kb serve-web --project <p> --store <kb> [--host] [--port]` (US-H*)

## 설계 준수
- **단일 조립 루트**(BR-CA1), **로직 미보유·위임**(BR-CA2), **명시적 실행**(BR-CA4), **ingest=full/sync=resync**(BR-CA5), **규모·소요 출력**(BR-CA6, US-N7), **부분 실패 격리 exit 0 / 치명 exit 1 / 사용법 exit 2**(BR-CA7), **최소 의존(argparse)·선택 의존 지연 import**(BR-CA8), **무외부호출**(BR-CA9, NFR-C3).

## PBT 컴플라이언스 (U4)
- 배선/I/O 계층 → 신규 PBT 대상 없음. round-trip/invariant는 U1 보증. U4는 PBT-10 예제(종료코드·출력·배선)로 커버. Partial 차단 위반 없음.

## 스토리 커버리지
US-E1(ingest), US-E5(sync), US-A6(serve-mcp), US-H*(serve-web), US-N7(리포트 출력).
