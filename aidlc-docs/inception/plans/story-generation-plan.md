# Story Generation Plan — TRACE

**단계**: INCEPTION / User Stories (Part 1 — Planning)
**작성일**: 2026-09-08
**역할**: Product Owner
**입력**: `aidlc-docs/inception/requirements/requirements.md`, 원천 요구사항 §3(페르소나)·부록 B(Hero)

---

## A. 스토리 개발 방법론 (실행 체크리스트)

- [x] 요구사항의 FR/NFR를 페르소나별 사용자 흐름으로 재구성
- [x] 각 스토리를 INVEST(Independent·Negotiable·Valuable·Estimable·Small·Testable)로 작성
- [x] 각 스토리에 수용 기준(Given/When/Then) 부여 (Q4=A)
- [x] 스토리 ↔ FR/NFR ID ↔ UOW 매핑(추적성) 표기 (Q5=A)
- [x] `personas.md` 생성 — 3개 페르소나 + AI 에이전트 액터 (Q1=A)
- [x] `stories.md` 생성 — Epic(=UOW) → Story 구조 (Q3=A)
- [x] Hero 시나리오를 E2E 통과 스토리로 명시 (US-06.1)

## B. 필수 산출물

- [x] `aidlc-docs/inception/user-stories/personas.md`
- [x] `aidlc-docs/inception/user-stories/stories.md`

---

## C. 스토리 구성(breakdown) 접근법 — 옵션과 트레이드오프

| 접근법 | 설명 | 이 프로젝트 적합도 |
|---|---|---|
| **User Journey-Based** | 사용자 흐름(온보딩→조회→충돌→영향분석)을 따라 스토리 구성 | Hero 시나리오와 직결, 사용성 평가에 유리 |
| **Feature-Based** | 시스템 기능/도구 중심(analyze_project, get_conflicts…) | MCP 도구 계약과 1:1, UOW 매핑 쉬움 |
| **Persona-Based** | 페르소나별로 묶음 | 3개 페르소나 차이 부각 |
| **Domain-Based** | 비즈니스 도메인 중심 | 단일 도메인이라 이점 적음 |
| **Epic-Based** | Epic(UOW) 하위에 스토리 | 계층 추적성 최고 |

> **PO 권장**: **Epic(=UOW) 기반 + 각 Epic 내부는 User-Journey 흐름** 하이브리드. UOW-01~06을 Epic으로 두고, Epic 안에서 페르소나 흐름 순서로 스토리를 배열하면 추적성(§21)과 사용성(Hero 흐름)을 동시에 만족. → **Q3에서 확정**

---

## D. 확인 질문 (Embedded Questions)

각 `[Answer]:` 뒤에 A/B/C/X로 답해주세요. 모두 채워지면 Part 2(생성)로 진행합니다.

### Q1. 페르소나 범위
스토리에 등장시킬 액터(actor)를 어디까지 둘까요?

A) 3개 사람 페르소나(개발자·유지보수자·PM) + **AI 코딩 에이전트(Claude Code)를 1급 액터로** 명시 — 실제 상호작용 구조 반영 (권장)

B) 3개 사람 페르소나만. 에이전트는 도구 호출 메커니즘으로만 취급

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Q2. 스토리 세분도(granularity)
스토리 크기를 어느 수준으로?

A) 중간 세분도 — 도구/사용자 흐름 단위(예: "충돌을 조회한다"). Epic당 3~6개. PoC 2일에 적합 (권장)

B) 세밀 — 수용 기준별로 잘게 분리(스토리 다수)

C) 큰 단위 — Epic ≈ Story (개수 최소)

X) Other (please describe after [Answer]: tag below)

[Answer]: A 

### Q3. 구성 접근법 (위 C 표 참조)
A) Epic(=UOW) 기반 + Epic 내부 User-Journey 하이브리드 (PO 권장)

B) Feature-Based (MCP 도구 중심)

C) Persona-Based

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Q4. 수용 기준 형식
A) **Given/When/Then** (Gherkin 스타일) — PBT/예제 테스트로 옮기기 쉬움 (권장)

B) 체크리스트형 불릿

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Q5. 추적성 표기
스토리에 FR/NFR·UOW ID 매핑을 넣을까요? (원천 §21 AI-DLC 추적성 요구)

A) 예 — 각 스토리에 `Implements: FR-..., NFR-...` 및 `UOW-..` 표기 (권장, 평가기준 1번 대응)

B) 아니오 — 스토리 텍스트만

X) Other (please describe after [Answer]: tag below)

[Answer]: A
