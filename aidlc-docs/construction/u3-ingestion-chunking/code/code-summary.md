# U3 Ingestion & Chunking — Code Summary

**Status**: Code generation complete. All source and tests implemented and green.

## Files

| File | Description |
|---|---|
| `knowledge_store/ingestion/__init__.py` | Public exports for U3 (registry, extractors, `Chunker`, `ChunkVersioner`). |
| `knowledge_store/ingestion/extractors.py` | `Extractor` Protocol, `ExtractorRegistry`, four extractors, `default_registry()`. |
| `knowledge_store/ingestion/chunker.py` | `Chunker` — semantic chunking + `serialize`/`deserialize` round-trip. |
| `knowledge_store/ingestion/versioner.py` | `ChunkVersioner`, `minhash_signature`, `estimate_jaccard`. |
| `knowledge_store/types/results.py` | Shared typed results: `Chunk`, `ExtractionResult`, `MatchResult`, `VersionResult`, `Status`. |

## Key public API

- `ExtractorRegistry.resolve(path)`, `ExtractorRegistry.extract(path) -> ExtractionResult`
- `default_registry() -> ExtractorRegistry`
- `Chunker.chunk(ExtractionResult) -> list[Chunk]`
- `Chunker.serialize(chunks) -> bytes` / `Chunker.deserialize(bytes) -> list[Chunk]`
- `ChunkVersioner.match(new_chunk, candidates) -> MatchResult`
- `ChunkVersioner.apply_version(new_chunk, match) -> VersionResult`
- `minhash_signature(text) -> tuple[int, ...]`, `estimate_jaccard(a, b) -> float`

## Tests exercising this unit (all passing)

- `tests/ingestion/test_extractors.py` — markdown text+tags, code language
  detection, csv table, unsupported-format-is-typed (US-1.1).
- `tests/ingestion/test_chunker_pbt.py` — **PBT-02** serialize/deserialize
  round-trip, serialize determinism, chunk-then-round-trip (~200/100/150 examples).
- `tests/ingestion/test_versioner_pbt.py` — **PBT-03** signature determinism,
  self-similarity, identical-chunk matching (~200/200/100 examples).
- `tests/generators.py` — PBT-07 reusable Hypothesis generators (`chunks`,
  `document_text`, `text_fragments`) consumed by the above.

Whole suite = **36 tests green**; PBT properties run 200–300 examples each with
Hypothesis (PBT-08 shrinking/reproducibility, PBT-09 framework).
