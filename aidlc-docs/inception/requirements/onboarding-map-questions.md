# 요구사항 확인 질문 — 신규 기능 "프로젝트 온보딩 맵"

**작성일**: 2026-09-09
**단계**: INCEPTION / Requirements Analysis (증분)
**대상**: TRACE를 쓰는 신입 개발자가 낯선 프로젝트에 투입됐을 때, **전체 흐름 · 파일 간 관계 · 함수 간 관계**를 온보딩 관점에서 파악하도록 돕는 새 기능.
**연결**: 기존 `requirements.md` §4 위에 `FR-MAP-*` 신설. 확정 후 User Stories에서 온보딩 페르소나+시나리오로 이어짐.

**응답 방법**: 각 질문의 `[Answer]:` 태그 뒤에 A/B/C/X 중 하나(또는 X + 설명)를 적어주세요. 추천안을 A로 두었습니다.

---

## Q1. 파일/함수 "관계" 추출 방식 (핵심)
"파일 간 관계", "함수 간 관계"를 어떻게 뽑아낼까요? 이것이 정확도·재현성·구현 범위를 좌우합니다.

A) **하이브리드 (추천)** — 기존 스캐너/파서가 이미 뽑은 자산 위에서 import/호출 등 관계 단서를 **가볍게 정적으로 추출**하고, **LLM이 근거와 함께 관계·흐름을 서술**. TRACE의 근거기반(Claim↔Evidence) 철학·기존 인프라를 그대로 재사용. 결정적 뼈대 + 설명.

B) **전면 정적 분석** — 언어별 AST로 정밀 호출 그래프를 만든다. 정확하지만 언어별 파서 구현 비용이 커 2일 PoC에는 과함.

C) **전면 LLM** — 정적 단서 없이 LLM이 코드에서 관계를 추론. 구현은 빠르나 재현성·정밀도가 낮고 근거 추적이 약함.

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q2. 산출물 소비 형태
온보딩 맵을 어떤 방식으로 제공할까요? (기존 5개 MCP tool + CLI 패턴과의 정합)

A) **둘 다 (추천)** — 새 MCP tool + CLI 명령(예: `get_project_map` / `trace map`)으로 **조회**하고, 동시에 `.trace/knowledge/overview.md`로 **영속화**. 기존 analyze/conflicts/task 패턴과 동일.

B) 영속 산출물만 — `overview.md`(+다이어그램) 파일만 생성, 별도 tool/CLI 없음.

C) tool/CLI만 — 조회 결과만 반환, 파일 영속화 없음.

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q3. 맵 구성 범위 (무엇을 "전체 흐름"으로 담을까)
온보딩 맵에 포함할 요소의 깊이를 정합니다.

A) **파일 레벨** — 진입점 + 파일/모듈 의존 그래프 + Feature→파일 매핑 + "여기서 시작하세요" 온보딩 내러티브.

B) **A + 함수 레벨 (추천)** — 위에 더해 핵심 경로의 **함수 간 호출 관계**(요청 핸들러→서비스→저장 등)까지. 요청하신 "함수들의 관계" 충족.

C) **B + 데이터 흐름 시퀀스** — 핵심 시나리오 1개의 요청→핸들러→검증→저장 시퀀스 다이어그램까지 상세.

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Q4. 관계 시각화 (다이어그램)
관계를 어떻게 보여줄까요?

A) **Mermaid 다이어그램 포함 (추천)** — 파일/모듈 의존 그래프 + 핵심 흐름 시퀀스를 Mermaid로. Markdown 뷰어·GitHub에서 바로 렌더.

B) 텍스트 트리/목록만 — 다이어그램 없이 계층 목록·표로만.

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Q5. 정적 추출 대상 언어 범위 (Q1=A/B일 때)
관계 단서를 정적으로 뽑을 대상 언어를 어디까지 볼까요? (데모=Java Petclinic, TRACE 자체=Python)

A) **데모 중심 + LLM 폴백 (추천)** — Java/Python의 import·호출 단서를 가볍게 정적 추출하고, 그 외 언어는 LLM 서술로 폴백. 데모 Hero를 확실히 커버하면서 범용성 유지.

B) 언어 무관 LLM 폴백만 — 정적 파서 없이 모든 언어를 LLM 서술로. 구현 최소, 정밀도 낮음.

C) 특정 언어만 확정(예: Java만) — 데모에만 집중, 그 외 언어 미지원.

X) Other (please describe after [Answer]: tag below)

[Answer]: A
