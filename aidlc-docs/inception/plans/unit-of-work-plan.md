# Unit of Work Plan

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Units Generation (Part 1: Planning)
> **작성일**: 2026-09-08
> **입력 산출물**: `application-design/*`, `requirements.md`, `stories.md`, `personas.md`, `execution-plan.md`
> **정의**: 작업 단위(Unit of Work) = 개발 목적의 스토리 논리 그룹. 본 프로젝트는 **단일 배포(모놀리식 단일 패키지, Q1=A)** 이므로 각 Unit은 **독립 배포 서비스가 아닌 논리 모듈**이다.

---

## 0. 배경 (Context)

- 아키텍처: 단일 Python 패키지 `agentic_kb/`, 포트 & 어댑터(헥사고날).
- 3개 서브시스템: Knowledge Engine(코어), MCP Server(에이전트 인터페이스), Web Viewer(사람 인터페이스) + 공통 CLI/조립 루트.
- 배포 모델: 로컬 단일 사용자, stdio·파일 기반. 독립 배포 단위 없음 → **모듈 단위 분해**.

---

## 1. 권장 분해안 (Recommended Decomposition — 질문으로 확정)

> 아래는 애플리케이션 설계 경계에 정렬한 **권장 4-Unit 분해안**이다. 2절 질문 답변으로 확정한다.

| Unit | 이름 | 범위(모듈) | 주 스토리 | 의존 |
|---|---|---|---|---|
| **U1** | **Engine Core** | `domain/*`, `ports/*`, `adapters/outbound/*`(Source/Parsers/Store), `application/*`(Sync/Read/Query/Snippet/Update 서비스) | US-E1~E5, US-A2/A3/A4(서비스 로직), US-N2~N7 | 없음 |
| **U2** | **MCP Server** | `adapters/inbound/mcp/*`(Resources/Tools/Prompts/stdio) | US-A1, US-A5, US-A6, US-N1 | U1 |
| **U3** | **Web Viewer** | `adapters/inbound/web/*`(SSR 트리/위키/그래프/검토) | US-H1~H4 | U1 |
| **U4** | **CLI & Assembly** | `adapters/inbound/cli/*`, `config.py`, `__main__.py`(DI 조립·진입점) | US-A6(serve), US-E1/E5(ingest/sync), US-N7 | U1, U2, U3 |

> 근거: 검색/스니펫/업데이트/읽기의 **로직은 코어(U1)** 에 두고, MCP/Web은 **얇은 인바운드 어댑터**로 이를 노출(설계 문서와 일치). 이렇게 하면 U1이 인터페이스와 독립적으로 완성·테스트(PBT 포함) 가능.

---

## 2. 결정 대기 질문 (Decomposition Questions)

**작성 지침**: 각 `[Answer]:` 태그 뒤에 옵션 문자(A/B/C…)를 적어주세요. 해당 없으면 마지막(Other)을 선택하고 서술해주세요. 모두 작성 후 "완료"라고 알려주시면 분석 후 Unit 산출물을 생성합니다.

### Question 1 — 그룹핑 전략 (Story Grouping)
스토리를 Unit으로 묶는 기준은?

A) **서브시스템별** — Engine Core / MCP Server / Web Viewer / CLI·Assembly (권장, 설계 경계와 일치)

B) 아키텍처 계층별 — domain / application / adapters를 각각 Unit으로

C) 스토리 Epic별 — Epic A / H / E / N을 각각 Unit으로

D) Other (please describe after [Answer]: tag below)

[Answer]: **서브시스템별** — Engine Core / MCP Server / Web Viewer / CLI·Assembly (권장, 설계 경계와 일치)

### Question 2 — 공유 읽기/검색 서비스 배치 (Dependencies)
Read/Query/Snippet/Update 서비스(로직)를 어느 Unit에 둘까요?

A) **Engine Core(U1)** 에 포함 — MCP·Web은 얇은 어댑터로 노출 (권장, 재사용·테스트 용이)

B) MCP Server(U2)에 포함 — 에이전트 전용으로 간주 (Web은 Read만 별도 공유)

C) 별도 "Application Services" Unit으로 분리

D) Other (please describe after [Answer]: tag below)

[Answer]: **Engine Core(U1)** 에 포함 — MCP·Web은 얇은 어댑터로 노출 (권장, 재사용·테스트 용이)

### Question 3 — CLI & 조립 루트 배치 (Story Grouping)
CLI 진입점과 DI 조립(config/__main__)을 어떻게 둘까요?

A) **독립 Unit U4** (CLI & Assembly) — 모든 Unit을 조립하는 최종 통합 지점 (권장)

B) Engine Core(U1)에 흡수 — 별도 Unit 없이 코어에 진입점 포함

C) Other (please describe after [Answer]: tag below)

[Answer]: **독립 Unit U4** (CLI & Assembly) — 모든 Unit을 조립하는 최종 통합 지점 (권장)

### Question 4 — Unit 개수/세분화 (Business Domain / Granularity)
전체 Unit 개수 세분화 수준은?

A) **4개 Unit** — Engine Core / MCP Server / Web Viewer / CLI·Assembly (권장)

B) 3개 Unit — CLI·Assembly를 Engine Core에 흡수

C) 2개 Unit — Engine+CLI(백엔드) / 인터페이스(MCP+Web)

D) Other (please describe after [Answer]: tag below)

[Answer]: **4개 Unit** — Engine Core / MCP Server / Web Viewer / CLI·Assembly (권장)

### Question 5 — Unit 개발 순서 (Dependencies / Sequencing)
Unit 구현 순서(per-unit 설계·코드 루프 진행 순서)는?

A) **U1 Engine Core → U2 MCP Server → U3 Web Viewer → U4 CLI & Assembly** (권장, 의존 순)

B) U1 → U4(CLI로 ingest/sync 조기 검증) → U2 → U3

C) 순서 무관 / 이후 조정

D) Other (please describe after [Answer]: tag below)

[Answer]: **U1 Engine Core → U2 MCP Server → U3 Web Viewer → U4 CLI & Assembly** (권장, 의존 순)

### Question 6 — PBT/테스트 하니스 배치 (Technical Considerations, US-N6)
Property-Based Testing(부분: PBT-02/03/07/08/09) 및 테스트 스캐폴딩을 어떻게 배치할까요?

A) **각 Unit 내부에 해당 Unit의 테스트 포함** + 공용 PBT 설정/제너레이터는 Engine Core(U1)에 (권장)

B) 전체 테스트를 별도 교차관심사 Unit으로 분리

C) Other (please describe after [Answer]: tag below)

[Answer]: **각 Unit 내부에 해당 Unit의 테스트 포함** + 공용 PBT 설정/제너레이터는 Engine Core(U1)에 (권장)

### Question 7 — 디렉토리/코드 구조 (Code Organization, Greenfield)
소스와 테스트 디렉토리 레이아웃 선호는?

A) **`src/agentic_kb/` + `tests/`** (src-layout, 패키징 친화) (권장)

B) `agentic_kb/` + `tests/` (flat-layout, 단순)

C) Other (please describe after [Answer]: tag below)

[Answer]: **`src/agentic_kb/` + `tests/`** (src-layout, 패키징 친화) (권장)

---

## 3. 필수 Unit 산출물 생성 계획 (Mandatory Artifacts — 답변 확정 후 실행)

- [x] `application-design/unit-of-work.md` — Unit 정의·책임 + **코드 조직 전략(greenfield, src-layout)**
- [x] `application-design/unit-of-work-dependency.md` — Unit 의존성 매트릭스 + 다이어그램(Mermaid + 텍스트 대안)
- [x] `application-design/unit-of-work-story-map.md` — 스토리 ↔ Unit 매핑 (22/22 배정 확인)
- [x] Unit 경계·의존 검증 (DAG, 순환 없음)
- [x] 모든 스토리가 Unit에 배정되었는지 확인 (US-A/H/E/N 22개 전수 배정 + Backlog US-F1~F5 범위 밖 표기)
- [x] 콘텐츠 검증(content-validation.md) — Mermaid 2종 + 텍스트 대안, 특수문자/테이블 파싱 확인

---

## 4. 진행 절차 (Process Checklist)

### Part 1 — Planning
- [x] Step 1–2: 플랜 + 필수 산출물 목록 작성
- [x] Step 3–4: 질문 임베드 및 플랜 저장 (`unit-of-work-plan.md`)
- [x] Step 5–6: 사용자 답변 수집 (Q1~Q7 모두 응답 = A)
- [x] Step 7–8: 답변 모호성 분석 (모호/모순 없음, 후속 질문 불필요)
- [x] Step 9–11: 계획 승인 요청/대기/기록 → Part 1 완료 (사용자 "이어서 진행" = 승인, 2026-09-08)

### Part 2 — Generation
- [x] Step 12–15: 승인된 계획으로 Unit 산출물 3종 생성, 체크박스 갱신
- [ ] Step 16–19: 완료 메시지 → 승인 → `aidlc-state.md` Units Generation 완료 표시 → CONSTRUCTION 전환 — **현재 대기 지점**

---

## 5. 스토리 배정 커버리지 점검표 (생성 시 확정)

| Epic | 스토리 | 예상 Unit(권장안 기준) |
|---|---|---|
| A | US-A1, A5, A6 | U2 (MCP) / A2·A3·A4 로직 U1 |
| H | US-H1~H4 | U3 (Web) |
| E | US-E1~E5 | U1 (Engine) |
| N | US-N1 | U2 표면 / U1 계측 |
| N | US-N2~N7 | U1 (Engine) |
| CLI 진입 | US-A6(serve), E1/E5(ingest/sync) | U4 |
| Backlog | US-F1~F5 | 범위 밖(MVP 제외) |
