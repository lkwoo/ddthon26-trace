# U3 Ingestion & Chunking — Business Rules

Rules enforced by the code in `knowledge_store/ingestion/` and
`knowledge_store/types/results.py`. Each cites the requirement/story it satisfies.

## Extraction (C4)

- **BR-U3-1** Resolution is first-match by `supports(path)` in registration order;
  `default_registry()` order is Markdown → Code → Spreadsheet → PDF (FR-1.1).
- **BR-U3-2** An unresolved file returns `ExtractionResult(status=UNSUPPORTED)`
  with a message — never an exception (US-1.1, App Design Q7).
- **BR-U3-3** Optional parsers degrade gracefully: missing `pypdf`/`openpyxl`
  yields `Status.ERROR` with an install hint, not a crash (FR-1.2, NFR-4).
- **BR-U3-4** Inline `#tags` are extracted deterministically as a sorted, de-duped
  tuple (`_find_tags`); code files record their detected `language` (FR-2.1 feed).
- **BR-U3-5** csv/xlsx cell data is preserved as `tables` (rows of cells),
  structure intact (FR-1.2, US-1.2).

## Chunking (C5)

- **BR-U3-6** Chunking is deterministic: same `ExtractionResult` → identical
  chunk list, including ids (FR-1.3, US-1.3, US-2.1 determinism spirit).
- **BR-U3-7** Boundaries are semantic — markdown blank-line blocks (heading →
  `section`, else `paragraph`), code blank-line blocks (`code`), one chunk per
  table (`table`) (FR-1.3).
- **BR-U3-8** Each `Chunk.id` is a stable sha256 over `(source_path, ordinal,
  kind, text)`; source path, ordinal and tags are retained as metadata (US-1.3).
- **BR-U3-9** A non-OK extraction produces an empty chunk list (guarded by
  `extraction.ok`).
- **BR-U3-10 (round-trip invariant)** `deserialize(serialize(chunks)) == chunks`
  for any valid chunk list; serialization uses `sort_keys=True` so it is also
  byte-stable (NFR-8.2, US-1.3 "직렬화 왕복 불변", PBT-02).

## Versioning (C8)

- **BR-U3-11** `minhash_signature` is deterministic — identical content always
  yields the identical signature; empty content degenerates to a zero vector
  (US-4.1 determinism, PBT-03).
- **BR-U3-12** Matching picks the highest Jaccard estimate; a match is accepted
  only when `similarity >= threshold` (default 0.6), else `Status.NOT_FOUND`
  (FR-4.2, NFR-2.2).
- **BR-U3-13** On match, the incoming content is **re-keyed onto the matched
  chunk id** and stored at `latest_version + 1`, preserving history
  (`is_new=False`) (FR-4.3, US-4.2).
- **BR-U3-14** No match → the chunk is stored as version 1 with its own id
  (`is_new=True`) (US-4.2 edge case).
- **BR-U3-15** Identical text between two chunks matches with `similarity == 1.0`
  (self-similarity of a signature is 1.0 when non-empty) (US-4.1, PBT-03).
