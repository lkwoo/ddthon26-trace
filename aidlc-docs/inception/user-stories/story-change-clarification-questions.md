# User Stories 변경 명확화 질문 (Change Clarification)

> **단계**: INCEPTION – User Stories (Request Changes)
> **작성일**: 2026-09-08
> **변경 취지**: MCP 서버/엔진은 LLM을 호출하지 않는다. 엔진은 구조화된 출력(구조·그래프·원문/청크)만 제공하고, 이를 소비하는 **에이전트(LLM)** 가 상호작용하며 요약/추론을 담당한다. → LLM 제공자 추상화(NFR-C1) 불필요.

아래 각 질문의 `[Answer]:` 태그 뒤에 letter 선택지를 적어주세요. 맞는 보기가 없으면 마지막 `Other`를 고르고 설명을 덧붙여 주세요.

## Question 1
엔진이 LLM을 호출하지 않게 되면, 파일/모듈 "요약(summary)" 콘텐츠는 어떻게 생성·보관합니까?

A) **에이전트 작성·저장** — 에이전트가 MCP 출력을 보고 요약을 만든 뒤 Update Tool로 지식 베이스에 기록 (agent-authored, 파일로 저장)

B) **엔진 구조 추출(LLM 없음)** — 엔진이 결정적 방식으로 시그니처·docstring·주석·헤딩 등을 추출해 요약 대체 (LLM 미사용)

C) **비저장** — 엔진은 구조+그래프+원문/청크만 제공하고, 요약은 에이전트가 필요 시 즉석에서 수행 (별도 저장 안 함)

D) **병행(B+A)** — 엔진의 결정적 구조 추출을 기본 제공하고, 에이전트가 심화 요약/노트를 Update Tool로 추가 저장

E) Other (please describe after [Answer]: tag below)

[Answer]: **병행(B+A)** — 엔진의 결정적 구조 추출을 기본 제공하고, 에이전트가 심화 요약/노트를 Update Tool로 추가 저장

## Question 2
요구사항 정의서(`requirements.md`)의 관련 항목도 이 변경에 맞게 함께 수정할까요?
(대상: FR-E3 요약 엔진, NFR-C1 LLM 제공자 추상화, NFR-R1 LLM 비용, Q4 제공자 추상화 결정)

A) 예 — `requirements.md`를 이 변경에 맞게 수정한 뒤 스토리를 갱신 (권장, 문서 정합성 유지)

B) 아니오 — 이번에는 스토리(`stories.md`/`personas.md`)만 수정하고 요구사항 문서는 현행 유지

C) Other (please describe after [Answer]: tag below)

[Answer]: 예 — `requirements.md`를 이 변경에 맞게 수정한 뒤 스토리를 갱신 (권장, 문서 정합성 유지)

## Question 3
"엔진은 외부 API를 전혀 호출하지 않는 완전 로컬/결정적 엔진"으로 확정할까요?
(즉, 요약뿐 아니라 어떤 단계에서도 엔진이 직접 LLM/외부 API를 부르지 않음)

A) 예 — 엔진은 파싱·그래프·저장까지 전부 로컬/결정적이며 외부 API 호출 없음. 모든 LLM 상호작용은 에이전트 쪽에서만 발생

B) 아니오 — 요약 외에 특정 기능에서는 엔진이 외부 API를 부를 수 있음 (해당 기능을 Other에 기술)

C) Other (please describe after [Answer]: tag below)

[Answer]: 예 — 엔진은 파싱·그래프·저장까지 전부 로컬/결정적이며 외부 API 호출 없음. 모든 LLM 상호작용은 에이전트 쪽에서만 발생
