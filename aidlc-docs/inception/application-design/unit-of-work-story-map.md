# Unit of Work → Story Map — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Units Generation (Part 2)
**Purpose**: map all **28 stories** (9 Epics) to the **8 units**. Every story has a primary owning unit; cross-cutting stories list contributing units.

---

## Story → Unit matrix

| Story | Requirement | Primary Unit | Contributing Unit(s) |
|---|---|---|---|
| US-1.1 Multi-format ingestion | FR-1.1, FR-1.4 | **U3** Ingestion & Chunking | U6 (Ingestion tool) |
| US-1.2 PDF tables / spreadsheet | FR-1.2 | **U3** | — |
| US-1.3 Semantic chunking (PBT) | FR-1.3, NFR-8.2 | **U3** | — |
| US-2.1 tree-sitter code relations | FR-2.1 | **U4** Code Structure & Relationships | U3 (Code extractor) |
| US-2.2 Symbol resolution / graph | FR-2.2 | **U4** | U1 (GraphRepository) |
| US-3.1 Embedding similarity link | FR-3.1, NFR-3.1 | **U4** (RelationshipBuilder) | U2 (EmbeddingProvider/SearchEngine), U1 |
| US-3.2 Markdown link parsing | FR-3.2 | **U4** | — |
| US-3.3 Tag matching | FR-3.3 | **U4** | — |
| US-4.1 Chunk match (hash/similarity, PBT) | FR-4.1/4.2, NFR-2.2/8.2 | **U3** ChunkVersioner | — |
| US-4.2 Chunk new version update | FR-4.3 | **U3** | U1 (ChunkRepository history) |
| US-5.1 Extract content to summarize | FR-5.2, NFR-3.1 | **U5** Retrieval & Summarization | U6 (Summarize tool) |
| US-5.2 Store / get summary | FR-5.1 | **U5** | U1 (SummaryRepository) |
| US-6.1 MCP Resources | FR-6.1 | **U6** Service Orchestration & MCP | U1 (repos) |
| US-6.2 Semantic Query tool | FR-6.2, NFR-1.2 | **U6** (QueryService) | U2 (SearchEngine) |
| US-6.3 Smart Snippet tool | FR-6.2, NFR-1.2 | **U6** (QueryService) | U5 (SnippetBuilder/TokenEstimator) |
| US-6.4 Ingestion/Update tools | FR-6.2, FR-5.1 | **U6** (IngestionService) | U3, U4, U5, U7 |
| US-7.1 Interactive tree view | FR-7.1 | **U7** Wiki Export & Viewer | — |
| US-7.2 Dependency graph view | FR-7.2 | **U7** | — |
| US-7.3 Wiki content viewer | FR-7.3 | **U7** | — |
| US-7.4 Review auto-updated wiki | FR-7.4, NFR-2.1 | **U7** | U6 (WikiExportService trigger) |
| US-8.1 Copy-style install script | FR-8.1, NFR-4.1 | **U8** Installer & Packaging | — |
| US-8.2 `.knowledge-store/` isolation | FR-8.2 | **U8** | U1 (init_schema) |
| US-8.3 MCP client auto-config | FR-8.3, NFR-5.1 | **U8** | U6 (server entry point) |
| US-8.4 Agent-readable README | FR-8.4, NFR-4.2, NFR-2.1 | **U8** | — |
| US-9.1 Agent discoverability | NFR-5.1, FR-6.3 | **U6** (self-describing tools) | — |
| US-9.2 Low-latency core queries | NFR-1.1 | **U6** (QueryService) | U1, U2, U5 |
| US-9.3 Token-efficient results | NFR-1.2 | **U5** (SnippetBuilder) | U6 (ToolResult serialization) |
| US-9.4 Simple install / minimal prereqs | NFR-4.1, NFR-4.2 | **U8** | — |

---

## Coverage check

| Unit | Primary stories | Count |
|---|---|---|
| U1 Storage Foundation | (foundation — supports US-2.2, US-4.2, US-5.2, US-6.1, US-8.2 persistence) | 0 primary / 5 contributing |
| U2 Embedding & Search | (supports US-3.1, US-6.2, US-9.2) | 0 primary / 3 contributing |
| U3 Ingestion & Chunking | US-1.1, US-1.2, US-1.3, US-4.1, US-4.2 | 5 |
| U4 Code Structure & Relationships | US-2.1, US-2.2, US-3.1, US-3.2, US-3.3 | 5 |
| U5 Retrieval & Summarization | US-5.1, US-5.2, US-9.3 | 3 |
| U6 Service Orchestration & MCP | US-6.1, US-6.2, US-6.3, US-6.4, US-9.1, US-9.2 | 6 |
| U7 Wiki Export & Viewer | US-7.1, US-7.2, US-7.3, US-7.4 | 4 |
| U8 Installer & Packaging | US-8.1, US-8.2, US-8.3, US-8.4, US-9.4 | 5 |

**Total primary assignments**: 5+5+3+6+4+5 = **28 stories** — full coverage, no gaps, no duplicates.

**Note on U1/U2**: These are pure infrastructure/foundation units with no user-facing story of their own; they exist to satisfy the persistence and vector-search needs of the stories above (repository-mediated access per App Design Q4/Q6). They are validated indirectly through the stories that depend on them and directly through unit tests (incl. PBT for U1 schema round-trips where applicable).
