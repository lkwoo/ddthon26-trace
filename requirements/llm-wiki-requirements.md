# Agentic Knowledge Base (MCP-based) 요구사항 정의서

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
- **MCP Prompts**: 에이전트의 특정 작업(예: 리팩토링, 버그 수정)에 최적화된 지식 활용 프롬프트 템플릿 제공.

### 2.2 Human Interface (Web Viewer)
사람이 프로젝트 지식을 탐색하기 위한 인터페이스입니다.
- **Interactive Tree View**: 프로젝트의 디렉토리 및 논리적 의존성 구조를 시각화.
- **Wiki Content Viewer**: 마크다운 기반으로 정리된 프로젝트 명세 및 코드 설명을 웹에서 렌더링.

### 2.3 Knowledge Engine (Core)
지식을 생성하고 관리하는 핵심 엔진입니다.
- **Ingestion Pipeline**: 다양한 파일 형식(Code, Markdown, PDF, HTML, etc.)의 수집 및 분석.
- **Graph Construction**:  기술 등을 활용하여 파일/함수/클래스 간의 관계 모델링.
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

#### 3.1.3 Prompt Templates
- **Onboarding Prompt**: 새로운 에이gent가 프로젝트에 투입될 때 프로젝트 전체 맥락을 빠르게 학습하도록 돕는 프롬프트.
- **Task-Specific Prompt**: 특정 작업(예: Unit Test 작성) 수행 시 필요한 지식만 집중적으로 제공하는 프롬프트.

### 3.2 Human-Centric Features (via Web UI)

#### 3.2.1 Visual Wiki Exploration
- **Hierarchical Navigation**: 트리 구조를 통한 직관적인 파일 탐색.
- **Dependency Visualization**: 코드 간의 관계를 그래프 형태로 시각화하여 논리적 흐름 파악 지원.

#### 3.2.2 Content Review & Management
- **Markdown Rendering**: 구조화된 위키 내용을 읽기 쉬운 형태로 표시.
- **Manual Edit/Sync**: 사람이 직접 위키 내용을 수정하거나, 엔진의 자동 업데이트 결과 검토.

### 3.3 Common Engine Requirements (Core)

#### 3.3.1 Multi-format Ingestion
- 코드, Markdown, PDF, HTML, PPT 등 다양한 포맷의 분석 및 구조화 지원.

#### 3.3.2 Graph-based Modeling
- 단순 파일 목록이 아닌, 코드의 실행 흐름과 의존성을 반영한 그래프 구조 생성.

---

## 4. MVP 개발 범위

### 핵심 기능 (필수)
- **MCP Server Core**: 기본적인 Resources 및 Tools 구현.
- **Basic Web Viewer**: 마크다운 기반 파일 트리 및 뷰어.
- **Ingestion Engine**: 소스 코드 및 Markdown 파일의 분석 및 위키화.

---

## 5. 부록
### A. 용어 정의
- **MCP (Model Context Protocol)**: LLM 에이전트와 외부 데이터/도구를 연결하기 위한 표준 프로토콜.
- **Agentic Context**: 에이전트가 작업을 수행하기 위해 필요한 최적화된 상태의 정보 묶음.
- **Dual-Interface**: 에이전트(MCP)와 사람(Web UI)이라는 두 종류의 사용자에게 최적화된 인터페이스를 동시에 제공하는 설계 방식.
