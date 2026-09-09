# U4 Code Structure & Relationships — Tech Stack Decisions

| Concern | Choice | Justification |
|---|---|---|
| Symbol/call/import extraction | stdlib `re` (deterministic regexes) | Guaranteed, offline, LLM-free path (NFR-3.1). |
| Robust multi-language parsing | `tree-sitter-language-pack` (optional) | Used when installed; regex fallback keeps install minimal (NFR-4). |
| Cross-file resolution | in-memory `defined` name→id map | No DB round-trips during analysis; deterministic. |
| Embedding-similarity relationships | local `SearchEngine` + `EmbeddingProvider` (U2) | No external embedding API — vectors computed locally (NFR-3.1, US-3.1). |
| Markdown link parsing | stdlib `re` (`[[wikilink]]`, `[..](..)`) | Deterministic, dependency-free (FR-3.2). |
| Data contracts | shared dataclasses (`types/results.py`) | Typed results with `resolved`/`status` flags (App Design Q7). |
| Property-based tests | **Hypothesis** (PBT-09) | Determinism verification; shared generators in `tests/generators.py`. |

## Offline / fallback rationale

- The analyzer's default path is **pure stdlib regex**, so code-graph extraction
  runs with no third-party dependency and no network (NFR-3.1, NFR-4). This
  mirrors U3's optional-parser degradation pattern.
- tree-sitter, when present, only *improves* parsing robustness; its absence
  never blocks analysis. The embedding strategy's similarity comes exclusively
  from the local embedding stack, never an external API.
