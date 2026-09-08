# Functional Design Plan — U1 Engine Core

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: CONSTRUCTION – Functional Design (per-unit) · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08
> **입력 산출물**: `unit-of-work.md`, `unit-of-work-story-map.md`, `component-methods.md`, `requirements.md`, `stories.md`
> **범위 스토리**: US-E1~E5, US-A2/A3/A4(서비스 로직), US-N2~N7
> **원칙**: 기술 비종속(도메인 순수·결정적·LLM 미호출·I/O 없음), 헥사고날 경계 준수

---

## 0. 자동 진행 안내

사용자가 **모든 승인 게이트에서 권장사항 자동 채택**을 위임함. 아래 질문은 권장 답안을 `[Answer]:`에 미리 채택하여 진행한다(각 항목에 근거 명시).

---

## 1. 설계 대상 (Scope)

U1은 순수 도메인 + 포트 + 아웃바운드 어댑터 + Application 서비스를 포함한다. 본 Functional Design은 다음 상세를 확정한다:
- **도메인 엔티티**: 필드·타입·불변식·직렬화 계약(round-trip 대상)
- **비즈니스 로직**: 그래프 구성, 구조 추출, 청킹, 검색, 동기화 파이프라인, 읽기 병합, 노트 갱신 알고리즘
- **비즈니스 규칙**: 검증·예외 정책, 엔진 우선 충돌 정책, 재동기화 시 에이전트 노트 보존, 미지원 포맷 스킵, 결정성 규칙

---

## 2. 결정 질문 (Functional Design Questions — 권장안 자동 채택)

### Q1 — 그래프 심볼 ID 스킴 (Domain Model)
심볼 고유 ID를 어떻게 구성할까?

A) **`<relpath>::<kind>::<qualified_name>`** 형태의 결정적 문자열 (권장 — 재현성·diff 친화, US-E4/N5)
B) 콘텐츠 해시 기반 ID
C) 순번 정수 ID

[Answer]: **A** — 파일 상대경로 + 종류 + 정규화 이름 조합. 결정적이고 사람이 읽을 수 있으며 diff 노이즈 최소(US-N5 AC-2, US-E2).

### Q2 — 검색 관련도(score) 산정 (Business Logic)
키워드 검색 관련도 점수는?

A) **결정적 가중 매칭** — 이름 정확일치 > 이름 부분일치 > 시그니처/docstring 매칭 > 본문 매칭, 동점은 안정 정렬(경로 오름차순) (권장, LLM/랜덤 없음)
B) TF-IDF 통계 스코어
C) 단순 부분문자열 포함 여부(불리언)

[Answer]: **A** — 결정성(NFR-C3)·설명가능성 확보. TF-IDF는 후속 확장 여지로 남김.

### Q3 — 스니펫 예산 초과 시 축약 전략 (Business Logic, US-A3 AC-3)
토큰 예산 초과 시 축약 우선순위는?

A) **대상 심볼 본문 우선 보존 → 시그니처/docstring 유지 → 주변 문맥 절단 → `truncated=True`** (권장)
B) 균등 비율 축소
C) 앞부분부터 단순 절단

[Answer]: **A** — 의미 완결성 우선(US-A3 AC-1), 절단 표시로 예산 관리(AC-2).

### Q4 — 토큰 추정 방식 (Business Logic, NFR-C3 결정성)
`estimate_tokens`는?

A) **결정적 휴리스틱**(문자수/4 + 공백·기호 보정)으로 외부 토크나이저 비의존 (권장 — 로컬·결정적)
B) 외부 tokenizer 라이브러리(tiktoken 등) 의존

[Answer]: **A** — 엔진 로컬성/결정성(NFR-C3) 및 최소 의존 원칙 준수. 근사치이나 예산 관리 목적에 충분.

### Q5 — 에이전트 노트 vs 엔진 요약 병합 표현 (US-A1.2 / US-A4 / FR-C1)
`get_summary`가 반환하는 병합 요약 구조는?

A) **`MergedSummary{ engine: ModuleSummary, agent_notes: list[AgentNote], provenance }`** — 출처 분리 유지, 엔진 우선 정책 명시 (권장)
B) 하나의 텍스트로 평면 병합
C) 에이전트 노트만 반환

[Answer]: **A** — 엔진 우선 재생성 시 에이전트 노트 보존/구분 가능(FR-C1), 출처 투명성(US-H4 AC-2).

### Q6 — 재동기화 시 에이전트 노트 보존 (US-E5 / FR-C1 / Q6 별도 네임스페이스)
resync 시 노트 처리 규칙은?

A) **엔진 산출물(구조/요약/그래프)만 재생성·덮어쓰기, 에이전트 노트는 별도 네임스페이스에 보존** (권장, 확정된 Q6 정책)
B) 전체 삭제 후 재생성(노트도 삭제)

[Answer]: **A** — 엔진 우선(FR-C1)이되 에이전트 노트는 별도 저장소 유지. 대상 심볼이 소스에서 사라지면 노트는 orphan으로 표시(삭제하지 않음).

### Q7 — 파싱/수집 실패 처리 (US-E1 AC-2, US-E2 AC-3)
개별 파일 실패 시?

A) **해당 파일 건너뛰고 SyncReport.failures/skipped에 사유 기록, 전체 파이프라인 계속** (권장)
B) 전체 중단

[Answer]: **A** — 부분 실패 격리(US-E2 AC-3), 규모/실패 리포트(US-N7).

### Q8 — PBT 대상 순수 함수 지정 (US-N6, NFR-T)
차단 PBT(PBT-02/03) 대상은?

A) **round-trip(PBT-02)**: 모든 도메인 모델 `to_dict`/`from_dict`; **invariant(PBT-03)**: `chunking.select_snippet`(예산 불초과·비공백), `graph_builder.build`(노드/엣지 결정성·중복없음), `estimate_tokens`(단조·비음수) (권장)
B) round-trip만

[Answer]: **A** — NFR-T1/T2 차단 규칙 충족 대상을 도메인 순수 계층에 명확 격리. 상세는 domain-entities/business-logic-model에 속성 명세로 기록(구현은 Code Generation).

---

## 3. 산출물 생성 계획 (Artifacts)

- [x] `construction/engine-core/functional-design/domain-entities.md` — 엔티티 필드·타입·불변식·직렬화 계약·PBT 속성
- [x] `construction/engine-core/functional-design/business-logic-model.md` — 서비스/도메인 로직 알고리즘·데이터 흐름·시퀀스
- [x] `construction/engine-core/functional-design/business-rules.md` — 검증·예외·충돌(엔진 우선)·스킵·결정성 규칙
- [x] 프런트엔드 컴포넌트 문서 — **N/A** (U1은 UI 없음)
- [x] 콘텐츠 검증(Mermaid + 텍스트 대안, 특수문자/테이블 파싱)

---

## 4. 진행 절차 (Process Checklist)

- [x] Step 1: Unit 컨텍스트 분석 (unit-of-work / story-map / component-methods)
- [x] Step 2: 계획 작성(본 문서)
- [x] Step 3-4: 질문 임베드 + 저장(권장안 자동 채택)
- [x] Step 5: 답변 분석 — 전 항목 단일 권장안, 모호성 없음
- [x] Step 6: 산출물 3종 생성
- [x] Step 7-9: 완료 메시지 → 승인(자동) → aidlc-state 갱신

---

## 5. 확장 컴플라이언스 (본 단계)

| Extension | 상태 | 판정 |
|---|---|---|
| Security Baseline | Disabled | N/A |
| Resiliency Baseline | Disabled | N/A |
| Property-Based Testing (Partial) | Enabled | **적용** — PBT-02/03 대상 순수 함수/직렬화를 domain-entities·business-logic-model에 속성으로 명세(Q8). PBT-07/08/09(프레임워크·생성기·재현성)는 NFR/Code Generation에서 강제. 본 단계 차단 위반 없음. |
