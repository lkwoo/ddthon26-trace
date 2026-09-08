# 요구사항 확인 질문 (Requirements Verification Questions)

**작성일**: 2026-09-08
**대상 문서**: requirments/trace-requirements.md
**목적**: 요구사항 문서 §23(미해결 결정)와 확장(extension) opt-in을 확정해 Construction 착수 근거를 마련합니다.

**응답 방법**: 각 질문의 `[Answer]:` 태그 뒤에 A/B/C/X 중 하나(또는 X + 설명)를 적어주세요.

---

## Q1. MCP 서버 구현 언어 / SDK (§23-2)
TRACE MCP 서버와 로컬 엔진을 어떤 스택으로 구현할까요?

A) Python + 공식 Python MCP SDK (`mcp`) — 파싱/AI 생태계(pydantic, PyYAML 등)가 풍부, PoC 속도에 유리

B) TypeScript + 공식 TypeScript MCP SDK — Node 생태계, Claude Code와 동일 계열 도구 경험

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q2. LLM 제공자 / 모델 (§23-3)
AI 워크플로우(Feature 식별, Claim 추출, Conflict 검출, Impact 분석)에 사용할 모델은?

A) Anthropic Claude (최신 모델, 예: Claude Sonnet 5) — 요구사항의 구조화 출력·그라운딩에 적합, Claude Code와 동일 계열

B) 로컬/오픈 모델 (예: Ollama 경유) — 완전 로컬, 오프라인 시연 가능하나 구조화 출력 안정성 낮음

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q3. 문서 파서 범위 — PDF/DOCX/PPTX (§23-5, FR-PROJECT-002)
P0 데모에서 문서 파싱 범위를 어디까지 잡을까요?

A) P0는 Markdown/텍스트 + OpenAPI(YAML/JSON) + SQL + 설정 + 소스/테스트만. PDF/DOCX/PPTX는 P1(시간 허용 시)

B) PDF까지 P0에 포함 (요구사항 PDF를 Hero 교차소스 근거로 확실히 쓰기 위해)

C) PDF/DOCX/PPTX 전부 P0에 포함

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Q4. Feature 검출 방식 (§23-8)
Hero Feature(Owner Registration 등) 식별을 어떻게 할까요?

A) 완전 자동 — AI가 자산에서 Feature를 스스로 식별 (일반성 높지만 데모 안정성 변동 가능)

B) 데모 설정 보조 — 데모 대상 Feature 힌트를 설정으로 제공하고 AI가 지식을 채움 (NFR-AI-004 시연 안정성 우선)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q5. 시연 안정성 — 캐시 & 폴백 CLI (§23-9, §23-10)
라이브 AI 실행 실패에 대비한 폴백 전략은? (NFR-AI-004, FR-DEMO-002)

A) 둘 다 구현 — 분석 결과 캐시(P1) + 얇은 폴백 CLI(P1). 시연 신뢰성 최대

B) 캐시만 구현 — 캐시된 분석 결과를 폴백으로 사용, 별도 CLI는 생략

C) 둘 다 생략 — 라이브 MCP 흐름만 P0로 집중 (시간 절약)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q6. 데모 데이터셋 (§18, §23)
Hero 시나리오("Owner 등록에 SMS 인증 추가")를 위한 대상 프로젝트는?

A) Spring Petclinic REST(또는 선별 부분집합) + 의도적 충돌을 심은 합성 요구사항 문서. 요구사항 §18 권장안 그대로

B) 더 작은 자체 합성 미니 프로젝트 — 저장소를 가볍게 유지하고 충돌을 완전 통제

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q7. 프로젝트 명칭 (§23-1)
결과물의 최종 이름을 `TRACE`로 확정할까요?

A) 예 — `TRACE`로 확정

B) 아니오 — 다른 이름 사용 (X에 기입)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q8. (확장) Security Baseline
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Q9. (확장) Resiliency Baseline
Should the resiliency baseline be applied to this project? (AWS Well-Architected Reliability Pillar 기반 설계 지침)

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q10. (확장) Property-Based Testing
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q11. (Resiliency 확장 필수) RTO/RPO 목표 및 재해복구(DR) 전략
Resiliency 확장(Q9=A)의 RESILIENCY-02 룰은 요구사항 확정 전 RTO/RPO 목표를 묻도록 요구합니다.
What are your Recovery Time Objective (RTO) and Recovery Point Objective (RPO) goals?

> **맥락 참고**: TRACE는 로컬 stdio MCP 서버 PoC(2일, 클라우드 인프라·멀티리전 없음, §2.1)입니다. 이 경우 대부분의 Resiliency 룰(멀티존/멀티리전/DR/백업)은 **N/A**가 되며, 로컬 재실행·재분석으로 복구합니다. 그래서 **E**가 자연스러운 선택입니다.

A) RPO/RTO: Hours — Backup & Restore. Lowest cost.

B) RPO/RTO: 10s of minutes — Pilot Light.

C) RPO/RTO: Minutes — Warm Standby.

D) RPO/RTO: Near real-time — Multi-site Active/Active.

E) N/A — Single-region(로컬 단일 프로세스) 로 충분, cross-region DR 불필요. (PoC 권장)

X) Other (please describe after [Answer]: tag below)

[Answer]: E
