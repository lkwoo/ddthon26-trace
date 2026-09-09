# U3 Ingestion & Chunking — Tech Stack Decisions

| Concern | Choice | Justification |
|---|---|---|
| csv parsing | stdlib `csv` + `io` | Zero dependency; always available (NFR-4). |
| Markdown / text | stdlib `re` blank-line splitting | Deterministic, no heavy parser needed (NFR-3/4). |
| PDF | `pypdf` (optional, extra `docs`) | Heavy; import guarded, absence → `Status.ERROR` (NFR-4). |
| xlsx | `openpyxl` (optional, extra `docs`) | Same optional-degradation pattern as PDF. |
| Code language detection | extension → language map | Deterministic; detailed parsing deferred to U4 (tree-sitter optional w/ regex fallback). |
| Chunk identity | `hashlib.sha256` (16 hex) over stable parts | Reproducible ids without external state. |
| Chunk serialization | stdlib `json` with `sort_keys=True` | Byte-stable, round-trip invariant (PBT-02, NFR-8.2). |
| Similarity signature | `hashlib.blake2b` MinHash (64 perms, 5-char shingles, Mersenne mod) | Fast, deterministic, no ML/network — matches NFR-3.1 LLM-free. |
| Property-based tests | **Hypothesis** | PBT-09 framework selection for Python; drives PBT-02/03/07/08. |

## Offline / fallback rationale

- All core paths (markdown, csv, chunking, versioning) run with **stdlib only**,
  so ingestion never requires network or an LLM (NFR-3.1).
- Optional parsers are imported lazily inside `extract()`; a missing library is a
  typed `Status.ERROR`, keeping the install minimal and the pipeline resilient
  (NFR-4). This mirrors U4's tree-sitter-optional / regex-fallback strategy.
