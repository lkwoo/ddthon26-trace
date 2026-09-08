# Requirements — Dual-Interface Knowledge Store (MCP-based Agentic Knowledge Base)

## 0. Intent Analysis Summary

- **User Request**: "Dual-Interface Knowledge Store" 서비스 구축 — LLM 에이전트에게는 토큰 최적화된 컨텍스트를, 사람에게는 시각화된 위키를 제공하는 MCP 기반 Agentic Knowledge Base.
- **Request Type**: New Project (Greenfield)
- **Scope Estimate**: System-wide (MCP Server + Knowledge Engine + Web Viewer + Installer)
- **Complexity Estimate**: Complex (다중 컴포넌트, tree-sitter 다언어 파싱, 그래프 모델링, 청크 버전 관리, 로컬 임베딩)
- **Requirements Depth**: Comprehensive
- **Primary Requirements Source**: `requirements/llm-wiki-requirements.md`, `requirements/constraints.md`
- **Reference Implementations (부록 B)**: Graphify (Apache-2.0), obsidian-wiki (MIT) — 로직 적극 참고·부분 이식(라이선스 고지 준수).

---

## 1. Confirmed Technical Decisions (from clarifying answers)

| # | 결정 항목 | 선택 | 근거/비고 |
|---|---|---|---|
| Q1 | 구현 언어/런타임 | **Python** | 참고 레퍼런스와 동일, tree-sitter·MCP Python SDK 재사용 |
| Q2 | 저장 백엔드 | **SQLite + 벡터 확장(sqlite-vec)** | 임베디드·설치 간편, 벡터 유사도 로컬 처리 |
| Q3 | LLM/임베딩 제공자 | **서버 LLM-free**; 요약은 Agent가 수행 | 외부 LLM API 미호출 |
| CQ1 | 임베딩 벡터 생성 | **서버 내장 경량 로컬 임베딩 모델** (예: fastembed/sentence-transformers 소형·오프라인) | LLM API 호출 없이 벡터 생성, sqlite-vec와 정합 |
| CQ2 | 인제스천/요약 실행 | **Agent 주도(interactive)** | 서버=결정론적 작업(파싱·청킹·관계·저장·검색·임베딩), 요약 텍스트=Agent가 생성 후 도구로 저장 |
| Q4 | MCP transport | **stdio** | 로컬 에이전트 표준, 설치 간편 (Graphify `serve.py` 참고) |
| Q5 | Web Viewer | **정적 HTML + D3.js** | 빌드 도구 불필요, 서빙 단순 (Graphify `tree_html.py` 스타일) |
| Q6 / CQ3 | 배포·설치 | **복사형 설치 스크립트 + Agent가 읽는 README** | 시스템을 대상 프로젝트에 복사 후 MCP 설정 자동 추가 |
| CQ3-1 | 지식 DB 위치 | **대상 프로젝트 내부 숨김 디렉토리** (`.knowledge-store/`) | |
| CQ3-2 | MCP 클라이언트 자동설정 대상 | **Claude Code (`.mcp.json`) 및 opencode** | 감지 시 자동 설정 + README 안내 |
| Q7 | 코드 파싱 언어 범위 | **tree-sitter 다수 언어** (Graphify 추출기 재사용) | |
| Q8 | 오픈소스 활용 | **Graphify + obsidian-wiki 적극 참고·부분 이식** | 라이선스 고지·NOTICE 보존 준수 |
| Q9 | 청크 버전 대응 판별 | **텍스트 유사도/해시 기반 매칭** (MinHash/편집거리) | LLM 비용 없음 |

### Extension Configuration
| Extension | Enabled | Mode |
|---|---|---|
| Security Baseline | No | — |
| Property-Based Testing | Yes | **Partial** (PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 강제) |
| Resiliency Baseline | No | — |

---

## 2. Architecture Overview (Confirmed)

Dual-Interface 시스템은 하나의 지식 저장소를 공유하는 세 계층으로 구성:

```
+-------------------+        +-------------------+
|  Agent (MCP)      |        |  Human (Browser)  |
|  Claude Code /    |        |  Static HTML+D3   |
|  opencode         |        |  Wiki Viewer      |
+---------+---------+        +---------+---------+
          | stdio (MCP)                | file:// or local serve
          v                            v
+-------------------------------------------------+
|            Knowledge Engine (Python)            |
|  Ingestion | Chunking | Structure Modeling      |
|  Relationship Construction | Versioning         |
|  Local Embedding (offline) | Search             |
|  (LLM-free: summaries supplied by the Agent)    |
+------------------------+------------------------+
                         |
                         v
        +----------------------------------+
        |  Knowledge Store                 |
        |  SQLite + sqlite-vec             |
        |  in <target>/.knowledge-store/   |
        +----------------------------------+
```

- **서버는 LLM-free**: 결정론적 파싱·청킹·관계구축·저장·검색과 로컬 임베딩만 수행. **요약 생성은 Agent가 MCP 도구를 통해 수행**하고 결과를 다시 저장(interactive ingestion)하는 모델.

---

## 3. Functional Requirements

### FR-1. Multi-format Ingestion & Chunking (Core)
- **FR-1.1** 다음 포맷을 수집·분석: **Code(다언어)**, **Markdown**, **PDF**, **xlsx**, **csv**.
- **FR-1.2** PDF는 텍스트뿐 아니라 **문서 내 표(Table)** 내용까지 추출. xlsx/csv는 시트·표 데이터 추출.
- **FR-1.3** 수집 문서는 **의미 단위(섹션/문단/표 등)로 청크(Chunk)** 분절화하여 저장. 이후 **관계 연결·검색·요약의 최소 단위는 청크**.
- **FR-1.4** 인제스천은 **Agent 주도 interactive** 방식: 서버는 파싱·청킹·저장을 결정론적으로 수행하는 MCP 도구를 노출.

### FR-2. Code Structure Modeling (Core)
- **FR-2.1** **tree-sitter 기반**으로 다수 프로그래밍 언어의 파일/함수/클래스 간 관계(**정의·호출·의존·상속/포함**)를 추출(결정론적, LLM-free). Graphify 추출기 로직 참고·이식.
- **FR-2.2** 파일 간 심볼 해석(symbol resolution)을 수행하여 코드의 논리적 구조를 **그래프로 모델링·저장**.

### FR-3. Relationship Construction: Code ↔ Document Chunk (Core)
함수/클래스와 문서 청크 간 관계를 아래 세 방식으로 도출·저장:
- **FR-3.1 임베딩/벡터 유사도**: 서버 내장 **로컬 임베딩 모델**로 코드·청크 임베딩 생성 → **sqlite-vec**로 유사도 기반 연결.
- **FR-3.2 Markdown 링크 파싱**: 청크 내 명시적 마크다운 링크(`[[wikilink]]`/일반 링크) 파싱하여 참조 관계 연결.
- **FR-3.3 태그 기반 연결**: 코드/청크 태그 매칭으로 관계 연결.

### FR-4. Document Versioning (Core)
- **FR-4.1** 버전 관리는 **청크 단위**로 수행.
- **FR-4.2** 문서 추가 시 청크 단위로 기존 청크와 내용 비교. **대응 판별은 텍스트 유사도/해시(MinHash/편집거리)** 기반.
- **FR-4.3** 대응되는 기존 청크(OLD ver)가 존재하면 해당 청크를 **신규 버전(NEW ver)** 으로 업데이트.

### FR-5. Summarization (Agent-driven)
- **FR-5.1** 코드/문서 청크의 요약은 **Agent가 MCP 도구 결과를 받아 생성**하고, 도구를 통해 지식 저장소에 저장.
- **FR-5.2** 서버는 요약 저장·조회 도구와, 요약 대상 콘텐츠 추출 도구를 제공(LLM 직접 호출 없음).

### FR-6. Agent Interface — MCP Server (stdio)
- **FR-6.1 MCP Resources**: 프로젝트 구조(Structure), 파일/모듈 요약(Summary), 관계/의존(Relationship) 데이터를 URI 형태로 노출.
- **FR-6.2 MCP Tools** (최소):
  - **Semantic Query Tool**: 의도(Intent) 기반 정보 검색.
  - **Smart Snippet Tool**: 요청 컨텍스트의 토큰 양을 고려해 최적 코드 범위(Scope)를 잘라 제공.
  - **Ingestion/Update Tools**: 문서·코드 수집, 청킹, 요약 저장, 위키 반영.
- **FR-6.3 Agent Discoverability**: 모든 Tools/Resources에 명확한 **Description·사용 지침(용도·입력·출력·사용 시점)** 제공. 시스템 존재·활용 방법이 Agent 컨텍스트에 자동 노출·발견 가능해야 함.

### FR-7. Human Interface — Web Viewer (Static HTML + D3)
- **FR-7.1 Interactive Tree View**: 디렉토리 및 논리적 의존 구조 시각화(접이식 트리, D3).
- **FR-7.2 Dependency Visualization**: 코드 간 관계를 그래프로 시각화.
- **FR-7.3 Wiki Content Viewer**: 마크다운 기반 위키 콘텐츠 렌더링.
- **FR-7.4 Content Review**: 사람이 위키 내용을 검토하고, 엔진/Agent의 자동 업데이트 결과를 확인(수동 편집/동기화 검토).

### FR-8. Deployment & Installation
- **FR-8.1** 시스템을 **대상 프로젝트 폴더에 복사**하고, 환경에 맞는 **MCP 설정을 자동 추가**하는 설치 스크립트 제공.
- **FR-8.2** 지식 저장소 데이터는 대상 프로젝트 내부 **`.knowledge-store/`** (숨김 디렉토리)에 저장.
- **FR-8.3** MCP 클라이언트 자동 설정 대상: **Claude Code(`.mcp.json`)** 및 **opencode**. 감지되지 않는 경우 README에 수동 설정 스니펫 안내.
- **FR-8.4** **Agent가 읽고 수행 가능한 설치 설명서**를 `README.md`에 기술. 사전 요구사항(Prerequisite)을 최소화·명확히 문서화.

---

## 4. Non-Functional Requirements

### NFR-1. Performance (Agent Experience)
- **NFR-1.1 Low Latency**: 핵심 조회 MCP Tool 응답 **1초 이내** 목표(에이전트 루프 방해 최소화).
- **NFR-1.2 Token Efficiency**: 모든 Resource·Tool 결과는 Smart Chunking·요약으로 불필요한 토큰 낭비 최소화.

### NFR-2. Data Consistency
- **NFR-2.1** 위키 구조는 소스 경로·관계 기반으로 생성됨. 대규모 리팩토링(파일 이동 등) 시 재동기화(Re-indexing)로 불일치 해소.
- **NFR-2.2** 청크 버전 매칭은 텍스트 유사도/해시 정확도에 의존.

### NFR-3. Cost & Resources
- **NFR-3.1** **외부 LLM/임베딩 API 호출 없음** → API 비용·네트워크 지연 제거. 임베딩은 로컬 모델로 수행(로컬 컴퓨팅 자원 사용).
- **NFR-3.2** 프로젝트 규모 증가 시 그래프 구성·파싱 컴퓨팅 자원 증가.

### NFR-4. Installability
- **NFR-4.1** 설치 간편성 최우선. 복잡한 수동 설정 지양, 스크립트 실행 수준의 설치/설정.
- **NFR-4.2** Prerequisite 최소화·명확 문서화.

### NFR-5. Agent Discoverability
- **NFR-5.1** Agent가 시스템의 기능·도구·리소스를 스스로 인지하고, 적절한 시점에 자율 호출 가능해야 함(별도 수동 안내 없이 발견 가능).

### NFR-6. Environment Assumptions
- **NFR-6.1** 파일시스템 기반 로컬/네트워크 드라이브 환경, Git 사용 환경을 상정.

### NFR-7. Licensing (참고 오픈소스 이식 시)
- **NFR-7.1** Graphify(Apache-2.0), obsidian-wiki(MIT) 코드 이식 시 **저작권/라이선스 고지 유지, NOTICE/LICENSE 파일 보존**.

### NFR-8. Testing (Extension: PBT Partial)
- **NFR-8.1** Property-Based Testing **Partial 모드** 적용: PBT-02(round-trip), PBT-03(invariant), PBT-07(generator quality), PBT-08(shrinking/reproducibility), PBT-09(framework selection) 강제. Python이므로 **Hypothesis** 프레임워크 채택 예정.
- **NFR-8.2** 특히 청킹·직렬화·파싱/포맷팅·해시 기반 매칭 등 순수 함수 및 직렬화 왕복(round-trip)에 PBT 적용.

---

## 5. Out of Scope (from constraints.md)

- 실시간 파일시스템 감시/자동 동기화(MVP 이후).
- CI/CD 파이프라인 긴밀 통합·자동 배포 연동.
- 심화 OCR, PDF 내 복잡한 차트/다이어그램 논리 구조 완전 복원.
- 지원 외 문서 포맷(PPT, HWP, 이미지 등).
- 초대규모(TB급) 코드베이스 실시간 인덱싱 성능 보장.
- Slack/Teams 등 메신저 양방향 실시간 알림 연동.

---

## 6. MVP Scope (필수)

- **MCP Server Core**: 기본 Resources + Tools(Semantic Query, Smart Snippet, Ingestion/Update) — stdio.
- **Ingestion Engine**: 소스 코드(다언어, tree-sitter) + 문서(Markdown/PDF/xlsx/csv) 분석·청킹·위키화.
- **Knowledge Store**: SQLite + sqlite-vec + 로컬 임베딩.
- **Relationship Construction**: 임베딩 유사도 + 마크다운 링크 + 태그.
- **Chunk Versioning**: 해시/텍스트 유사도 기반.
- **Basic Web Viewer**: 정적 HTML + D3 트리/그래프 + 마크다운 뷰어.
- **Easy Installation**: 복사형 설치 스크립트 + `.mcp.json`/opencode 자동 설정 + Agent-readable README.

---

## 7. Key Requirements Summary

- Python 기반, **LLM-free 서버 + 로컬 임베딩** + **Agent 주도 요약**의 MCP(stdio) 지식 저장소.
- **SQLite + sqlite-vec** 단일 임베디드 저장소, 대상 프로젝트 `.knowledge-store/`에 위치.
- tree-sitter 다언어 코드 그래프 + 다포맷 문서 청킹 + 3방식 관계 연결 + 해시 기반 청크 버전 관리.
- 정적 HTML + D3 Web Viewer(트리/그래프/위키).
- 복사형 설치 스크립트로 Claude Code/opencode에 MCP 자동 설정.
- Graphify/obsidian-wiki 적극 참고·부분 이식(라이선스 준수).
- 확장: Security No / PBT Partial(Hypothesis) / Resiliency No.
