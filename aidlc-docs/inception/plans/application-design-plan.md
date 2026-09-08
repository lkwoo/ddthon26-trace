# Application Design Plan — TRACE

**단계**: INCEPTION / Application Design (Part 1 — Planning)
**작성일**: 2026-09-08
**입력**: `requirements.md`, `stories.md`, `execution-plan.md`
**역할**: Software Architect

> 목표: 고수준 **컴포넌트 식별 + 코어 함수 인터페이스 + 서비스 오케스트레이션 + 의존성**을 정의한다. 상세 비즈니스 로직/데이터 모델은 Construction의 Functional Design(유닛별)에서 다룬다.

---

## A. 설계 방법론 (실행 체크리스트)

- [ ] 요구사항 §4(4계층 컴포넌트 A~D)와 §13(코어 인터페이스)를 컴포넌트로 매핑
- [ ] 컴포넌트 책임·인터페이스 정의 (`components.md`)
- [ ] 코어 함수 시그니처 정의 (`component-methods.md`) — 비즈니스 규칙은 Functional Design로 이연
- [ ] 서비스/오케스트레이션 정의 (`services.md`) — analyze_project·analyze_task_impact 파이프라인 조율
- [ ] 컴포넌트 의존성·통신·데이터 흐름 정의 (`component-dependency.md`)
- [ ] 통합 설계 문서 (`application-design.md`)
- [ ] NFR-CORE-001/002(코어·인터페이스 분리, 재사용) & NFR-MAINT-001/002(모듈 분리, 프롬프트 분리) 준수 확인

## B. 필수 산출물

- [ ] `aidlc-docs/inception/application-design/components.md`
- [ ] `aidlc-docs/inception/application-design/component-methods.md`
- [ ] `aidlc-docs/inception/application-design/services.md`
- [ ] `aidlc-docs/inception/application-design/component-dependency.md`
- [ ] `aidlc-docs/inception/application-design/application-design.md`

---

## C. 사전 정렬 (요구사항이 이미 규정한 것 — 확정 전제)

- 4계층: **MCP 서버 인터페이스 / 로컬 지식 엔진 / AI 워크플로우 계층 / 지식 저장소** (§4.1 A~D)
- 코어 함수(§13.2): `scan_project`, `analyze_project`, `list_features`, `get_feature_knowledge`, `get_conflicts`, `analyze_task_impact`
- MCP 서버는 코어 함수를 호출만 하고 AI 로직을 직접 갖지 않음 (NFR-CORE-001)
- 프롬프트는 코드와 분리 저장 (NFR-MAINT-002)
- 언어=Python, LLM=Claude (Requirements Q1/Q2)

---

## D. 확인 질문 (Embedded Questions)

각 `[Answer]:`에 A/B/C/X로 답해주세요.

### Q1. 모듈/패키지 구조
Python 패키지를 어떻게 나눌까요? (NFR-MAINT-001 모듈 분리)

A) 계층별 단일 패키지 `trace/` 하위에 서브모듈: `mcp_server/`, `engine/`(scan·parse), `workflow/`(AI), `knowledge/`(model·store), `conflict/`, `impact/`, `config/`, `prompts/`, `cli/` — 요구사항 모듈 경계 그대로 (권장)

B) 더 얇게 — `server`/`core`/`io` 3묶음으로 단순화

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Q2. 코어 API 호출 스타일
코어 함수와 MCP 도구 핸들러의 결합 방식은?

A) 코어는 순수 함수/서비스 클래스로 두고, MCP 도구 핸들러는 **얇은 어댑터**로 코어를 호출·직렬화만 (NFR-CORE-001/002, CLI 재사용). (권장)

B) 도구 핸들러에 로직 일부 포함(간결하나 재사용성 낮음)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Q3. AI 워크플로우 오케스트레이션
Feature 식별→Claim→Evidence→Conflict→Confidence→지식 생성 파이프라인 구성은?

A) **명시적 순차 파이프라인** — 단계별 함수(step) + 구조화(JSON) 출력 검증, 실패 시 단계 스킵/경고 (NFR-AI-001, FR-ANALYSIS-003). PoC 결정성·디버깅에 유리 (권장)

B) 단일 대형 프롬프트로 한 번에 생성 (단순하나 결정성·부분실패 처리 약함)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Q4. 도구 결과 표현(결과 봉투)
MCP 도구의 구조화 결과 형식은? (NFR-MCP-UX-002 점진적 노출)

A) 공통 result envelope — `{ summary, conflicts, impact, evidence, warnings, meta }` 순서로 핵심 우선 배치 + 사람이 읽는 요약 텍스트 동반 (권장)

B) 도구마다 자유 형식 JSON

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Q5. 지식/캐시 저장 위치
생성 지식과 분석 캐시의 위치는?

A) 대상 프로젝트 밖 TRACE 작업영역(예: 대상경로 기준 `.trace/knowledge/`, `.trace/cache/`) — 대상 저장소를 더럽히지 않음 (권장)

B) 대상 프로젝트 내부 `knowledge/` 에 직접 생성 (요구사항 예시 표기 그대로)

X) Other (please describe after [Answer]: tag below)

[Answer]: 
