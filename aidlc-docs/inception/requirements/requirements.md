# 요구사항 정의서 (Requirements Document)

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **작성 단계**: INCEPTION – Requirements Analysis
> **작성일**: 2026-09-08
> **원본 소스**: `requirements/llm-wiki-requirements.md`, `requirements/constraints.md`, `aidlc-docs/inception/requirements/requirement-verification-questions.md`

---

## 1. 의도 분석 요약 (Intent Analysis)

| 항목 | 평가 |
|---|---|
| **사용자 요청** | LLM 에이전트가 프로젝트 맥락을 완벽히 이해하도록 코드/문서를 구조화된 지식으로 변환해 제공하는 MCP 기반 Agentic Knowledge Base 구축. 에이전트에게는 최적화된 컨텍스트를, 사람에게는 시각화 위키를 제공하는 Dual-Interface 모델. |
| **요청 유형 (Request Type)** | New Project (그린필드) |
| **범위 (Scope)** | System-wide — MCP 서버, Knowledge Engine, Web Viewer 3개 주요 서브시스템 |
| **복잡도 (Complexity)** | Complex — 다중 서브시스템, 에이전트-엔진 상호작용, 코드 그래프 분석, 이중 인터페이스 |
| **요구사항 깊이 (Depth)** | Comprehensive |

---

## 2. 확정된 기술 및 정책 결정 (Confirmed Decisions)

요구사항 확인 질문(Q1~Q13)에 대한 사용자 답변으로 확정된 사항입니다.

| # | 결정 항목 | 확정 내용 |
|---|---|---|
| Q1 | 주 구현 언어/런타임 | **Python** (MCP Python SDK + LLM/파싱 생태계 활용) |
| Q2 | MCP 전송 방식 (Transport) | **stdio** (로컬 단일 사용자, Claude Desktop/Claude Code 등에서 직접 실행) |
| Q3 | 지식 저장 방식 (Persistence) | **파일 기반** (Markdown + JSON, Git 친화적) |
| Q4 | LLM 호출 주체 | **엔진은 LLM 미호출** — 엔진은 결정적 구조 추출만 수행하고, 요약/추론은 소비 에이전트가 MCP 출력과 상호작용하며 담당(Update Tool로 저장). 따라서 LLM 제공자 추상화 불필요. *(변경: 2026-09-08 — 아래 변경 이력 참조)* |
| Q5 | 시맨틱 검색 수준 (MVP) | **키워드 + 코드 구조(그래프) 기반 검색**부터 시작, 임베딩은 이후 단계 |
| Q6 | 코드 관계 그래프 언어 범위 | **다국어 확장형** (tree-sitter 등 파서 기반, 언어 추가 가능한 구조) |
| Q7 | MVP 인제스천 포맷 | **소스 코드 + Markdown만** (PDF/HTML/PPT는 이후 단계) |
| Q8 | Web Viewer 스택 | **경량 서버사이드 렌더링** (Markdown 정적 렌더 위주, 최소 의존성) |
| Q9 | 사용 환경 / 사용자 모델 | **단일 개발자의 로컬 환경** |
| Q10 | 편집/동기화 충돌 정책 | **엔진 우선** — 소스 코드 기준 자동 재생성 (수동 수정은 재동기화 시 사라질 수 있음) |
| Q11 | Security Baseline 확장 | **미적용 (Opt-out)** |
| Q12 | Resiliency Baseline 확장 | **미적용 (Opt-out)** |
| Q13 | Property-Based Testing 확장 | **부분 적용 (Partial)** — 순수 함수 및 직렬화 왕복(round-trip)에 한정 |

---

## 3. 기능 요구사항 (Functional Requirements)

### 3.1 Agent Interface (MCP Server)

- **FR-A1 — MCP Resources 노출**: 프로젝트 구조, 파일/모듈 요약본, 관계 그래프 데이터를 URI 형태의 MCP Resource로 제공한다.
  - FR-A1.1 Structure Resource: 프로젝트 전체의 논리적 계층 구조 제공
  - FR-A1.2 Summary Resource: 주요 파일 및 모듈의 핵심 요약 정보 제공
  - FR-A1.3 Relationship Resource: 모듈 간 의존성 및 호출 관계 데이터 제공
- **FR-A2 — Semantic Query Tool**: 키워드 및 코드 구조(그래프) 기반의 정보 검색을 제공한다. (MVP: 키워드 + 그래프 기반. 임베딩 기반 의미 검색은 후속 단계.)
- **FR-A3 — Smart Snippet Tool**: 요청 컨텍스트의 토큰 양을 고려하여 최적의 코드 범위(Scope)를 잘라 토큰 최적화된 스니펫을 제공한다.
- **FR-A4 — Update Tool**: 에이전트의 작업 결과를 지식 베이스(위키)에 반영한다.
- **FR-A5 — MCP Prompts (Prompt Templates)**: 특정 작업에 최적화된 프롬프트 템플릿을 제공한다.
  - FR-A5.1 Onboarding Prompt: 신규 에이전트가 프로젝트 전체 맥락을 빠르게 학습하도록 지원
  - FR-A5.2 Task-Specific Prompt: 특정 작업(예: 단위 테스트 작성) 수행에 필요한 지식만 집중 제공
- **FR-A6 — 전송 방식**: MCP 서버는 stdio 전송을 통해 로컬 클라이언트(Claude Desktop/Claude Code 등)에서 직접 실행된다.

### 3.2 Human Interface (Web Viewer)

- **FR-H1 — Interactive Tree View**: 프로젝트의 디렉토리 및 논리적 의존성 구조를 트리 형태로 시각화한다.
- **FR-H2 — Wiki Content Viewer**: Markdown 기반으로 정리된 명세 및 코드 설명을 웹에서 렌더링한다.
- **FR-H3 — Dependency Visualization**: 코드 간 관계(호출/의존성)를 그래프 형태로 시각화한다.
- **FR-H4 — Content Review**: 사람이 엔진이 생성/수정한 지식 베이스를 검토할 수 있다.
- **FR-H5 — 구현 형태**: Web Viewer는 경량 서버사이드 렌더링 방식(Markdown 정적 렌더 위주, 최소 의존성)으로 구현한다.

### 3.3 Knowledge Engine (Core)

- **FR-E1 — Multi-format Ingestion (MVP 범위)**: 소스 코드 및 Markdown 파일을 수집·분석·구조화한다. (PDF/HTML/PPT는 MVP 제외, 후속 단계.)
- **FR-E2 — Graph Construction**: 파서(tree-sitter 등) 기반으로 파일/함수/클래스 간의 호출 및 의존성 관계를 모델링한다. 다국어 확장이 가능한 구조로 설계한다.
- **FR-E3 — Structured Extraction & Agent-authored Summaries**: 엔진은 **LLM을 호출하지 않고** 파서 기반의 **결정적 구조 추출**(함수/클래스 시그니처, docstring, 주석, Markdown 헤딩 등)로 파일/모듈의 구조적 요약 정보를 생성한다. **심화된 자연어 요약/노트**는 소비 에이전트(P1)가 MCP 출력과 상호작용하며 작성하여 **Update Tool(FR-A4)** 을 통해 지식 베이스에 저장한다(병행 모델: 엔진 기본 추출 + 에이전트 심화 요약). 모든 LLM 상호작용은 에이전트 측에서 발생하며 엔진은 완전 로컬/결정적으로 동작한다.
- **FR-E4 — Persistence**: 생성된 지식(요약, 구조, 관계 그래프)을 파일 기반(Markdown + JSON)으로 Git 친화적 형태로 저장한다.
- **FR-E5 — Re-sync / 재동기화**: 소스 코드 변경 시 명시적 재동기화(또는 재실행)를 통해 위키를 소스 기준으로 재생성한다.

### 3.4 편집/동기화 충돌 정책 (Conflict Policy)

- **FR-C1 — 엔진 우선(Engine-first)**: 위키는 소스 코드를 진실의 원천(source of truth)으로 삼아 자동 재생성된다. 사람이 수동으로 수정한 내용은 재동기화 시 덮어써질 수 있음을 정책으로 명시한다. (사용자 확정 — Q10)

---

## 4. 비기능 요구사항 (Non-Functional Requirements)

### 4.1 성능 (Performance)
- **NFR-P1 — Low Latency**: MCP Tool의 핵심 조회 기능 응답 시간은 **1초 이내**를 목표로 한다. 에이전트의 반복 루프를 방해하지 않아야 한다.
- **NFR-P2 — Token Efficiency**: 에이전트에게 제공되는 모든 Resource 및 Tool 결과물은 Smart Chunking 및 Summarization을 적용하여 불필요한 토큰 낭비를 최소화한다.

### 4.2 이식성 / 구성 (Portability & Configurability)
- **NFR-C1 — (제거됨)** ~~LLM Provider 추상화~~: 엔진이 LLM을 호출하지 않으므로 제공자 추상화 요구사항은 **폐지**한다. *(변경: 2026-09-08)*
- **NFR-C2 — 파서 확장성**: 코드 그래프 분석은 언어별 파서를 플러그인 형태로 추가할 수 있는 구조로 설계한다.
- **NFR-C3 — 엔진 로컬성/결정성**: 엔진은 파싱·그래프·저장 전 과정에서 외부 API(LLM 포함)를 호출하지 않으며, 동일 입력에 대해 결정적으로 동작한다. *(신규: 2026-09-08)*

### 4.3 데이터 및 환경 (Data & Environment)
- **NFR-D1 — Git 친화 저장**: 지식 산출물은 텍스트 기반(Markdown + JSON)으로 저장하여 버전 관리 및 diff에 친화적이어야 한다.
- **NFR-E1 — 실행 환경**: 파일 시스템 기반의 단일 개발자 로컬 환경에서 동작하며, Git 사용 환경을 상정한다.

### 4.4 비용 / 자원 (Cost & Resource) — 인지된 제약
- **NFR-R1**: 엔진은 외부 API(LLM)를 호출하지 않으므로 **엔진 자체의 API 비용/지연은 없다.** LLM 사용 비용/지연은 **에이전트(MCP 클라이언트) 측**에서 발생하며 엔진의 범위 밖이다. *(변경: 2026-09-08)*
- **NFR-R2**: 프로젝트 규모 증가에 따라 그래프 생성 및 파싱 컴퓨팅 자원이 증가함을 인지한다.

### 4.5 테스트 품질 (Testability — Property-Based Testing, Partial)
- **NFR-T1**: 순수 함수 및 직렬화 왕복(round-trip) 로직에 대해 속성 기반 테스트(PBT)를 적용한다.
- **NFR-T2**: Partial 모드로 PBT 규칙 **PBT-02(Round-trip), PBT-03(Invariant), PBT-07(Generator Quality), PBT-08(Shrinking/Reproducibility), PBT-09(Framework Selection)** 를 차단(blocking) 제약으로 강제한다. 그 외 PBT 규칙은 권고(advisory) 사항이다.
- **NFR-T3**: Python용 PBT 프레임워크(예: Hypothesis)를 선정하여 의존성에 포함한다. (NFR Requirements / Code Generation 단계에서 확정)

---

## 5. 제약사항 및 제외 범위 (Constraints & Out of Scope)

### 5.1 제외 기능 (Out of Scope — MVP 및 이후 별도 검토)
- 실시간 파일 시스템 감시 및 자동 동기화
- CI/CD 파이프라인 긴밀 통합 및 자동 배포 연동
- 심화 OCR (이미지 내 복잡 레이아웃/손글씨 완전 구조화)
- 고급 문서 변환 (PPT/PDF 내 복잡 차트·다이어그램 논리 구조 완전 복원)
- 초대규모(TB 단위) 코드베이스 실시간 인덱싱 및 즉각 검색 성능 보장
- Slack/Teams 등 메신저 양방향 실시간 알림 연동
- PDF / HTML / PPT 포맷 인제스천 (MVP 제외 — 후속 단계)
- 임베딩 기반 벡터 시맨틱 검색 (MVP 제외 — 후속 단계)

### 5.2 기술적 제약 (Technical Constraints)
- 위키 구조는 소스 코드의 파일 경로 및 관계 기반으로 생성되므로, 대규모 리팩토링(파일 이동 등) 시 논리 구조 불일치가 발생할 수 있으며 재동기화가 필요하다.
- 데이터 일관성은 "엔진 우선" 정책에 따라 소스 코드 기준으로 유지된다.

---

## 6. MVP 개발 범위 (MVP Scope)

MVP는 다음 핵심 기능으로 한정한다.

1. **MCP Server Core**: 기본 Resources(FR-A1) 및 Tools(FR-A2, FR-A3, FR-A4) 구현, stdio 전송.
2. **Ingestion Engine**: 소스 코드 및 Markdown 파일의 분석 및 위키화 (FR-E1), 그래프 구성(FR-E2), 결정적 구조 추출 요약(FR-E3, LLM 미호출), 파일 기반 저장(FR-E4).
3. **Basic Web Viewer**: Markdown 기반 파일 트리 및 뷰어 (FR-H1, FR-H2), 경량 SSR.

**MVP 검색 수준**: 키워드 + 코드 구조(그래프) 기반. (임베딩 기반 의미 검색 제외)

---

## 7. 확장(Extension) 구성

| Extension | 적용 여부 | 비고 |
|---|---|---|
| Security Baseline | 미적용 | PoC/프로토타입 성격 (Q11) |
| Resiliency Baseline | 미적용 | 빠른 반복 우선 (Q12) |
| Property-Based Testing | 부분 적용 | 강제 규칙: PBT-02, 03, 07, 08, 09 (Q13) |

---

## 8. 핵심 요구사항 요약 (Key Requirements Summary)

- **Dual-Interface**: 에이전트용 MCP 서버(stdio) + 사람용 경량 웹 뷰어.
- **Knowledge Engine**: Python 기반, tree-sitter 파서로 다국어 확장 가능한 코드 그래프 구성, **결정적 구조 추출 요약(엔진 LLM 미호출)**, 파일 기반(Markdown+JSON) Git 친화 저장. 심화 요약은 에이전트가 작성해 Update Tool로 저장.
- **MVP 범위**: 소스 코드 + Markdown 인제스천, 키워드+그래프 검색, 기본 MCP Resources/Tools, 기본 웹 뷰어.
- **핵심 NFR**: 조회 응답 1초 이내, 토큰 효율(Smart Chunking/Summarization), LLM 제공자 교체 가능.
- **정책**: 엔진 우선 재동기화 (소스 코드가 진실의 원천).
- **품질**: 순수 함수/직렬화 round-trip에 대한 부분 PBT 적용.

---

## 9. 미해결 / 후속 단계 결정 사항 (Deferred Decisions)

다음 항목은 후속 단계(NFR Requirements / Application Design / Code Generation)에서 구체화한다.

- 구체적 Python PBT 프레임워크 및 테스트 러너 구성 (Hypothesis 유력)
- 경량 SSR 웹 뷰어의 구체 기술 선택 (프레임워크/템플릿 엔진)
- 그래프 데이터 스키마 및 파일 저장 레이아웃 상세
- 엔진의 결정적 구조 추출 범위 상세 (추출 대상: 시그니처/docstring/주석/헤딩 등)
- MCP Resource URI 스킴 및 Tool 입출력 스키마 상세 (특히 에이전트 심화 요약 저장용 Update Tool 페이로드)

---

## 10. 변경 이력 (Change Log)

| 일자 | 변경 내용 |
|---|---|
| 2026-09-08 | **아키텍처 정정**: 엔진(MCP 서버)이 LLM을 호출하지 않고, 소비 에이전트가 MCP 출력과 상호작용하며 요약/추론을 담당하도록 변경. 영향: Q4 재정의, FR-E3 재작성(결정적 구조 추출 + 에이전트 심화 요약), NFR-C1(LLM 제공자 추상화) 폐지, NFR-C3(엔진 로컬성/결정성) 신규, NFR-R1 재정의(엔진 API 비용 없음). |
