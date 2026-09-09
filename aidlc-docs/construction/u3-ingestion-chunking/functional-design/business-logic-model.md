# U3 Ingestion & Chunking — Business Logic Model

**Unit**: `u3-ingestion-chunking` · **Package**: `knowledge_store/ingestion/`
**Components**: C4 ExtractorRegistry (+Extractors), C5 Chunker, C8 ChunkVersioner
**Stage**: CONSTRUCTION → Functional Design

## Responsibilities

1. **Resolve file → extractor** and produce a typed `ExtractionResult`; unsupported
   formats return `Status.UNSUPPORTED` instead of raising (US-1.1, FR-1.1).
2. **Chunk** extracted content into deterministic semantic units (section /
   paragraph / table / code) with stable identity and source metadata (FR-1.3,
   US-1.3), and provide a `serialize`/`deserialize` round-trip (NFR-8.2).
3. **Version** chunks by MinHash text-similarity matching — matched chunks are
   re-keyed onto the existing chunk id and bumped a version, unmatched become v1
   (FR-4, US-4.1/4.2).

## Key operations (real class/method names)

- `ExtractorRegistry.resolve(path) -> Extractor | None` — first extractor whose
  `supports(path)` is true (order = priority in `default_registry()`).
- `ExtractorRegistry.extract(path) -> ExtractionResult` — resolve then extract;
  `None` → `Status.UNSUPPORTED` result.
- `Chunker.chunk(ExtractionResult) -> list[Chunk]` — dispatches to
  `_chunk_tables` / `_chunk_code` / `_chunk_text` by result shape.
- `Chunker.serialize(chunks) -> bytes` / `Chunker.deserialize(bytes) -> list[Chunk]`
  — JSON with `sort_keys=True` (deterministic, round-trip invariant).
- `ChunkVersioner.match(new_chunk, candidates) -> MatchResult` — best Jaccard
  estimate over `minhash_signature`; `>= threshold` (default 0.6) → OK.
- `ChunkVersioner.apply_version(new_chunk, match) -> VersionResult` — matched:
  re-key onto `matched_chunk_id`, `latest_version + 1`; else new v1.
- `minhash_signature(text) -> tuple[int, ...]` — deterministic blake2b MinHash
  over 5-char shingles (identical text → identical signature).

## Operation flow (ingestion pipeline slice)

```
file path
   |
   v
ExtractorRegistry.resolve --miss--> ExtractionResult(UNSUPPORTED)
   | hit
   v
Extractor.extract -> ExtractionResult(OK | ERROR)
   |
   v
Chunker.chunk -> list[Chunk]  --serialize/deserialize--> identical list (PBT-02)
   |
   v
ChunkVersioner.match(new, candidates) -> MatchResult
   |                    |
 matched (>=thr)     unmatched
   v                    v
apply_version:        apply_version:
 re-key onto id,       new id, version 1
 latest+1 (is_new=F)   (is_new=T)
```

Extraction and chunking are pure functions of their inputs; only
`apply_version` touches persistence (via `ChunkRepository`).
