# Component Methods — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Application Design
**Convention (Q7)**: methods return **typed result objects / dataclasses**; expected non-fatal outcomes (`unsupported`, `unresolved`, `broken_link`, `no_match`) are **status fields** on the result, not exceptions. Exceptions are reserved for truly unexpected failures.

> Signatures are high-level Python-style contracts. **Business rules are defined later in per-unit Functional Design** — here we fix names, purposes, and input/output types.

---

## Shared result / data types (illustrative)

```
@dataclass Chunk: id: str; doc_id: str; kind: str; text: str; position: Span; meta: dict; version: int
@dataclass ExtractionResult: status: Literal["ok","unsupported"]; source: str; blocks: list[Block]; tables: list[Table]; message: str|None
@dataclass GraphResult: nodes: list[Node]; edges: list[Edge]; unresolved: list[SymbolRef]
@dataclass Relationship: src_id: str; dst_id: str; kind: str; strategy: str; score: float|None; status: Literal["ok","unresolved"]
@dataclass MatchResult: matched: bool; old_chunk_id: str|None; similarity: float; method: str
@dataclass VersionResult: chunk_id: str; new_version: int; previous_version: int|None
@dataclass SearchHit: id: str; kind: str; score: float; snippet: str|None
@dataclass SnippetResult: text: str; token_count: int; truncated: bool; scope: str
@dataclass ExportResult: files: list[str]; export_dir: str
@dataclass ToolResult: ok: bool; data: Any; status: str; message: str|None   # MCP-facing envelope
```

---

## C1. McpServer (thin adapter)
| Method | Purpose | Input → Output |
|---|---|---|
| `register_resources()` | Register Structure/Summary/Relationship resource URIs with descriptions | () → None |
| `register_tools()` | Register self-describing tools (name, description, input schema, usage timing) | () → None |
| `handle_tool(name, args)` | Validate input, delegate to a Service, serialize typed result to token-efficient `ToolResult` | (str, dict) → ToolResult |
| `read_resource(uri)` | Resolve a resource URI via QueryService | (str) → ToolResult |

## C3. Installer → InstallService (see services.md)
| Method | Purpose | Input → Output |
|---|---|---|
| `run(target_dir, options)` | Orchestrate copy + store init + client config | (Path, dict) → InstallReport |

---

## C4. ExtractorRegistry + Extractor
| Method | Purpose | Input → Output |
|---|---|---|
| `ExtractorRegistry.resolve(file_path)` | Select extractor by format/language | (Path) → Extractor \| None |
| `ExtractorRegistry.register(key, extractor)` | Add a pluggable extractor | (str, Extractor) → None |
| `Extractor.extract(file_path)` | Extract text/tables/structure; `status="unsupported"` if not handled | (Path) → ExtractionResult |
| `CodeExtractor.extract(file_path)` | tree-sitter parse → code units for structure analysis | (Path) → ExtractionResult |

## C5. Chunker
| Method | Purpose | Input → Output |
|---|---|---|
| `chunk(extraction)` | Split into semantic-unit chunks with ids + source metadata | (ExtractionResult) → list[Chunk] |
| `serialize(chunks)` | Deterministic serialization (PBT round-trip) | (list[Chunk]) → bytes |
| `deserialize(blob)` | Inverse of serialize (round-trip invariant) | (bytes) → list[Chunk] |

## C6. CodeStructureAnalyzer
| Method | Purpose | Input → Output |
|---|---|---|
| `analyze(code_units)` | Extract nodes/edges (define/call/depend/inherit) | (list[CodeUnit]) → GraphResult |
| `resolve_symbols(graph)` | Cross-file symbol resolution; unresolved flagged, not fatal | (GraphResult) → GraphResult |

## C7. RelationshipBuilder + RelationStrategy
| Method | Purpose | Input → Output |
|---|---|---|
| `build(items)` | Run all enabled strategies, merge relationships | (Items) → list[Relationship] |
| `RelationStrategy.relate(items)` | One strategy's relationships | (Items) → list[Relationship] |
| `MarkdownLinkStrategy.relate(...)` | Parse `[[wikilink]]`/links; broken → `status="unresolved"` | (Items) → list[Relationship] |

## C8. ChunkVersioner
| Method | Purpose | Input → Output |
|---|---|---|
| `signature(chunk)` | Deterministic hash/MinHash signature (PBT determinism) | (Chunk) → Signature |
| `match(new_chunk, candidates)` | Find corresponding OLD chunk by similarity/hash | (Chunk, list[Chunk]) → MatchResult |
| `apply_version(match, new_chunk)` | Update OLD→NEW version (history preserved) or create v1 | (MatchResult, Chunk) → VersionResult |

## C9. SearchEngine
| Method | Purpose | Input → Output |
|---|---|---|
| `search(intent, limit)` | Intent-based semantic search (embed + sqlite-vec rank) | (str, int) → list[SearchHit] |
| `index(item_id, vector)` | Store embedding for an item | (str, Vector) → None |

## C10. SnippetBuilder + TokenEstimator
| Method | Purpose | Input → Output |
|---|---|---|
| `build(target_id, token_budget)` | Cut minimal relevant scope within budget, preserve boundaries | (str, int) → SnippetResult |
| `TokenEstimator.count(text)` | Estimate token count | (str) → int |

## C11. EmbeddingProvider
| Method | Purpose | Input → Output |
|---|---|---|
| `embed(texts)` | Local/offline embedding (no network) | (list[str]) → list[Vector] |
| `dimension` | Vector dimension (for sqlite-vec schema) | → int |

## C12. SummaryStore
| Method | Purpose | Input → Output |
|---|---|---|
| `extract_for_summary(id)` | Return content the Agent should summarize (no LLM call) | (str) → Content |
| `save_summary(chunk_id, text)` | Persist Agent-authored summary (→ SummaryRepository) | (str, str) → None |
| `get_summary(chunk_id)` | Retrieve stored summary | (str) → str \| None |

## C13. WikiExporter
| Method | Purpose | Input → Output |
|---|---|---|
| `export(export_dir)` | Write static JSON/HTML artifacts for the viewer | (Path) → ExportResult |

## C14. KnowledgeStore
| Method | Purpose | Input → Output |
|---|---|---|
| `connect()` | Open SQLite + load sqlite-vec extension | () → Connection |
| `init_schema()` | Create tables/indexes in `.knowledge-store/` | () → None |
| `reindex()` | Support re-indexing after large refactors (NFR-2.1) | () → None |

## C15. Repositories (all SQL isolated here)
| Repository | Key methods (purpose) |
|---|---|
| `ChunkRepository` | `upsert(chunk)`, `get(id)`, `list_versions(chunk_id)`, `by_document(doc_id)` |
| `GraphRepository` | `save_nodes(nodes)`, `save_edges(edges)`, `neighbors(node_id)`, `tree(root)` |
| `RelationshipRepository` | `save(relationships)`, `for_item(id)`, `unresolved()` |
| `EmbeddingRepository` | `upsert(id, vector)`, `knn(vector, k)` (sqlite-vec) |
| `SummaryRepository` | `save(chunk_id, text)`, `get(chunk_id)` |

---

## Notes
- All expected edge cases from the acceptance criteria (unsupported format US-1.1, unresolved symbol US-2.2, broken link US-3.2, no-match new chunk US-4.2, tiny token budget US-6.3) surface as **status fields on typed results** (Q7), never silent failures or uncaught exceptions.
- MCP-facing methods return the token-efficient `ToolResult` envelope (NFR-1.2); internal component methods return their domain result types.
