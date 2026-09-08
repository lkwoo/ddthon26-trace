# NFR Requirements — U2 MCP Server

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U2 MCP Server** · 2026-09-08
> U2는 얇은 인바운드 어댑터로, 대부분의 NFR을 U1에서 승계한다. 아래는 U2 고유/승계 NFR을 정리한다.

## 1. Performance (US-N1 / NFR-P1)
- **NFR-U2-P1**: Tool/Resource 핸들러의 U2 자체 오버헤드(파싱+직렬화)는 U1 위임 시간 대비 무시 가능(<수 ms 목표). 전체 조회 1초 목표(NFR-P1)는 U1이 충족.
- **NFR-U2-P2**: 모든 핸들러는 `measure()`로 elapsed_ms를 로깅하여 지연 관찰 가능(US-N1 표면 계측).

## 2. Availability / Fault Isolation
- **NFR-U2-A1**: 단일 요청 실패(잘못된 URI/인자/하위 예외)는 `isError`/not-found로 변환되며 **서버 프로세스를 종료시키지 않는다**(BR-M4/M8, US-A1 AC-4).
- **NFR-U2-A2**: 서버는 로컬 stdio 상주 프로세스로, 외부 서비스 의존 없이 기동·동작(US-A6 AC-2, NFR-E1).

## 3. Concurrency
- **NFR-U2-C1**: MVP는 로컬 단일 사용자·단일 클라이언트 순차 처리. provider는 무상태(요청별 U1 서비스 위임)로 공유 가변 상태 없음.

## 4. Security (Baseline OFF — 최소 위생)
- **NFR-U2-S1**: 경로 기반 접근은 U1 `FileSystemSource`의 confinement(BR-4)가 최종 보증. U2는 `{target}`를 그대로 전달만 한다.
- **NFR-U2-S2**: 인증/인가/시크릿 없음(로컬 stdio, 외부 노출 없음). Security/Resiliency Baseline은 Disabled → 본 단계 N/A.
- **NFR-U2-S3**: 엔진 LLM/외부 API 미호출 원칙 유지(NFR-C3). U2는 어떤 외부 호출도 하지 않는다.

## 5. Maintainability / Extensibility (NFR-C2)
- **NFR-U2-M1**: provider(resources/tools/prompts) 매핑 로직은 MCP SDK에 독립 → 단위 테스트 가능. SDK 바인딩은 `server.py`에 격리.
- **NFR-U2-M2**: Tool/Resource 추가는 provider에 매핑 항목 추가로 확장(코어 U1 무수정).

## 6. Testability (PBT Partial)
- **NFR-U2-T1**: provider 단위 테스트는 목 U1 서비스 주입으로 수행. URI 파싱·오류 매핑·Tool 디스패치를 예제 테스트로 검증(PBT-10).
- **NFR-U2-T2**: 직렬화 round-trip(PBT-02)은 U1 도메인에서 이미 보증되므로 U2에서 재검증하지 않는다. U2 PBT 대상은 얕음(순수 매핑) → Partial 범위에서 예제 테스트로 충분.

## 7. 확장 컴플라이언스 요약
| Extension | 상태 | 판정 |
|---|---|---|
| Security Baseline | Disabled | N/A |
| Resiliency Baseline | Disabled | N/A |
| PBT (Partial) | Enabled | 적용 — U2는 매핑 계층이라 신규 PBT 대상 얕음. PBT-02/03은 U1이 보증, U2는 PBT-10 예제로 커버. 차단 위반 없음. |
