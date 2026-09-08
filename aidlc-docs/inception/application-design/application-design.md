# Application Design (Consolidated)

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Application Design (Part 2: Generation)
> **작성일**: 2026-09-08
> **본 문서**: `components.md`, `component-methods.md`, `services.md`, `component-dependency.md`의 통합본.
> **범위**: 고수준 컴포넌트/서비스/의존 설계. 상세 비즈니스 규칙·스키마·알고리즘은 **Functional Design(per-unit, CONSTRUCTION)** 에서 정의.

---

## 1. 설계 결정 요약

| # | 질문 | 결정 |
|---|---|---|
| Q1 | 코드 구성 | **단일 Python 패키지 `agentic_kb/` + 내부 모듈** |
| Q2 | 코어 지식 접근 | **공유 `KnowledgeReadService`/`KnowledgeStorePort`** (MCP·Web 공용) |
| Q3 | 파서 플러그인 | **인메모리 레지스트리** + 공통 `LanguageParser` 인터페이스 |
| Q4 | 오케스트레이션 | **단일 `SyncService` 파이프라인** |
| Q5 | MCP-엔진 결합 | **MCP가 인제스천/재동기화 Tool 트리거 가능** |
| Q6 | 에이전트 노트 저장 | **별도 네임스페이스 + 조회 시 병합**(엔진 우선 보존) |
| Q7 | 아키텍처 스타일 | **포트 & 어댑터(헥사고날)** |
| Q8 | 진입점 | **단일 CLI + 서브커맨드** (`ingest`/`sync`/`serve-mcp`/`serve-web`) |

**핵심 원칙**: 코어 도메인은 순수·결정적·LLM 미호출·I/O 없음(NFR-C3). 모든 파일/전송/외부 상호작용은 어댑터에 격리 → US-N6(PBT) 적용 지점 명확화.

---

## 2. 아키텍처 개요

```
[에이전트 P1] --stdio--> MCP Server ┐
                                     ├─> Application Services ─> Domain(순수) + Ports
[개발자 P2]  --HTTP---> Web Viewer  ┘                              │
[개발자 P2]  --exec---> CLI ─────────> SyncService                 └─> Outbound Adapters
                                                                        (Source/Parsers/Store)
                                                                        → 파일시스템 (Markdown+JSON)
```

- **Inbound 어댑터**: MCP Server(Resources/Tools/Prompts/stdio), Web Viewer(SSR), CLI.
- **Application 서비스**: SyncService, KnowledgeReadService, QueryService, SnippetService, UpdateService.
- **Domain(순수)**: Models, GraphBuilder, StructuredExtractor, ChunkingService, QueryEngine.
- **Ports**: FileSourcePort, LanguageParserPort, KnowledgeStorePort.
- **Outbound 어댑터**: FileSystemSource, ParserRegistry+TreeSitter, FileSystemKnowledgeStore.

상세 다이어그램·매트릭스는 `component-dependency.md` 참조.

---

## 3. 컴포넌트 (요약)

| 계층 | 컴포넌트 | 핵심 책임 | 스토리 |
|---|---|---|---|
| Domain | Models / GraphBuilder / StructuredExtractor / ChunkingService / QueryEngine | 순수·결정적 로직 | US-E2/E3, US-A2/A3, US-N2/N6 |
| Ports | FileSourcePort / LanguageParserPort / KnowledgeStorePort | 추상 계약 | US-E1/E2/E4, NFR-C2 |
| Application | SyncService / KnowledgeReadService / QueryService / SnippetService / UpdateService | 유즈케이스 조율 | US-A1~A4, US-E1~E5 |
| Inbound | MCP / Web / CLI | 인터페이스 위임 | US-A1~A6, US-H1~H4 |
| Outbound | FileSystemSource / ParserRegistry+TreeSitter / FileSystemKnowledgeStore | 포트 구현 | US-E2/E4, US-N4/N5 |

상세 정의는 `components.md`, 메서드 시그니처는 `component-methods.md` 참조.

---

## 4. 서비스 오케스트레이션 (요약)

- **SyncService**: 수집→파싱→그래프→추출→저장 파이프라인. 엔진 우선 재생성 + 에이전트 노트 보존. SyncReport 반환.
- **KnowledgeReadService**: MCP Resources·Web 공유 읽기 파사드. 구조 요약 + 에이전트 노트 병합, 지연 계측.
- **QueryService / SnippetService**: 검색·토큰 최적 스니펫.
- **UpdateService**: 에이전트 노트 검증·별도 네임스페이스 저장.

상세 흐름은 `services.md` 참조.

---

## 5. 요구사항/스토리 추적성 커버리지

| 영역 | 커버 컴포넌트/서비스 | 상태 |
|---|---|---|
| FR-A1 Resources | MCP ResourcesProvider → KnowledgeReadService | ✅ |
| FR-A2 Query | MCP ToolsProvider → QueryService → QueryEngine | ✅ |
| FR-A3 Snippet | MCP ToolsProvider → SnippetService → ChunkingService | ✅ |
| FR-A4 Update | MCP ToolsProvider → UpdateService (별도 네임스페이스) | ✅ |
| FR-A5 Prompts | MCP PromptsProvider | ✅ |
| FR-A6 stdio | MCP StdioTransport | ✅ |
| FR-H1~H4 뷰 | Web Viewer → KnowledgeReadService | ✅ |
| FR-H5 SSR | Web Viewer(SSR) | ✅ |
| FR-E1 Ingestion | SyncService + FileSystemSource | ✅ |
| FR-E2 Graph | SyncService + ParserRegistry + GraphBuilder | ✅ |
| FR-E3 구조 추출 | StructuredExtractor(LLM 미호출) | ✅ |
| FR-E4 Persistence | FileSystemKnowledgeStore | ✅ |
| FR-E5 Re-sync | SyncService(resync) + MCP sync_tool | ✅ |
| FR-C1 엔진 우선 | SyncService 재생성 + 에이전트 노트 보존 정책 | ✅ |
| NFR-P1 지연 | KnowledgeReadService 계측 훅 | ✅(설계) |
| NFR-P2 토큰 | ChunkingService | ✅ |
| NFR-C2 파서 확장 | ParserRegistry + LanguageParserPort | ✅ |
| NFR-C3 로컬/결정성 | 순수 도메인 + 어댑터 격리 | ✅ |
| NFR-D1 Git 친화 | 결정적 Markdown+JSON 직렬화 | ✅ |
| NFR-E1 로컬 환경 | FileSystemSource/Store, stdio | ✅ |
| US-N6 PBT 대상 | Domain Models 직렬화 + 순수 함수 | ✅(분리) |
| US-N7 자원 인지 | SyncReport | ✅ |

**미커버 없음**. 임베딩 검색(US-F1) 등 Backlog는 범위 밖(MVP 제외).

---

## 6. 다음 단계로의 인계 (Handoff to Functional Design)

Functional Design(per-unit)에서 구체화할 항목:
- 도메인 모델의 정확한 JSON 스키마 및 파일 저장 레이아웃(엔진/에이전트 네임스페이스 경로)
- MCP Resource **URI 스킴** 및 Tool 입출력 스키마(특히 Update Tool 페이로드)
- 결정적 구조 추출 대상 범위 상세, 청킹/검색 알고리즘
- 에이전트 노트 보존/정리(대상 소스 제거 시) 정책 상세
- 파서 인터페이스의 정확한 계약 및 tree-sitter 통합 세부

Units Generation에서는 위 컴포넌트를 작업 단위(예: Engine Core / MCP Server / Web Viewer / 교차관심사)로 분해한다.

---

## 7. 확장(Extension) 컴플라이언스 요약

| Extension | 상태 | 본 단계 적용 판정 |
|---|---|---|
| Security Baseline | Disabled(Opt-out) | N/A — 미적용 확장 |
| Resiliency Baseline | Disabled(Opt-out) | N/A — 미적용 확장 |
| Property-Based Testing (Partial) | Enabled(Partial) | **적용** — 설계가 순수 도메인 로직/직렬화 모델을 어댑터·I/O와 분리하여 PBT-02(round-trip)/PBT-03(invariant) 대상을 명확히 격리(US-N6). PBT-07/08/09(생성기/재현성/프레임워크)는 Code Generation/NFR 단계에서 강제. 본 설계 단계에서 차단 위반 없음. |

> Security/Resiliency는 Requirements Analysis에서 Opt-out 확정(aidlc-state.md) → 본 단계 N/A(비차단).
