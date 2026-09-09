# 사용자 스토리 생성 계획 — Increment 2 "프로젝트 온보딩 맵"

**단계**: INCEPTION / User Stories (증분)
**작성일**: 2026-09-09
**입력**: `requirements.md` §4.10 FR-MAP-001~007, §9 UOW-07
**산출물**: 기존 `personas.md`·`stories.md`에 **증분 추가**(덮어쓰기 아님)

---

## Part 1 — 방법론(정착 컨벤션 재사용)

Increment 1에서 승인·정착된 스토리 규약을 **그대로 재사용**한다(아래 Q3에서 확인만 받음):
- **조직**: Epic(=UOW) 기반 + Epic 내부 User-Journey
- **수용 기준**: Given/When/Then
- **추적성**: 각 스토리에 `Implements:`(FR/NFR) + `UOW:` 매핑
- **INVEST** 준수, 액터 표기(As/I want/so that)

새로 정할 것(아래 질문)은 **페르소나**와 **여정 세분도**뿐이다.

## User Stories 필요성 판정 (Step 1)
- **판정: 실행(High Priority)** — 신규 사용자 대면 기능(온보딩 맵), 새 사용자 워크플로우(낯선 프로젝트 파악), 다중 산출물(도구+CLI+overview.md). 스토리가 수용 기준·팀 이해를 명확히 함.

---

## Part 1 — 확인 질문

**응답 방법**: 각 `[Answer]:` 뒤에 A/B/C/X 중 하나. 추천안을 A로 둠.

### Q1. 페르소나 — 신규 페르소나가 필요한가?
온보딩 맵의 주 사용자를 어떻게 표현할까요?

A) **신규 페르소나 "P4 뉴비(신입 온보딩)" 추가 (추천)** — 기존 P1 데브는 *기술수준 높음·티켓 단위 영향 분석*이 목표인 반면, 신입은 *프로젝트 전체 그림·시작점·용어·파일/함수 관계 파악*이 목표라 관심사·기술수준·성공기준이 뚜렷이 다르다. P1과 함께 UOW-07에 매핑.

B) 기존 P1 데브만 재사용 — P1이 이미 "낯선 코드베이스에 갓 투입된 개발자"라 충분. 페르소나 추가 없이 스토리만 추가.

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Q2. 여정 세분도 — UOW-07 스토리를 몇 개로 쪼갤까?
온보딩 맵 기능(FR-MAP-001~007)을 어떤 사용자 여정으로 나눌까요?

A) **사용자 여정 기반 5개 스토리 (추천)** — (1) 맵 생성·조회(MCP 도구 + CLI, 영속화 FR-MAP-001/006), (2) 진입점 + 파일/모듈 의존 그래프 Mermaid(FR-MAP-003a~b/004/005), (3) Feature→파일 매핑(FR-MAP-003c), (4) 핵심 경로 함수 호출 관계(FR-MAP-002/003d), (5) "여기서 시작하세요" 온보딩 내러티브 + 근거 인용(FR-MAP-003e/007). FR-MAP 전부 커버.

B) 더 굵게 3개 스토리 — 생성·조회 / 시각화(그래프+시퀀스) / 내러티브·근거.

C) 더 잘게 7개 스토리 — FR-MAP-001~007 각 1:1.

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Q3. 포맷 재사용 확인
Increment 1의 스토리 컨벤션(Epic=UOW, Given/When/Then AC, `Implements:`/`UOW:` 추적성)을 그대로 쓸까요?

A) **그대로 재사용 (추천)** — 기존 stories.md와 일관.

X) 변경 (please describe after [Answer]: tag below)

[Answer]: A

> **확정(2026-09-09)**: Q1=A 신규 페르소나 P4 뉴비 추가, Q2=A 5개 스토리, Q3=A 포맷 재사용. Part 2 실행.

---

## Part 2 — 생성 체크리스트 (승인 후 실행)
- [x] `personas.md`에 Q1 결정 반영(신규 페르소나 P4 뉴비 추가 + Epic 매핑 갱신)
- [x] `stories.md`에 `## EPIC UOW-07 — 프로젝트 온보딩 맵` 섹션 + 5개 스토리 추가(Given/When/Then, Implements/UOW)
- [x] `stories.md` 추적성 요약 표에 UOW-07 행 추가, 총계 갱신
- [x] `aidlc-state.md` User Stories 완료 표기, audit.md 기록
