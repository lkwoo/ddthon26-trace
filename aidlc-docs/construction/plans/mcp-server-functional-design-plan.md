# Functional Design Plan — U2 MCP Server

> **Unit**: U2 MCP Server (inbound adapter) · **Depends on**: U1 Engine Core
> **Stories**: US-A1, US-A2, US-A3, US-A4, US-A5, US-A6, US-N1 (surface latency)
> **Principle**: 얇은 인바운드 어댑터 — 로직 미보유, U1 Application 서비스로 위임만. 엔진은 LLM 미호출(NFR-C3).

## Steps
- [x] S1. Unit 컨텍스트/스토리 분석 (unit-of-work.md, stories.md US-A*)
- [x] S2. 설계 질문 생성 + 권장안 채택(자동 진행)
- [x] S3. domain-entities.md — MCP 표면 개념 모델(Resource URI 스킴, Tool I/O 페이로드, Prompt 템플릿)
- [x] S4. business-logic-model.md — Resources/Tools/Prompts 제공자 위임 흐름, 오류·계측
- [x] S5. business-rules.md — URI 파싱/검증, 오류 매핑, 계측, 위임 규칙
- [x] S6. 완료 메시지 + 승인(자동 채택)

## 설계 질문 및 채택 답변 (권장안 자동 채택)

### Q1. MCP Resource URI 스킴
- A. `agentic-kb://structure`, `agentic-kb://summary/{target}`, `agentic-kb://relationships[/{target}]` (커스텀 스킴, 계층적) **(권장)**
- B. 단일 flat 이름공간
- **[Answer]: A** — 리소스 종류별 명확한 계층 URI. `{target}`는 프로젝트 상대 경로/심볼 id.

### Q2. Tool 집합과 이름
- A. `query`, `snippet`, `update_note`, `sync` 4개 (US-A2/A3/A4 + 운영 sync) **(권장)**
- B. query/snippet/update만(수동 sync)
- **[Answer]: A** — U1 서비스 1:1 매핑. `sync`는 US-E/US-N7 재동기화 표면.

### Q3. 미존재/오류 응답 방식 (AC-4, US-A2 AC-3, US-A4 AC-3)
- A. Resource 미존재→MCP "not found"류 오류(서버 미중단); Tool 검증오류→구조화 `isError` 결과(엔진 미변경) **(권장)**
- B. 모두 예외 throw
- **[Answer]: A** — 서버는 절대 중단되지 않음. Tool은 결과 객체에 오류를 담아 반환.

### Q4. Prompts 범위 (US-A5)
- A. `onboarding`(전체 맥락) + `task`(인자 `task_kind`로 작업별) 2종 **(권장)**
- B. onboarding만
- **[Answer]: A** — 템플릿은 구조/요약 리소스를 참조하도록 지시하는 텍스트(정적 조합, LLM 미호출).

### Q5. 지연 계측 (US-N1)
- A. 각 Tool/Resource 핸들러를 U1 `measure()` 컨텍스트로 감싸 elapsed_ms 로깅 **(권장)**
- B. 계측 없음
- **[Answer]: A** — 표면 계측만, 서버 로직 무추가.

### Q6. MCP 프레임워크 바인딩 위치
- A. 공식 `mcp` Python SDK를 어댑터에서 사용하되 provider 함수는 SDK 독립(순수 매핑 함수) + 얇은 SDK 바인딩 분리 **(권장)**
- B. SDK에 직접 결합
- **[Answer]: A** — provider 매핑 로직은 SDK 없이 테스트 가능(NFR-C2 유연성), 바인딩은 `server.py`에 격리.
