# Application Design Plan

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Application Design (Part 1: Plan)
> **작성일**: 2026-09-08
> **입력 산출물**: `requirements.md`, `stories.md`, `personas.md`, `execution-plan.md`
> **목적**: 고수준 컴포넌트 식별 + 서비스 계층 설계 (상세 비즈니스 로직은 이후 Functional Design/per-unit에서 정의)

---

## 0. 범위 및 원칙 (Scope & Principles)

- 본 단계는 **무엇을(컴포넌트/책임/인터페이스/의존성)** 정의하며, **어떻게(상세 로직/스키마)** 는 다루지 않는다.
- 대상 3개 서브시스템: **MCP Server**(에이전트 인터페이스, P1), **Web Viewer**(사람 인터페이스, P2), **Knowledge Engine**(코어).
- 아키텍처 원칙(요구사항 확정): 엔진은 **LLM 미호출·로컬·결정적**(NFR-C3), **파일 기반 저장**(Markdown+JSON, NFR-D1), **stdio MCP**(FR-A6), **파서 플러그인 확장성**(NFR-C2), **엔진 우선 재동기화**(FR-C1).

---

## 1. 컨텍스트 분석 (Step 1 — 완료)

- [x] `requirements.md` 로드 및 핵심 역량 식별 (FR-A/H/E, NFR-P/C/D/E/R/T)
- [x] `stories.md` 로드 및 Epic/스토리 매핑 확인 (Epic A/H/E/N)
- [x] `personas.md` 로드 (P1 LLM 에이전트, P2 개발자/운영자)
- [x] 설계 범위/복잡도 판정: **Comprehensive** (다중 서브시스템, 교차 관심사)

---

## 2. 컴포넌트 식별 후보 (Draft — 답변에 따라 확정)

> 아래는 초안이며, 3~9절 질문에 대한 답변으로 경계/구성이 확정된다.

| 후보 컴포넌트 | 소속 서브시스템 | 핵심 책임 (요약) | 관련 스토리 |
|---|---|---|---|
| **Ingestion** | Engine | 소스/Markdown 파일 수집·필터링·등록 | US-E1 |
| **Parser Registry / Language Parsers** | Engine | tree-sitter 기반 파싱, 언어별 플러그인 | US-E2, US-N4 |
| **Graph Builder** | Engine | 심볼(파일/함수/클래스) 노드·호출/의존 엣지 구성 | US-E2 |
| **Structured Extractor** | Engine | 결정적 구조 추출(시그니처/docstring/주석/헤딩) | US-E3 |
| **Knowledge Store (Persistence)** | Engine | Markdown+JSON 파일 저장/로드, 결정적 직렬화 | US-E4, US-N5 |
| **Sync/Re-sync Orchestrator** | Engine | 인제스천→그래프→추출→저장 파이프라인, 엔진 우선 재생성 | US-E5 |
| **Query/Search** | Engine | 키워드 + 그래프 기반 검색 | US-A2 |
| **Snippet/Chunking** | Engine | 토큰 예산 기반 스니펫 선택·청킹 | US-A3, US-N2 |
| **MCP Resources Provider** | MCP Server | 구조/요약/관계 Resource(URI) 노출 | US-A1 |
| **MCP Tools Provider** | MCP Server | Query/Snippet/Update Tool | US-A2/A3/A4 |
| **MCP Prompts Provider** | MCP Server | 온보딩/작업별 프롬프트 템플릿 | US-A5 |
| **MCP Transport (stdio)** | MCP Server | stdio 핸드셰이크·기동 | US-A6 |
| **Web Renderer (SSR)** | Web Viewer | Markdown→HTML, 트리/위키/의존성 그래프 뷰 | US-H1/H2/H3/H4 |
| **CLI / Entry Points** | 공통 | 인제스천·재동기화·서버 기동 진입점 | US-A6, US-E1/E5 |

---

## 3. 결정 대기 질문 (Design Questions)

**작성 지침**: 각 질문의 `[Answer]:` 태그 뒤에 선택한 옵션 문자(A/B/C…)를 적어주세요. 해당하는 항목이 없으면 마지막 옵션(Other)을 선택하고 `[Answer]:` 뒤에 원하는 바를 서술해주세요. 모두 작성하신 뒤 "완료" 또는 "done"이라고 알려주시면 답변을 분석하고 설계 산출물을 생성합니다.

### Question 1 — 코드 구성 / 패키지 구조 (Component Identification)
코드베이스를 어떻게 구성할까요?

A) 단일 Python 패키지 + 내부 모듈 (예: `core/`, `engine/`, `mcp_server/`, `web_viewer/`, `cli/`)

B) 모노레포 내 다수의 개별 설치형 패키지 (서브패키지로 분리)

C) 책임별 계층 구조 (domain / application / interface / infrastructure)

D) Other (please describe after [Answer]: tag below)

[Answer]: 단일 Python 패키지 + 내부 모듈

### Question 2 — 코어 지식 접근 방식 (Component Dependencies)
MCP Server와 Web Viewer는 모두 저장된 지식(Markdown+JSON)을 읽습니다. 접근 방식은?

A) 공유 읽기 라이브러리/리포지토리 계층(`KnowledgeStore`)을 두고 두 인터페이스가 이를 통해 접근 (권장 — 결합도↓, 재사용↑)

B) 각 인터페이스가 저장 파일을 직접 읽음

C) Other (please describe after [Answer]: tag below)

[Answer]: 공유 읽기 라이브러리/리포지토리 계층(`KnowledgeStore`)을 두고 두 인터페이스가 이를 통해 접근 (권장 — 결합도↓, 재사용↑)

### Question 3 — 파서 플러그인 아키텍처 (Design Patterns, NFR-C2)
언어별 파서를 어떻게 플러그인으로 추가 가능하게 할까요?

A) 인메모리 레지스트리 인터페이스 — 공통 `LanguageParser` 인터페이스 구현체를 레지스트리에 등록(코어 수정 없이 모듈 추가로 확장)

B) 설정 파일 기반 매핑 (확장자 → 파서 모듈 경로)

C) Python entry-points 기반 자동 탐색 (설치형 플러그인 배포까지 고려)

D) Other (please describe after [Answer]: tag below)

[Answer]: 인메모리 레지스트리 인터페이스 — 공통 `LanguageParser` 인터페이스 구현체를 레지스트리에 등록(코어 수정 없이 모듈 추가로 확장)

### Question 4 — 서비스 계층 오케스트레이션 (Service Layer Design)
인제스천 → 파싱/그래프 → 구조추출 → 저장 흐름을 어떻게 조율할까요?

A) 단일 오케스트레이션/파이프라인 서비스(`SyncService`)가 단계를 순차 조율

B) 각 서비스를 CLI/진입점에서 직접 개별 호출 (오케스트레이터 없음)

C) Other (please describe after [Answer]: tag below)

[Answer]: 단일 오케스트레이션/파이프라인 서비스(`SyncService`)가 단계를 순차 조율

### Question 5 — MCP Server와 엔진의 결합 (Component Dependencies)
MCP 서버가 인제스천/재동기화를 트리거할 수 있어야 할까요, 아니면 이미 생성된 지식만 조회할까요?

A) MCP 서버는 **읽기 전용** — 인제스천/재동기화는 별도 CLI로 P2(개발자)가 실행 (관심사 분리, 결정성↑)

B) MCP 서버가 Tool로 인제스천/재동기화도 트리거 가능

C) 기본은 읽기 전용 + 선택적 관리(admin) Tool 제공

D) Other (please describe after [Answer]: tag below)

[Answer]: MCP 서버가 Tool로 인제스천/재동기화도 트리거 가능

### Question 6 — 에이전트 심화 요약 저장 경계 (Component Methods, FR-C1 / US-A4)
Update Tool로 저장되는 에이전트 작성 심화 요약을, 엔진이 자동 생성하는 구조 요약과 어떻게 분리 저장할까요? (엔진 우선 재동기화 정책과의 충돌 관리)

A) **별도 네임스페이스/파일**로 저장하고 조회 시 병합 — 엔진 생성분은 재동기화 시 재생성, 에이전트 노트는 소스가 존재하는 한 보존 (병행 모델에 부합)

B) 동일 파일에 저장하고 재동기화 시 엔진 기준으로 덮어씀 (엄격한 엔진 우선, 에이전트 노트 소실 가능 — Q10 문자 그대로)

C) 별도 파일이되 엔진 우선 정책 적용 대상으로 명시(재생성될 수 있음을 문서화)

D) Other (please describe after [Answer]: tag below)

[Answer]: **별도 네임스페이스/파일**로 저장하고 조회 시 병합 — 엔진 생성분은 재동기화 시 재생성, 에이전트 노트는 소스가 존재하는 한 보존 (병행 모델에 부합)

### Question 7 — 전체 아키텍처 스타일 (Design Patterns)
전반적인 아키텍처 스타일 선호는?

A) 포트 & 어댑터(헥사고날) — 코어 도메인 + 어댑터(MCP / Web / CLI / 파서 / 저장) (테스트·확장 용이, PBT 순수함수 분리에 유리)

B) 단순 계층형 (core + interfaces), 포트/어댑터 형식화 없이 경량

C) 파이프라인 중심 (데이터 흐름 파이프라인을 중심 골격으로)

D) Other (please describe after [Answer]: tag below)

[Answer]: 포트 & 어댑터(헥사고날) — 코어 도메인 + 어댑터(MCP / Web / CLI / 파서 / 저장) (테스트·확장 용이, PBT 순수함수 분리에 유리)

### Question 8 — 실행 진입점 구성 (Component Identification)
컴포넌트 기동/실행 진입점을 어떻게 구성할까요?

A) 단일 CLI + 서브커맨드 (`ingest`, `sync`, `serve-mcp`, `serve-web`) (권장 — 단일 진입점, 발견성↑)

B) 각각 별도 콘솔 스크립트 진입점 (인제스천 CLI / MCP 서버 / 웹 뷰어 분리)

C) Other (please describe after [Answer]: tag below)

[Answer]: 단일 CLI + 서브커맨드 (`ingest`, `sync`, `serve-mcp`, `serve-web`) (권장 — 단일 진입점, 발견성↑)

---

## 4. 설계 산출물 생성 계획 (Mandatory Artifacts — 답변 확정 후 실행)

> 아래 산출물은 3절 질문 답변 확정 및 승인 후 생성한다 (application-design.md Step 10).

- [x] `application-design/components.md` — 컴포넌트 정의, 고수준 책임, 인터페이스
- [x] `application-design/component-methods.md` — 컴포넌트별 메서드 시그니처, 입출력 타입, 고수준 목적 (상세 비즈니스 규칙은 Functional Design)
- [x] `application-design/services.md` — 서비스 정의, 책임, 오케스트레이션/상호작용
- [x] `application-design/component-dependency.md` — 의존성 매트릭스, 통신 패턴, 데이터 흐름 다이어그램 (Mermaid + 텍스트 대안)
- [x] `application-design/application-design.md` — 위 문서 통합본
- [x] 설계 완전성·일관성 검증 (요구사항/스토리 추적성 커버리지 확인 — 미커버 없음)
- [x] 콘텐츠 검증(content-validation.md): Mermaid 노드 ID 영숫자, 라벨 이스케이프, 텍스트 대안 포함

---

## 5. 진행 절차 (Process Checklist)

- [x] Step 1: 컨텍스트 분석
- [x] Step 2–3: 플랜 + 필수 산출물 목록 작성
- [x] Step 4–5: 질문 임베드 및 플랜 저장 (`application-design-plan.md`)
- [x] Step 6–7: 사용자 답변 수집 (Q1~Q8 모두 응답 완료)
- [x] Step 8–9: 답변 모호성 분석 (모호/모순 없음, 후속 질문 불필요)
- [x] Step 10: 설계 산출물 생성 (5종)
- [ ] Step 11–14: 승인 요청/대기/기록 — **현재 대기 지점**
- [ ] Step 15: `aidlc-state.md` Application Design 완료 표시

---

## 6. 추적성 커버리지 (설계가 반드시 다뤄야 할 항목)

| 영역 | 반드시 커버 |
|---|---|
| Agent Interface | FR-A1~A6 (Resources/Tools/Prompts/stdio) |
| Human Interface | FR-H1~H5 (Tree/Wiki/Graph/Review/SSR) |
| Knowledge Engine | FR-E1~E5 (Ingestion/Graph/Extract/Persist/Re-sync) |
| Conflict Policy | FR-C1 (엔진 우선) |
| NFR | NFR-P1(지연), NFR-P2(토큰), NFR-C2(파서 확장), NFR-C3(로컬/결정성), NFR-D1(Git 친화), NFR-E1(로컬 환경) |
| 교차 관심사(설계 반영) | 계측(US-N1 AC-2), 청킹(US-N2), 캐시/스킵(US-N7), PBT 대상 순수함수 분리(US-N6) |
