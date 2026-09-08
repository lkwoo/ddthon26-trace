# Business Rules — U4 CLI & Assembly

> 상위 원칙: "조립 격리·위임·최소 의존·명시적 실행". (U3 BR-W* 를 이어 BR-CA* 로 번호화)

## 조립 규칙
- **BR-CA1 (단일 조립 루트)**: 구현체(FileSystemSource/FileSystemKnowledgeStore/default_registry) 선택·주입은 오직 `config.assemble`에서. 서비스/어댑터는 서로 직접 생성하지 않는다(포트 추상 의존).
- **BR-CA2 (로직 미보유)**: CLI 핸들러는 검색/추출/저장/렌더 로직을 구현하지 않는다. 조립된 U1~U3 컴포넌트에 위임한다.
- **BR-CA3 (지연 기동)**: `serve-mcp`/`serve-web`는 해당 커맨드에서만 서버를 기동한다. `ingest`/`sync`는 서버를 띄우지 않는다.

## 실행/동기화 규칙
- **BR-CA4 (명시적 실행, US-E5)**: 동기화는 명시적 커맨드로만 수행된다. 자동/실시간 동기화 없음(MVP 범위).
- **BR-CA5 (ingest=full / sync=resync)**: `ingest`는 full, `sync`는 기본 resync(증분), `--full`로 강제 full. 모두 `SyncService.run`에 mode 매핑.

## 출력/종료 규칙
- **BR-CA6 (규모·소요 출력, US-N7)**: sync/ingest는 files/symbols/skipped/failures/elapsed를 출력한다. `--json`은 `SyncReport.to_dict()`.
- **BR-CA7 (부분 실패 격리)**: 파일 단위 실패는 report.failures로 보고하되 종료 코드는 0(전체 실패 아님, BR-3). 치명 실패만 exit 1. 사용법 오류 exit 2.

## 의존/보안 규칙
- **BR-CA8 (최소 의존)**: CLI는 stdlib `argparse`만 사용. MCP/web 서버는 각 커맨드 실행 시에만 import(선택 의존 격리).
- **BR-CA9 (로컬·무외부호출)**: 조립·실행 전 과정에서 엔진은 LLM/외부 API를 호출하지 않는다(NFR-C3). 경로 confinement는 U1 어댑터(BR-4)가 보증.
