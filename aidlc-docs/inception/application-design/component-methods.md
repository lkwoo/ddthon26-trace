# Component Methods — Application Design

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Application Design (Part 2: Generation)
> **작성일**: 2026-09-08
> **범위**: 고수준 메서드 시그니처 + 입출력 타입 + 목적. **상세 비즈니스 규칙/알고리즘/스키마는 Functional Design(per-unit, CONSTRUCTION)에서 정의.**
> **표기**: Python 타입 힌트 스타일(가안). 명칭/시그니처는 Functional Design에서 확정.

---

## 1. Domain Models (`domain/models.py`)

> 불변 데이터 클래스. 직렬화 계약(`to_dict`/`from_dict`)은 US-N6 round-trip PBT 대상.

| 타입 | 핵심 필드(가안) | 목적 |
|---|---|---|
| `SourceFile` | `path: str`, `language: str`, `content: str` | 인제스천 대상 파일 |
| `ParsedUnit` | `file: SourceFile`, `symbols: list[Symbol]`, `references: list[Reference]`, `doc_elements: list[DocElement]` | 파서 산출물 |
| `Symbol` | `id: str`, `kind: Literal['file','function','class']`, `name: str`, `location: Span` | 그래프 노드 |
| `Edge` | `src: str`, `dst: str`, `kind: Literal['call','dependency']` | 그래프 엣지 |
| `RelationshipGraph` | `nodes: list[Symbol]`, `edges: list[Edge]` | 관계 그래프 |
| `StructureTree` | `root: TreeNode` | 논리 계층 구조 |
| `ModuleSummary` | `target: str`, `signatures: list[str]`, `docstrings: list[str]`, `headings: list[str]` | 결정적 구조 요약 |
| `AgentNote` | `target: str`, `body_md: str`, `author: str`, `created_at: str` | 에이전트 심화 요약(Q6 별도 네임스페이스) |
| `Snippet` | `text: str`, `estimated_tokens: int`, `truncated: bool` | 토큰 최적화 스니펫 |
| `SearchResult` | `target: str`, `score: float`, `kind: str` | 검색 결과 항목 |
| `SyncReport` | `files_total: int`, `symbols_total: int`, `skipped: list[str]`, `failures: list[str]`, `duration_ms: int` | 재동기화 리포트(US-N7) |

**공통 메서드**: `to_dict(self) -> dict`, `@classmethod from_dict(cls, d: dict) -> Self` — 직렬화 왕복 불변식 대상.

---

## 2. Domain Logic (순수 함수)

### GraphBuilder (`domain/graph_builder.py`)
- `build(units: list[ParsedUnit]) -> RelationshipGraph`
  - 목적: 심볼 노드/호출·의존 엣지 구성. 안정 정렬로 결정성 보장(US-E2, US-N4).

### StructuredExtractor (`domain/extractor.py`)
- `extract(unit: ParsedUnit) -> ModuleSummary`
  - 목적: 시그니처/docstring/주석/헤딩에서 구조 요약 산출. LLM 미호출·결정적(US-E3, NFR-C3).

### ChunkingService (`domain/chunking.py`)
- `select_snippet(symbol: Symbol, source_text: str, token_budget: int) -> Snippet`
  - 목적: 예산 내 의미 완결 스니펫. 초과 시 우선순위 축약 + `truncated=True`(US-A3, US-N2).
- `estimate_tokens(text: str) -> int`
  - 목적: 토큰 추정(예산 관리 정보 제공, US-A3 AC-2).

### QueryEngine (`domain/query.py`)
- `search_keyword(index: SearchIndex, query: str) -> list[SearchResult]`
  - 목적: 키워드 매칭 + 관련도 정렬(US-A2 AC-1). 무매칭 시 빈 리스트(AC-3).
- `neighbors(graph: RelationshipGraph, symbol_id: str, direction: Literal['callers','callees','deps']) -> list[SearchResult]`
  - 목적: 그래프 인접 심볼 탐색(US-A2 AC-2).

---

## 3. Ports (추상 인터페이스)

### LanguageParserPort (`ports/parser_port.py`)
- `parse(file: SourceFile) -> ParsedUnit` — 파일 파싱(심볼/참조/문서요소 추출).
- `supported_extensions() -> set[str]` — 지원 확장자 집합.

### KnowledgeStorePort (`ports/store_port.py`)
- `save_structure(tree: StructureTree) -> None`
- `save_summary(summary: ModuleSummary) -> None`
- `save_graph(graph: RelationshipGraph) -> None`
- `load_structure() -> StructureTree | None`
- `load_summary(target: str) -> ModuleSummary | None`
- `load_graph() -> RelationshipGraph | None`
- `save_agent_note(note: AgentNote) -> None` — 별도 네임스페이스 저장(Q6).
- `load_agent_notes(target: str) -> list[AgentNote]`
- `exists(target: str) -> bool` — 미존재 리소스 안전 응답 지원(US-A1 AC-4).

### FileSourcePort (`ports/source_port.py`)
- `discover(root: str, filters: SourceFilter) -> list[SourceFile]` — 지원 포맷만, 미지원 건너뜀(US-E1 AC-2).
- `read(path: str) -> str`

---

## 4. Application Services

### SyncService (`application/sync_service.py`)
- `run(project_root: str, mode: Literal['full','resync'] = 'full') -> SyncReport`
  - 목적: 파이프라인 조율(수집→파싱→그래프→추출→저장). 재동기화 시 엔진 우선 재생성 + 에이전트 노트 보존(Q6, FR-C1). 실패/건너뜀/규모 리포트(US-E2 AC-3, US-N7).

### KnowledgeReadService (`application/read_service.py`)
- `get_structure() -> StructureTree | None` — US-A1.1 / US-H1.
- `get_summary(target: str) -> MergedSummary | None`
  - 목적: 엔진 구조 요약 + 에이전트 노트 **병합** 반환(Q6, US-A1.2 / US-H2).
- `get_relationships(target: str | None = None) -> RelationshipGraph | None` — US-A1.3 / US-H3.
- 계측: 각 조회는 지연 계측 훅을 통과(US-N1 AC-2).

### QueryService (`application/query_service.py`)
- `query(text: str, mode: Literal['keyword','graph','auto'] = 'auto') -> list[SearchResult]` — US-A2.

### SnippetService (`application/snippet_service.py`)
- `snippet(target: str, token_budget: int) -> Snippet` — US-A3.

### UpdateService (Update Tool 백엔드; `application/`)
- `apply_note(payload: AgentNotePayload) -> UpdateResult`
  - 목적: 에이전트 심화 요약 검증 후 별도 네임스페이스 저장(US-A4). 유효성 실패 시 변경 없이 검증 오류(AC-3).

---

## 5. Inbound Adapters (얇은 위임)

### MCP Server (`adapters/inbound/mcp/`)
- **ResourcesProvider**
  - `list_resources() -> list[ResourceDescriptor]`
  - `read_resource(uri: str) -> ResourceContent` — `KnowledgeReadService` 위임. 미존재 시 "리소스 없음"(US-A1 AC-4).
- **ToolsProvider**
  - `query_tool(text, mode) -> ...` → `QueryService`
  - `snippet_tool(target, token_budget) -> ...` → `SnippetService`
  - `update_tool(payload) -> ...` → `UpdateService`
  - `sync_tool(mode) -> SyncReport` → `SyncService` (**Q5=B**: MCP가 재동기화 트리거)
- **PromptsProvider**
  - `list_prompts() -> list[PromptDescriptor]`, `get_prompt(name, args) -> PromptMessages` (US-A5).
- **StdioTransport**
  - `serve() -> None` — stdio 핸드셰이크·목록 노출(US-A6).

### Web Viewer (`adapters/inbound/web/`)
- `render_tree() -> HTML` (US-H1) · `render_wiki(target) -> HTML` (US-H2, Markdown→HTML)
- `render_graph() -> HTML` (US-H3) · `render_review(target) -> HTML` (US-H4, 엔진 우선 고지)
- 모두 `KnowledgeReadService` 데이터 사용, SSR 렌더(FR-H5).

### CLI (`adapters/inbound/cli/`)
- `main(argv) -> int` — 서브커맨드 디스패치.
- `cmd_ingest(args)` / `cmd_sync(args)` → `SyncService.run(...)`
- `cmd_serve_mcp(args)` → MCP `StdioTransport.serve()`
- `cmd_serve_web(args)` → Web 서버 기동

---

## 6. Outbound Adapters

### ParserRegistry (`adapters/outbound/parsers/`)
- `register(parser: LanguageParserPort) -> None` — 코어 수정 없이 등록(US-N4).
- `for_file(path: str) -> LanguageParserPort | None` — 확장자 매핑. 없으면 `None`(건너뜀).

### FileSystemKnowledgeStore (`adapters/outbound/store/`)
- `KnowledgeStorePort` 전체 구현. Markdown+JSON, 결정적 직렬화(US-E4/N5). 에이전트 노트 별도 경로(Q6).

### FileSystemSource (`adapters/outbound/source/`)
- `FileSourcePort` 구현 — 로컬 순회/읽기(US-E1, NFR-E1).

---

> **주의**: 위 시그니처는 컴포넌트 경계·계약 확정용 **고수준 정의**이다. 인자 세부, 검증 규칙, 예외 정책, URI 스킴, JSON 스키마, 청킹/검색 알고리즘 등 **상세 비즈니스 규칙은 Functional Design(per-unit)** 에서 정의한다.
