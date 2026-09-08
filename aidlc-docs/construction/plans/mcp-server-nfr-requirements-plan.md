# NFR Requirements Plan — U2 MCP Server

> **Unit**: U2 MCP Server · **Depends on**: U1 · **Stories**: US-A1/2/3/4/5/6, US-N1
> 얇은 인바운드 어댑터의 NFR은 대부분 U1에서 승계. U2 고유 관심사는 전송(stdio) 안정성·표면 지연·프로토콜 준수.

## Steps
- [x] S1. Functional Design 분석 (mcp-server/functional-design/*)
- [x] S2. NFR 질문 + 권장안 채택(자동)
- [x] S3. nfr-requirements.md 생성
- [x] S4. tech-stack-decisions.md 생성 (mcp SDK 선정)
- [x] S5. 완료 메시지 + 승인(자동 채택)

## 질문 및 채택 답변 (권장안 자동 채택)

### Q1. 성능 목표 (US-N1/NFR-P1)
- A. Tool/Resource 표면 오버헤드는 U1 위임 시간에 무시할 수준(<수 ms), 전체 조회 1초 목표는 U1이 충족 **(권장)**
- B. U2 자체 SLA 별도 정의
- **[Answer]: A** — U2는 위임+직렬화만. 계측으로 elapsed_ms 관찰.

### Q2. 가용성/장애 격리
- A. 단일 요청 실패가 서버를 중단시키지 않음(예외 포착→isError/not-found), 프로세스는 상시 상주 **(권장)**
- B. 실패 시 종료
- **[Answer]: A** — BR-M8 준수. 로컬 stdio 단일 프로세스.

### Q3. MCP SDK 선택 (Tech Stack)
- A. 공식 `mcp` Python SDK(stdio 서버) — optional-extra `[mcp]` **(권장)**
- B. 프로토콜 수동 구현
- **[Answer]: A** — 표준 준수·유지보수. provider 로직은 SDK 독립 유지(NFR-C2).

### Q4. 동시성 모델
- A. stdio 단일 클라이언트·순차 처리(로컬 단일 사용자, NFR-E1) **(권장)**
- B. 멀티 커넥션/비동기 풀
- **[Answer]: A** — MVP 로컬 단일 사용자. SDK 기본 async 루프 사용하되 상태 공유 없음(무상태 provider).

### Q5. 보안 (Security Baseline OFF)
- A. 최소 위생만: 경로 confinement는 U1 어댑터(BR-4)가 보증, 시크릿/인증 없음, 로컬 전용 **(권장)**
- B. 인증/인가 추가
- **[Answer]: A** — 로컬 stdio, 외부 노출 없음. 확장은 Disabled(N/A).

### Q6. 테스트 전략
- A. provider 단위 테스트(목 U1 서비스) + URI 파싱/오류 매핑 예제 테스트, PBT는 U1 도메인에 집중(U2는 순수 매핑이라 PBT 대상 얕음) **(권장)**
- B. U2에도 광범위 PBT
- **[Answer]: A** — PBT Partial 범위상 U2 매핑은 예제 테스트로 충분. round-trip은 U1이 보증.
