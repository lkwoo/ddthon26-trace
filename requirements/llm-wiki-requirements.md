# Dual-Interface Knowledge Store 요구사항 정의서

## 1. 프로젝트 개요

### 1.1 프로젝트 비전
LLM 에이전트가 프로젝트의 맥락(Context)를 완벽하게 이해하고 작업을 수행할 수 있도록, 코드와 문서를 구조화된 지식(Knowledge)으로 변환하여 제공하는 **MCP(Model Context Protocol) 기반의 Agentic Knowledge Base** 구축. 에이전트에게는 최적화된 컨텍스트를, 사람에게는 시각화된 위키를 제공하는 Dual-Interface 모델을 지향함.

### 1.2 핵심 가치 제안

**A. Agent 관점 (Efficiency & Precision)**
- **Token-Optimized Context**: 에이전트의 컨텍스트 윈도우를 낭비하지 않도록, 필요한 정보만을 요약 및 추출하여 제공.
- **Tool-Driven Interaction**: 에이전트가 직접 검색, 구조 조회, 업데이트를 수행할 수 있는 표준화된 MCP 인터페이스 제공.
- **Semantic Understanding**: 단순 텍스트 매칭을 넘어, 코드의 논리적 관계(Call Graph 등)를 기반으로 한 고차원적 맥락 제공.

**B. Human 관점 (Visibility & Control)**
- **Visualized Knowledge**: 복잡한 코드 구조와 파일 간 관계를 시각적인 위키(Wiki) 형태로 제공하여 직관적 파악 지원.
- **Easy Inspection**: 에이전트가 생성/수정한 지식 베이스를 사람이 쉽게 검토하고 수정할 수 있는 인터페이스 제공.

---

## 2. 시스템 아키텍처 (Dual-Interface)

### 2.1 Agent Interface (MCP Server)
에이전트가 MCP 프로토콜을 통해 접근하는 인터페이스입니다.
- **MCP Resources**: 프로젝트 구조, 파일 요약본, 관계 그래프 데이터를 URI 형태로 제공.
- **MCP Tools**: 
    - : 의미 기반 정보 검색.
    - : 특정 코드/파일의 토큰 최적화된 스니펫 추출.
    - : 에이전트의 작업 결과를 위키에 반영.

### 2.2 Human Interface (Web Viewer)
사람이 프로젝트 지식을 탐색하기 위한 인터페이스입니다.
- **Interactive Tree View**: 프로젝트의 디렉토리 및 논리적 의존성 구조를 시각화.
- **Wiki Content Viewer**: 마크다운 기반으로 정리된 프로젝트 명세 및 코드 설명을 웹에서 렌더링.

### 2.3 Knowledge Engine (Core)
지식을 생성하고 관리하는 핵심 엔진입니다.
- **Ingestion Pipeline**: 지원 문서 형식(Code, Markdown, PDF, xlsx, csv)의 수집 및 분석. PDF는 텍스트뿐 아니라 문서 내 표(Table) 내용까지 추출.
- **Chunking Engine**: 문서를 의미 단위(섹션/문단/표 등)로 **분절화(Chunk)** 하여 저장. 관계 연결과 검색의 최소 단위는 전체 문서가 아닌 분절화된 청크(Chunk)로 함.
- **Structure Modeling**: 파일/함수/클래스 간의 구조적 관계(정의, 호출, 의존, 상속/포함 등)를 분석하여 코드의 논리적 구조를 그래프로 모델링.
- **Relationship Construction**: 함수/클래스와 분절화된 문서 청크 간의 관계를 다음 세 가지 방식으로 도출·저장.
    - **임베딩/벡터 유사도(Embedding/Vector Similarity)**: 코드(함수/클래스)와 문서 청크를 임베딩하여 의미적 유사도 기반으로 관계 연결.
    - **Markdown 링크 파싱(Markdown Link Parsing)**: 문서 청크 내 명시적 마크다운 링크를 파싱하여 참조 관계 연결.
    - **태그 기반 연결(Tag-based Linking)**: 코드/문서 청크에 부여된 태그(Tag)를 매칭하여 관계 연결.
- **Versioning Engine**: 버전 관리는 분절화된 문서 청크(Chunk) 단위로 수행. 신규 문서가 추가되면 청크 단위로 기존 청크(OLD ver)와 내용을 비교하여, 대응되는 기존 청크가 존재하면 해당 청크를 새로운 버전(NEW ver)으로 업데이트.
- **Summarization Engine**: LLM을 활용하여 코드 및 문서의 핵심 내용을 요약.

---

## 3. 핵심 기능 요구사항

### 3.1 Agent-Centric Features (via MCP)

#### 3.1.1 Contextual Resource Exposure
- **Structure Resource**: 프로젝트 전체의 논리적 계층 구조 제공.
- **Summary Resource**: 주요 파일 및 모듈의 핵심 요약 정보 제공.
- **Relationship Resource**: 모듈 간 의존성 및 호출 관계 데이터 제공.

#### 3.1.2 Intelligent Tooling
- **Semantic Query Tool**: 키워드가 아닌 의도(Intent) 기반의 정보 검색.
- **Smart Snippet Tool**: 요청된 컨텍스트의 토큰 양을 고려하여 최적의 코드 범위(Scope)를 잘라서 제공.

### 3.2 Human-Centric Features (via Web UI)

#### 3.2.1 Visual Wiki Exploration
- **Hierarchical Navigation**: 트리 구조를 통한 직관적인 파일 탐색.
- **Dependency Visualization**: 코드 간의 관계를 그래프 형태로 시각화하여 논리적 흐름 파악 지원.

#### 3.2.2 Content Review & Management
- **Markdown Rendering**: 구조화된 위키 내용을 읽기 쉬운 형태로 표시.
- **Manual Edit/Sync**: 사람이 직접 위키 내용을 수정하거나, 엔진의 자동 업데이트 결과 검토.

### 3.3 Common Engine Requirements (Core)

#### 3.3.1 Multi-format Ingestion & Chunking
- 다음 문서 종류의 분석 및 구조화 지원:
    - **Markdown**: 텍스트 및 마크다운 링크 파싱.
    - **PDF**: 텍스트 및 문서 내 표(Table) 내용 추출.
    - **xlsx (Excel)**: 시트 및 표 형태의 데이터 추출.
    - **csv**: 표 형태의 데이터 추출.
- **문서 분절화(Chunking)**: 수집된 문서는 의미 단위(섹션/문단/표 등)로 분절화하여 저장하며, 이후 관계 연결·검색·요약의 최소 단위는 분절화된 청크(Chunk)로 함.

#### 3.3.2 Relationship Modeling & Storage
- **코드 구조 관계 모델링**: 파일/함수/클래스 간의 관계(정의·호출·의존·상속/포함 등)를 분석하여 코드의 논리적 구조를 그래프 형태로 모델링·저장.
- **코드-문서(청크) 관계 저장**: 함수/클래스와 분절화된 문서 청크 간의 관계를 아래 세 가지 방식으로 도출하여 저장:
    - **임베딩/벡터 유사도**: 함수/클래스와 문서 청크의 임베딩 벡터 유사도를 기반으로 의미적으로 관련된 항목을 연결.
    - **Markdown 링크 파싱**: 문서 청크 내 명시적 링크를 파싱하여 참조 관계를 연결.
    - **태그 기반 연결**: 공통 태그를 매칭하여 함수/클래스-문서 청크를 연결.

#### 3.3.3 Document Versioning
- 버전 관리는 분절화된 문서 청크(Chunk) 단위로 수행.
- 문서가 추가될 때 청크 단위로 기존 청크와 내용을 비교하여, 대응되는 기존 청크(OLD ver)가 존재하면 해당 청크를 신규 버전(NEW ver)으로 업데이트하는 방식으로 관리.

---

#### 3.3.4 Agent Discoverability
- 본 시스템이 설치된 프로젝트에서, Agent는 이 시스템이 어떤 동작(제공 기능·도구·리소스)을 수행하는지 스스로 인지할 수 있어야 함.
- 모든 MCP Tools/Resources에 명확한 설명(Description)과 사용 지침(용도·입력·출력·사용 시점)을 제공하여, Agent가 필요한 시점에 스스로 판단하여 호출할 수 있도록 함.
- 시스템의 존재와 활용 방법이 Agent 컨텍스트에서 자동으로 노출·발견 가능해야 함.

### 3.4 Deployment & Installation Requirements

#### 3.4.1 Easy Installation
- 시스템 배포 시 사용자 입장에서 설치를 최대한 간편하게 수행할 수 있어야 함.
- 복잡한 수동 환경 설정을 최소화하고, 단일 명령어 수준의 설치/실행(예: 패키지 매니저 설치, 컨테이너 실행, 원클릭 스크립트 등) 방식을 지향.
- 설치에 필요한 사전 요구사항(Prerequisite)을 최소화하고 명확하게 문서화.

---

## 4. MVP 개발 범위

### 핵심 기능 (필수)
- **MCP Server Core**: 기본적인 Resources 및 Tools 구현.
- **Basic Web Viewer**: 마크다운 기반 파일 트리 및 뷰어.
- **Ingestion Engine**: 소스 코드 및 지원 문서(Markdown, PDF, xlsx, csv)의 분석 및 위키화.
- **Easy Installation**: 사용자가 간편하게 설치·실행할 수 있는 배포 패키지 제공.

---

## 5. 부록
### A. 용어 정의
- **MCP (Model Context Protocol)**: LLM 에이전트와 외부 데이터/도구를 연결하기 위한 표준 프로토콜.
- **Agentic Context**: 에이전트가 작업을 수행하기 위해 필요한 최적화된 상태의 정보 묶음.
- **Dual-Interface**: 에이전트(MCP)와 사람(Web UI)이라는 두 종류의 사용자에게 최적화된 인터페이스를 동시에 제공하는 설계 방식.

### B. 참고 오픈소스 레퍼런스 (Reference Implementations)

본 요구사항의 로직을 구현할 때, 아래 두 오픈소스 레포지토리의 로직 중 **필요한 부분을 선택적으로 가져다 참고·재사용할 수 있음**. 개념 참고, 부분 이식, 라이브러리 의존 등 어떤 방식이든 허용하되, 각 레포의 라이선스 조건을 준수해야 함(저작권/라이선스 고지 유지, NOTICE 파일 보존 등). 각 레포에서 우리 요구사항의 어떤 부분에 활용 가능한지는 아래 매핑을 참고.

#### B.1 Graphify — https://github.com/Graphify-Labs/graphify
- **성격**: 코드·문서·PDF 등을 **지식 그래프(Knowledge Graph)** 로 매핑하는 Python CLI. tree-sitter AST 기반의 결정론적(LLM-free) 코드 파싱과 그래프 순회 질의를 제공. **라이선스: Apache License 2.0** (일부 기여분 MIT, `NOTICE`/`LICENSE-MIT` 참조).
- **활용 가능 로직 매핑**:
    - **2.3 Structure Modeling / 3.3.2 코드 구조 관계 모델링**: `extractors/`(약 40개 언어 tree-sitter 추출기), `extract.py`, `symbol_resolution.py`, `resolver_registry.py`, `cross_repo_calls.py`, `cross_repo_types.py` — 정의·호출·의존·상속 등 코드 관계를 결정론적으로 추출하고 파일 간 심볼을 해석하는 로직.
    - **2.3 Ingestion Pipeline / 3.3.1 Multi-format Ingestion**: `ingest.py`, `manifest_ingest.py`, `mcp_ingest.py`(MCP 서버 설정 추출), `pg_introspect.py` — 다양한 소스의 수집·주석화 로직.
    - **2.3 Chunking Engine / 3.3.1 문서 분절화**: `file_slice.py` — 대용량 문서를 파일 내 단위로 슬라이싱하는 로직.
    - **3.1.2 Smart Snippet Tool**: `file_slice.py`의 스코프 슬라이싱, `dedup.py`/`_minhash.py`(중복 제거) — 토큰 최적화된 스니펫 범위 산정에 참고.
    - **3.1.1 Contextual Resource Exposure / 3.1.2 Intelligent Tooling / 3.3.4 Agent Discoverability**: `serve.py`(MCP stdio 서버, 그래프 질의 도구를 Claude 등 에이전트에 노출) — MCP Tools/Resources 노출 구조의 직접 참고 대상.
    - **3.2.2 Dependency Visualization / Interactive Tree View**: `tree_html.py`(D3 v7 접이식 트리), `callflow_html.py`, `export.py`(HTML/JSON/SVG/GraphML/Obsidian/Neo4j 내보내기) — Web Viewer의 그래프 시각화·내보내기.
    - **3.2 Wiki Content / Summarization Engine(2.3)**: `wiki.py`(그래프 → 위키피디아 스타일 마크다운 아티클), `report.py`(사람이 읽는 요약 리포트), `cluster.py`(Leiden/Louvain 커뮤니티 탐지), `llm.py`(요약).

#### B.2 obsidian-wiki — https://github.com/Ar9av/obsidian-wiki
- **성격**: 문서/대화/PDF 등을 **상호 연결된 마크다운 위키(`[[wikilink]]`)** 로 컴파일·유지하는 Python 도구 및 에이전트 스킬 모음. Karpathy의 "LLM Wiki" 패턴(지식을 한 번 컴파일하여 지속 유지) 기반. **라이선스: MIT.**
- **활용 가능 로직 매핑**:
    - **2.3 Relationship Construction / 3.3.2 Markdown 링크·태그 기반 연결**: `cross-linker` 스킬, `graph_analysis.py`, `.skills/tag-taxonomy` — 마크다운 위키링크 파싱 및 태그 기반으로 신규 페이지를 지식 그래프에 엮는 로직.
    - **2.3 Ingestion Pipeline / 3.3.1 Multi-format Ingestion**: `wiki-ingest`, `wiki-import`, `wiki-history-ingest` 스킬, `batch.py`, `session_sources.py` — 문서·PDF·대화 로그 등 다양한 입력의 수집·정규화.
    - **2.3 Versioning Engine / 3.3.3 Document Versioning**: `sync.py`, `wiki-update`/`wiki-rebuild`/`wiki-dedup` 스킬 — 기존 내용을 갱신·병합·중복 제거하며 위키를 지속 유지하는 로직(청크 단위 버전 관리 설계 참고).
    - **3.3.1 Chunking / Code Understanding**: `ast_extractor.py`, `code_understanding.py`, `code_understanding_codegraph.py`, `code_understanding_builtin.py` — 코드 구조 이해 및 codegraph 연동.
    - **3.1 Semantic Query / Contextual Resource**: `graphrag.py`, `context_pack.py`, `wiki-query`/`wiki-context-pack` 스킬 — 의도 기반 검색과 인용(`[[wikilink]]`) 포함 컨텍스트 패킹.
    - **3.1.1 / 3.3.4 Agent Discoverability & MCP**: `server.py`, `wiki-agent`/`llm-wiki` 스킬 — 에이전트가 위키 기능을 발견·호출하는 인터페이스 참고.
    - **3.2.2 Content Review & Management**: `lint.py`, `wiki-lint`/`wiki-status`/`wiki-dashboard` 스킬 — 깨진 링크·고아 페이지·모순 탐지 등 위키 품질 유지.
    - **3.2.1 Dependency Visualization**: `session_viz.py`, `graph-colorize` 스킬, Obsidian graph view / `graph.json`·GraphML·`graph.html` 내보내기 — 관계 시각화.

> **주의**: 위 매핑은 구현 시 참고를 돕기 위한 가이드이며, 실제 코드 이식·의존 여부는 구현 단계에서 판단함. 코드를 직접 가져다 쓸 경우 해당 레포의 라이선스(Graphify: Apache-2.0, obsidian-wiki: MIT) 고지 의무를 반드시 준수할 것.
