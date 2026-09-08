# Components — Application Design

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Application Design (Part 2: Generation)
> **작성일**: 2026-09-08
> **아키텍처 스타일**: 포트 & 어댑터(헥사고날) — 단일 Python 패키지 + 내부 모듈 (Q1=A, Q7=A)
> **입력 산출물**: `application-design-plan.md`(답변 확정), `requirements.md`, `stories.md`, `personas.md`

---

## 0. 설계 결정 요약 (Confirmed Design Decisions)

| # | 결정 | 근거 스토리/요구 |
|---|---|---|
| Q1=A | **단일 Python 패키지 `agentic_kb/` + 내부 모듈** | 로컬 단일 사용자, 최소 의존성(P2) |
| Q2=A | **공유 `KnowledgeStore` 읽기 계층** — MCP/Web 모두 이를 통해 접근 | US-A1, US-H2/H4, 결합도↓ |
| Q3=A | **인메모리 파서 레지스트리** — 공통 `LanguageParser` 인터페이스 | US-E2, US-N4, NFR-C2 |
| Q4=A | **단일 `SyncService` 파이프라인** (ingest→parse→graph→extract→persist) | US-E1~E5 |
| Q5=B | **MCP 서버가 인제스천/재동기화 Tool 트리거 가능** | US-A6, US-E5 |
| Q6=A | **에이전트 노트 별도 네임스페이스, 조회 시 병합** | US-A4, FR-C1 |
| Q7=A | **포트 & 어댑터(헥사고날)** — 코어 도메인 + 어댑터 | 테스트성, US-N6(PBT 순수함수 분리) |
| Q8=A | **단일 CLI + 서브커맨드** (`ingest`/`sync`/`serve-mcp`/`serve-web`) | US-A6, US-E1/E5 |

**아키텍처 원칙**: 코어 도메인은 **순수·결정적·I/O 없음·LLM 미호출**(NFR-C3). 모든 파일/전송/외부 상호작용은 **어댑터**에 격리된다. 이는 US-N6(순수 함수·직렬화 round-trip PBT) 적용 지점을 명확히 분리한다.

---

## 1. 패키지 레이아웃 (Module Layout)

```
agentic_kb/
├── domain/                # 코어 도메인 (순수·결정적·I/O 없음·LLM 미호출)
│   ├── models.py          # 데이터 모델
│   ├── graph_builder.py   # 관계 그래프 구성 (순수)
│   ├── extractor.py       # 결정적 구조 추출 (순수)
│   ├── chunking.py        # 토큰 예산 스니펫/청킹 (순수)
│   └── query.py           # 키워드 + 그래프 검색 (순수)
├── ports/                 # 추상 인터페이스 (Protocol/ABC)
│   ├── parser_port.py     # LanguageParser (driven)
│   ├── store_port.py      # KnowledgeStore (driven)
│   └── source_port.py     # FileSource (driven)
├── application/           # 애플리케이션 서비스 (유즈케이스 오케스트레이션)
│   ├── sync_service.py    # SyncService (파이프라인)
│   ├── read_service.py    # KnowledgeReadService (조회 파사드)
│   ├── query_service.py   # QueryService
│   └── snippet_service.py # SnippetService
├── adapters/
│   ├── inbound/           # 구동(Driving) 어댑터
│   │   ├── mcp/           # MCP 서버: resources/tools/prompts/stdio
│   │   ├── web/           # 경량 SSR 웹 뷰어
│   │   └── cli/           # CLI 서브커맨드
│   └── outbound/          # 피구동(Driven) 어댑터
│       ├── parsers/       # tree-sitter LanguageParser 구현 + 레지스트리
│       ├── store/         # FileSystemKnowledgeStore (Markdown+JSON)
│       └── source/        # FileSystemSource
├── config.py              # 설정(경로/네임스페이스/토큰 기본값)
└── __main__.py            # 단일 CLI 진입점 (서브커맨드 디스패치)
```

---

## 2. 코어 도메인 컴포넌트 (Core Domain — 순수/결정적)

### 2.1 Domain Models (`domain/models.py`)
- **목적**: 시스템 전반에서 공유되는 불변(immutable) 데이터 구조 정의.
- **책임**:
  - `FileNode`, `Symbol`(함수/클래스), `Edge`(call/dependency), `StructureTree`, `ModuleSummary`, `RelationshipGraph`, `Snippet`, `SearchResult`, `AgentNote`, `SyncReport` 등 정의.
  - JSON 직렬화/역직렬화 대상(그래프/구조) — round-trip 불변식(US-N6 AC-1) 검증 대상.
- **인터페이스**: 순수 데이터 클래스 + `to_dict()`/`from_dict()` (직렬화 계약).

### 2.2 GraphBuilder (`domain/graph_builder.py`)
- **목적**: 파서가 산출한 심볼/참조로부터 관계 그래프를 **결정적**으로 구성.
- **책임**: 심볼 노드 생성, 호출/의존 엣지 연결, 안정적 정렬(결정성). US-E2, US-N4.
- **인터페이스**: `build(parsed_units) -> RelationshipGraph` (순수 함수).

### 2.3 StructuredExtractor (`domain/extractor.py`)
- **목적**: LLM 없이 시그니처/docstring/주석/Markdown 헤딩에서 구조적 요약 생성.
- **책임**: 파일/모듈 단위 `ModuleSummary` 산출. 동일 입력 → 동일 출력(US-E3 AC-3). NFR-C3.
- **인터페이스**: `extract(parsed_unit) -> ModuleSummary` (순수 함수).

### 2.4 ChunkingService (`domain/chunking.py`)
- **목적**: 토큰 예산에 맞춘 의미 완결 스니펫 선택·축약.
- **책임**: 범위 선택, 예산 초과 시 우선순위 축약 + 절단 표시(US-A3, US-N2).
- **인터페이스**: `select_snippet(symbol, source_text, token_budget) -> Snippet` (순수 함수).

### 2.5 QueryEngine (`domain/query.py`)
- **목적**: 키워드 + 그래프 기반 검색 로직.
- **책임**: 키워드 매칭·관련도 정렬, 그래프 인접(호출/참조) 탐색(US-A2). 빈 결과 안전 반환.
- **인터페이스**: `search_keyword(index, query) -> list[SearchResult]`, `neighbors(graph, symbol_id, direction) -> list[SearchResult]` (순수 함수).

---

## 3. 포트 (Ports — 추상 인터페이스)

### 3.1 LanguageParserPort (`ports/parser_port.py`) — Driven
- **목적**: 언어별 파서 플러그인 계약.
- **책임**: 파일 → 심볼/참조/구조 요소 파싱. tree-sitter 기반 구현을 어댑터로 격리.
- **인터페이스**: `parse(file: SourceFile) -> ParsedUnit`, `supported_extensions() -> set[str]`.

### 3.2 KnowledgeStorePort (`ports/store_port.py`) — Driven
- **목적**: 지식 산출물의 저장/조회 계약 (Markdown+JSON). Q2의 공유 접근 지점.
- **책임**: 구조/요약/그래프/에이전트 노트의 결정적 저장·로드. 에이전트 노트는 별도 네임스페이스(Q6).
- **인터페이스**: `save_*`, `load_structure/summary/graph`, `save_agent_note/load_agent_notes`.

### 3.3 FileSourcePort (`ports/source_port.py`) — Driven
- **목적**: 인제스천 대상 파일 수집·읽기 계약.
- **책임**: 경로 순회, 지원 포맷 필터(코드/Markdown), 미지원 건너뛰기(US-E1 AC-2).
- **인터페이스**: `discover(root, filters) -> list[SourceFile]`, `read(path) -> str`.

---

## 4. 애플리케이션 서비스 (Application Services — 오케스트레이션)

### 4.1 SyncService (`application/sync_service.py`)
- **목적**: 인제스천→파싱→그래프→추출→저장 **파이프라인** 조율 (Q4=A).
- **책임**: `FileSource`로 수집 → `ParserRegistry`로 파싱 → `GraphBuilder`/`StructuredExtractor` → `KnowledgeStore` 저장. 재동기화 시 엔진 우선 재생성, 에이전트 노트 보존(Q6). 처리 규모/실패 리포트(US-N7, US-E2 AC-3).
- **인터페이스**: `run(project_root, mode) -> SyncReport`.

### 4.2 KnowledgeReadService (`application/read_service.py`)
- **목적**: MCP Resources 및 Web Viewer의 **공유 읽기 파사드** (Q2=A).
- **책임**: 구조/요약/관계 조회, 에이전트 노트 병합(Q6), 조회 지연 계측(US-N1 AC-2).
- **인터페이스**: `get_structure()`, `get_summary(target)`, `get_relationships(target)`.

### 4.3 QueryService (`application/query_service.py`)
- **목적**: 검색 유즈케이스 조율(인덱스/그래프 로드 → `QueryEngine` 호출).
- **인터페이스**: `query(text, mode) -> list[SearchResult]`.

### 4.4 SnippetService (`application/snippet_service.py`)
- **목적**: 스니펫 유즈케이스 조율(대상 소스 로드 → `ChunkingService` 호출).
- **인터페이스**: `snippet(target, token_budget) -> Snippet`.

---

## 5. 인바운드 어댑터 (Driving Adapters)

### 5.1 MCP Server Adapter (`adapters/inbound/mcp/`)
- **목적**: 에이전트(P1)용 MCP 인터페이스. **stdio 전송**(FR-A6).
- **하위 컴포넌트/책임**:
  - **ResourcesProvider**: 구조/요약/관계 Resource(URI) 노출 → `KnowledgeReadService` 위임 (US-A1).
  - **ToolsProvider**: Query/Snippet/Update Tool + **Sync/Ingest Tool**(Q5=B) → 각 서비스 위임 (US-A2/A3/A4, US-E5).
  - **PromptsProvider**: 온보딩/작업별 프롬프트 템플릿 (US-A5).
  - **StdioTransport**: 서버 기동·핸드셰이크·목록 노출 (US-A6).
- **특성**: 어댑터는 얇은 위임 계층 — 도메인 로직 없음.

### 5.2 Web Viewer Adapter (`adapters/inbound/web/`)
- **목적**: 개발자(P2)용 경량 **SSR** 웹 뷰어 (FR-H5).
- **책임**: 트리 뷰(US-H1), 위키 Markdown→HTML 렌더(US-H2), 의존성 그래프 뷰(US-H3), 검토 뷰 + 엔진 우선 고지(US-H4/FR-C1). `KnowledgeReadService`로 데이터 획득.

### 5.3 CLI Adapter (`adapters/inbound/cli/`)
- **목적**: 단일 CLI + 서브커맨드 진입점 (Q8=A).
- **책임**: `ingest`/`sync`(→`SyncService`), `serve-mcp`(→MCP), `serve-web`(→Web). 규모/소요 출력(US-N7).

---

## 6. 아웃바운드 어댑터 (Driven Adapters)

### 6.1 ParserRegistry + TreeSitter Parsers (`adapters/outbound/parsers/`)
- **목적**: `LanguageParserPort` 구현 및 **인메모리 레지스트리**(Q3=A).
- **책임**: 확장자→파서 매핑, 신규 언어를 코어 수정 없이 등록(US-N4). 미지원/파싱 실패 건너뛰기(US-E2 AC-3).
- **인터페이스**: `register(parser)`, `for_file(path) -> LanguageParser | None`.

### 6.2 FileSystemKnowledgeStore (`adapters/outbound/store/`)
- **목적**: `KnowledgeStorePort` 구현 — Markdown+JSON 파일 저장(US-E4, NFR-D1).
- **책임**: 결정적 직렬화(diff 노이즈 최소, US-N5 AC-2), 에이전트 노트 별도 네임스페이스 저장/로드(Q6).

### 6.3 FileSystemSource (`adapters/outbound/source/`)
- **목적**: `FileSourcePort` 구현 — 로컬 파일 순회/읽기(US-E1, NFR-E1).

---

## 7. 컴포넌트 요약 인덱스

| 계층 | 컴포넌트 | 관련 스토리 |
|---|---|---|
| Domain | Models, GraphBuilder, StructuredExtractor, ChunkingService, QueryEngine | US-E2/E3, US-A2/A3, US-N2/N6 |
| Ports | LanguageParserPort, KnowledgeStorePort, FileSourcePort | US-E1/E2/E4, NFR-C2 |
| Application | SyncService, KnowledgeReadService, QueryService, SnippetService | US-E1~E5, US-A1~A4 |
| Inbound Adapter | MCP(Resources/Tools/Prompts/stdio), Web(SSR), CLI | US-A1~A6, US-H1~H4 |
| Outbound Adapter | ParserRegistry+Parsers, FileSystemKnowledgeStore, FileSystemSource | US-E2/E4, US-N4/N5 |

> 상세 메서드 시그니처는 `component-methods.md`, 서비스 오케스트레이션은 `services.md`, 의존/통신은 `component-dependency.md` 참조. 상세 비즈니스 규칙·스키마는 이후 Functional Design(per-unit)에서 정의한다.
