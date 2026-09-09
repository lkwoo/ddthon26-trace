# U3 Ingestion & Chunking — Domain Entities

Defined in `knowledge_store/types/results.py` (shared typed results, App Design Q7).

## Entities / structures

- **`Chunk`** (frozen dataclass) — a semantic-unit chunk.
  - Fields: `id`, `text`, `source_path`, `ordinal`, `kind`
    (`section|paragraph|table|code`), `tags: tuple[str,...]`, `metadata: dict`.
  - `Chunk.make(...)` derives `id` deterministically via `_stable_id` (sha256 of
    `source_path, ordinal, kind, text`, 16 hex chars).
  - `to_dict()` / `from_dict()` provide the JSON envelope used for serialization
    (tags list ↔ tuple normalization).
- **`ExtractionResult`** — extractor output.
  - Fields: `status`, `source_path`, `format`, `text`, `tables`, `tags`,
    `is_code`, `language`, `message`; `.ok` property == `status is OK`.
- **`MatchResult`** — outcome of `ChunkVersioner.match`.
  - Fields: `status` (OK matched / NOT_FOUND new), `matched_chunk_id`,
    `similarity`.
- **`VersionResult`** — outcome of `apply_version`.
  - Fields: `chunk_id`, `version`, `is_new`.
- **`ChunkVersion`** — versioned row (`chunk_id`, `version`, `text`, `is_latest`).
- **`Status`** enum — `OK`, `UNSUPPORTED`, `UNRESOLVED`, `NOT_FOUND`, `SKIPPED`,
  `ERROR`.

## Entity sketch

```
ExtractionResult --Chunker.chunk--> [ Chunk ]
                                       | (id, text, source_path, ordinal, kind, tags, metadata)
                                       v
                        ChunkVersioner.match -> MatchResult -> apply_version -> VersionResult
```

## Testable Properties (PBT-01)

| ID | Property | Status |
|---|---|---|
| P-U3-1 | `deserialize(serialize(chunks)) == chunks` for any valid chunk list | **Enforced (PBT-02)** — `test_serialize_deserialize_round_trip`, `test_chunk_then_round_trip` |
| P-U3-2 | `serialize` is deterministic (equal bytes for equal input) | **Enforced (PBT-02/03)** — `test_serialize_is_deterministic` |
| P-U3-3 | `minhash_signature(t) == minhash_signature(t)` (determinism) | **Enforced (PBT-03)** — `test_signature_is_deterministic` |
| P-U3-4 | Non-empty signature is fully self-similar (`estimate_jaccard(sig,sig)==1.0`) | **Enforced (PBT-03)** — `test_signature_self_similarity` |
| P-U3-5 | Identical text → match with `similarity==1.0` and matched id | **Enforced (PBT-03)** — `test_identical_chunks_match` |
| P-U3-6 | `Chunk.id` is a pure function of `(source_path, ordinal, kind, text)` | Advisory (implied by P-U3-1) |
| P-U3-7 | Unsupported format → `Status.UNSUPPORTED`, never raises | Advisory (example test `test_unsupported_format_is_typed_not_raised`) |
