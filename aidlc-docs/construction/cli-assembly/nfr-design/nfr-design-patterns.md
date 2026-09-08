# NFR Design Patterns — U4 CLI & Assembly

> **단계**: CONSTRUCTION – NFR Design · **Unit: U4 CLI & Assembly** · 2026-09-08

## 1. Composition Root
- **패턴**: Composition Root(수동 DI). `config.assemble`가 유일한 구현체 결선 지점. 서비스는 포트 추상에만 의존(BR-CA1, NFR-U4-M1).

## 2. Command Dispatch (Table-driven)
- **패턴**: argparse 서브파서 → 커맨드명→핸들러 매핑. 핸들러는 조립된 컴포넌트에 위임(BR-CA2).

## 3. 지연 의존 격리 (Lazy Import)
- **패턴**: serve-mcp/serve-web 서버 기동은 커맨드 실행 시 지연 import. 미설치 선택 의존(`mcp`)은 안내 메시지로 degrade(NFR-U4-D2, BR-CA8).

## 4. 오류/종료 코드 (Boundary)
- **패턴**: main 경계에서 예외 포착 → stderr + exit 1. 부분 실패는 report로 보고·exit 0. 사용법 오류 exit 2(NFR-U4-R1, BR-CA7).

## 5. Humble Object (진입점)
- **패턴**: `__main__.main`은 argparse→config→assemble→dispatch만. 테스트는 `main(argv)` 및 `assemble()`로 배선·종료코드 검증(NFR-U4-M2/T1).

## 6. 관측성
- sync/ingest는 SyncReport(files/symbols/skipped/failures/elapsed)를 출력(US-N7). 서버 커맨드는 U1 measure 로그 승계.
