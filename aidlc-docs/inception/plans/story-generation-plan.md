# Story Generation Plan

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – User Stories (Part 1: Planning)
> **작성일**: 2026-09-08
> **역할**: Product Owner
> **입력 산출물**: `aidlc-docs/inception/requirements/requirements.md`, `aidlc-docs/inception/plans/user-stories-assessment.md`

---

## 1. 목적 및 방법론 (Methodology)

요구사항 정의서의 기능/비기능 요구사항(FR-A/H/E/C, NFR-P/C/D/R/T)을 **사용자 중심 스토리**로 변환한다.
- 모든 스토리는 **INVEST** 기준(Independent, Negotiable, Valuable, Estimable, Small, Testable)을 만족한다.
- 스토리 형식: `As a <persona>, I want <capability>, so that <benefit>`.
- 각 스토리에는 **인수 기준(Acceptance Criteria)** 을 Given/When/Then 형태로 부여한다.
- 각 스토리를 페르소나 및 원본 요구사항 ID에 매핑하여 **추적성(traceability)** 을 확보한다.

**핵심 특성**: 본 시스템은 Dual-Interface(에이전트 소비자 + 사람 검토자)이므로, "사용자"에 **비인간 행위자(LLM 에이전트)** 를 1급 페르소나로 포함한다.

---

## 2. 예비 페르소나 (Draft Personas — 확정은 답변 후)

| # | 페르소나 | 유형 | 설명 |
|---|---|---|---|
| P1 | **LLM 에이전트 (Consuming Agent)** | 비인간 | MCP 클라이언트를 통해 지식 베이스를 소비하는 코딩 에이전트. 토큰 효율적이고 정확한 컨텍스트를 필요로 함. |
| P2 | **개발자 (Human Developer / Operator)** | 인간 | 프로젝트를 인제스천하고, 웹 뷰어로 지식을 검토하며, 재동기화를 수행하는 단일 개발자. |
| P3 | **(후보) 지식 관리자 / 리뷰어** | 인간 | 위키 콘텐츠 품질을 검토·검증하는 역할 (P2와 동일인일 수 있음 — Q1에서 확인). |

---

## 3. 실행 체크리스트 (Execution Checklist)

### Part 1 — Planning
- [x] 요구사항 및 assessment 로드 및 분석
- [x] 예비 페르소나 정의
- [x] 스토리 브레이크다운 접근법 옵션 제시 (섹션 5)
- [x] 명확화 질문 작성 (섹션 6)
- [x] 사용자 답변 수집
- [x] 답변 모호성 분석 (필요 시 후속 질문) — 모호성 없음, 후속 질문 불필요
- [x] 계획 승인 획득

### Part 2 — Generation (승인 후 실행)
- [x] `personas.md` 생성 — 페르소나 아키타입 및 특성
- [x] `stories.md` 생성 — INVEST 기준 스토리 + 인수 기준
- [x] 각 스토리에 인수 기준(Given/When/Then) 포함
- [x] 페르소나 ↔ 스토리 매핑
- [x] 스토리 ↔ 요구사항 ID(FR/NFR) 추적성 매핑
- [x] INVEST 준수 검증
- [x] 완료 메시지 제시 및 승인 획득 (1차 생성 → 변경 요청 → 수정본 승인)

---

## 4. 필수 산출물 (Mandatory Artifacts)
- [x] `aidlc-docs/inception/user-stories/stories.md`
- [x] `aidlc-docs/inception/user-stories/personas.md`

---

## 5. 스토리 브레이크다운 접근법 옵션 (질문 Q2에서 선택)

| 접근법 | 설명 | 장점 | 트레이드오프 |
|---|---|---|---|
| **A. Persona-Based** | 페르소나(에이전트 / 개발자)별로 스토리를 그룹화 | Dual-Interface 특성이 명확히 드러남 | 서브시스템 경계와 어긋날 수 있음 |
| **B. Feature-Based** | 시스템 기능(Resources, Tools, Ingestion, Viewer)별 그룹화 | 요구사항 FR과 1:1 매핑 용이 | 사용자 관점이 약해질 수 있음 |
| **C. User Journey-Based** | 워크플로(인제스천 → 검토 → 에이전트 소비 → 재동기화) 흐름별 그룹화 | 실제 사용 흐름 이해에 유리 | 스토리 경계가 겹칠 수 있음 |
| **D. Epic-Based** | 상위 Epic(예: Agent Interface, Human Interface, Knowledge Engine) 아래 하위 스토리 | 3개 서브시스템 구조와 정합, 확장 용이 | 초기 구조화 비용 |
| **E. Hybrid (Epic + Persona)** | Epic(서브시스템)으로 상위 구조 + 각 스토리에 페르소나 태깅 | 구조 정합성 + 사용자 관점 모두 확보 | 약간의 중복 |

---

# 6. 명확화 질문 (Clarification Questions)

아래 각 질문의 `[Answer]:` 태그 뒤에 **letter 선택지**를 적어주세요. 보기와 맞지 않으면 마지막 `Other` 를 선택하고 설명을 덧붙여 주세요.

## Question 1
페르소나 구성을 어떻게 할까요? (사람 사용자 역할 분리 여부)

A) 2개 페르소나 — LLM 에이전트(P1) + 단일 개발자(P2). "검토"도 개발자가 겸함 (요구사항의 단일 개발자 로컬 모델에 부합)

B) 3개 페르소나 — LLM 에이전트(P1) + 개발자/운영자(P2) + 별도 리뷰어(P3)

C) LLM 에이전트를 세분화 — 온보딩 에이전트 vs 작업 수행 에이전트로 구분 + 개발자(P2)

D) Other (please describe after [Answer]: tag below)

[Answer]: 2개 페르소나 — LLM 에이전트(P1) + 단일 개발자(P2). "검토"도 개발자가 겸함 (요구사항의 단일 개발자 로컬 모델에 부합)

## Question 2
스토리 브레이크다운 접근법은 무엇으로 할까요? (섹션 5 참고)

A) Persona-Based (에이전트/개발자별 그룹화)

B) Feature-Based (기능별 그룹화)

C) User Journey-Based (사용 흐름별 그룹화)

D) Epic-Based (서브시스템 Epic별)

E) Hybrid — Epic(서브시스템) 구조 + 스토리별 페르소나 태깅 (권장)

F) Other (please describe after [Answer]: tag below)

[Answer]: Hybrid — Epic(서브시스템) 구조 + 스토리별 페르소나 태깅 (권장)

## Question 3
스토리 세분화(Granularity) 수준은 어느 정도로 할까요?

A) 큰 단위 (서브시스템당 소수의 굵은 스토리, 빠른 개요 우선)

B) 중간 단위 (기능(FR)당 1~2개 스토리, MVP 구현에 적합) (권장)

C) 세밀한 단위 (기능을 여러 작은 스토리로 분해, 상세 추적성 우선)

D) Other (please describe after [Answer]: tag below)

[Answer]: 중간 단위 (기능(FR)당 1~2개 스토리, MVP 구현에 적합) (권장)

## Question 4
인수 기준(Acceptance Criteria) 형식은 무엇으로 할까요?

A) Given/When/Then (Gherkin 스타일) (권장 — 테스트 가능, PBT/기능 테스트 매핑 용이)

B) 체크리스트 형식 (bullet 목록의 검증 항목)

C) 서술형 조건 문장

D) Other (please describe after [Answer]: tag below)

[Answer]: Given/When/Then (Gherkin 스타일) (권장 — 테스트 가능, PBT/기능 테스트 매핑 용이)

## Question 5
스토리 범위(Scope)를 MVP로 한정할까요, 아니면 후속(post-MVP) 항목도 포함할까요?

A) MVP 범위만 (임베딩 검색, PDF/HTML 인제스천 등 후속 기능은 스토리에서 제외)

B) MVP를 주(主)로 하되, 후속 기능은 별도 "Backlog/Future" 섹션에 요약 스토리로 표기 (권장)

C) MVP + 후속 기능 모두 동등하게 상세 스토리로 작성

D) Other (please describe after [Answer]: tag below)

[Answer]: MVP를 주(主)로 하되, 후속 기능은 별도 "Backlog/Future" 섹션에 요약 스토리로 표기 (권장)

## Question 6
비기능 요구사항(NFR: 응답 1초, 토큰 효율, LLM 제공자 추상화, PBT 등)을 스토리에 어떻게 반영할까요?

A) 관련 기능 스토리의 인수 기준 안에 NFR 제약을 포함 (예: "1초 이내 응답")

B) 별도의 NFR/기술 스토리(technical stories)로 분리 작성

C) 두 방식 병행 — 기능 스토리 인수 기준에 반영 + 교차 관심사(cross-cutting)는 별도 NFR 스토리로 (권장)

D) Other (please describe after [Answer]: tag below)

[Answer]: 두 방식 병행 — 기능 스토리 인수 기준에 반영 + 교차 관심사(cross-cutting)는 별도 NFR 스토리로 (권장)

## Question 7
각 스토리에 우선순위/구현 순서 표기를 포함할까요?

A) 예 — MoSCoW(Must/Should/Could/Won't) 등 우선순위 라벨 포함

B) 예 — 단순 우선순위(High/Medium/Low)만 포함

C) 아니오 — 우선순위는 후속 단계(Workflow/Units)에서 다루고 스토리에는 미포함 (권장, 방법론상 우선순위는 별도 단계)

D) Other (please describe after [Answer]: tag below)

[Answer]: 아니오 — 우선순위는 후속 단계(Workflow/Units)에서 다루고 스토리에는 미포함 (권장, 방법론상 우선순위는 별도 단계)

## Question 8
스토리 문서 언어는 무엇으로 할까요?

A) 한국어 (요구사항 정의서와 일관) (권장)

B) 영어

C) 한국어 + 영어 병기

D) Other (please describe after [Answer]: tag below)

[Answer]: 한국어 (요구사항 정의서와 일관) (권장)

---

## 7. 참고
- 본 단계는 **스토리 구조·형식·페르소나** 결정에 집중합니다. 기술 구현 상세, 스프린트/타임라인, 개발 태스크는 다루지 않습니다(후속 단계에서 처리).
- 모든 `[Answer]:` 태그가 채워진 후 답변의 모호성을 분석하고, 필요 시 후속 질문을 별도 파일로 만든 뒤, 계획 승인을 요청합니다.
