# U3 Ingestion & Chunking — Logical Components

Concrete classes mapped to the components in `components.md`.

| Class (module) | Component | Role (one line) |
|---|---|---|
| `Extractor` (Protocol) — `extractors.py` | C4 | Interface: `supports(path)` + `extract(path) -> ExtractionResult`. |
| `ExtractorRegistry` — `extractors.py` | C4 | Ordered registry; `resolve`/`extract`, unsupported → typed status. |
| `MarkdownExtractor` — `extractors.py` | C4 | `.md/.markdown/.txt/.rst` → text + inline `#tags`. |
| `CodeExtractor` — `extractors.py` | C4 | Source files → raw text + detected language (feeds U4). |
| `SpreadsheetExtractor` — `extractors.py` | C4 | csv (stdlib) + xlsx (openpyxl optional) → tables. |
| `PdfExtractor` — `extractors.py` | C4 | PDF text via pypdf (optional). |
| `default_registry()` — `extractors.py` | C4 | Factory wiring the four built-in extractors in priority order. |
| `Chunker` — `chunker.py` | C5 | Deterministic semantic chunking + serialize/deserialize round-trip. |
| `ChunkVersioner` — `versioner.py` | C8 | MinHash match + version apply (via `ChunkRepository`). |
| `minhash_signature` / `estimate_jaccard` — `versioner.py` | C8 | Deterministic similarity primitives. |
| `Chunk`, `ExtractionResult`, `MatchResult`, `VersionResult` — `types/results.py` | shared (Q7) | Typed contracts crossing unit boundaries. |

**Dependencies**: U1 `ChunkRepository` (persistence for `apply_version`);
`CodeExtractor` output consumed by U4. No peer-unit or upward coupling.
