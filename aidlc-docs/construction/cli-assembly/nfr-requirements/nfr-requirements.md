# NFR Requirements — U4 CLI & Assembly

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U4 CLI & Assembly** · 2026-09-08
> 조립 루트/진입점. NFR 대부분 U1~U3 승계. 고유 관심사: 최소 의존 CLI·조립 배선·선택 의존 격리.

## 1. Performance
- **NFR-U4-P1**: argparse 파싱 + assemble 배선 오버헤드는 무시 수준. sync/ingest 시간은 U1 파이프라인이 지배(US-N7 elapsed로 관찰).

## 2. Dependencies / Deployability
- **NFR-U4-D1**: CLI는 stdlib `argparse`만 사용. `[project.scripts] agentic-kb`로 콘솔 진입점 제공.
- **NFR-U4-D2**: MCP(`[mcp]`)/web(stdlib) 서버 의존은 해당 커맨드 실행 시 지연 import. `serve-mcp`는 `mcp` 미설치 시 안내 메시지(BR-CA8).

## 3. Maintainability (조립 격리)
- **NFR-U4-M1**: 구현체 바인딩은 `config.assemble` 한 곳. 컴포넌트 교체(예: 저장소 구현)는 조립 루트만 수정(포트 추상 의존, BR-CA1).
- **NFR-U4-M2**: CLI 핸들러는 얇은 위임(BR-CA2). 테스트는 `main(argv)` 종료 코드/출력 + `assemble()` 배선으로 검증.

## 4. Reliability
- **NFR-U4-R1**: 파일 단위 부분 실패는 exit 0 유지·보고(격리), 치명 실패만 exit 1, 사용법 오류 exit 2(BR-CA7).

## 5. Security (Baseline OFF)
- **NFR-U4-S1**: 엔진 무외부호출 유지(NFR-C3). 경로 confinement는 U1(BR-4). serve-web 기본 127.0.0.1 바인드. 시크릿/인증 없음. Security/Resiliency 확장 N/A.

## 6. Testability (PBT Partial)
- **NFR-U4-T1**: CLI/assemble은 배선·I/O 계층 → 예제 테스트(PBT-10)로 커버. round-trip/invariant PBT는 U1 보증.

## 7. 확장 컴플라이언스 요약
| Extension | 상태 | 판정 |
|---|---|---|
| Security Baseline | Disabled | N/A (무외부호출·로컬 바인드·경로 confinement 유지) |
| Resiliency Baseline | Disabled | N/A |
| PBT (Partial) | Enabled | 적용 — 배선 계층, 신규 PBT 대상 없음. PBT-10 예제 커버. 차단 위반 없음. |
