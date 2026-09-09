# Change Note — Content-derived tag enrichment for substantive relationships

**Increment**: 3 (U-Tags) · **Units touched**: u3-ingestion-chunking, u4-codegraph-relationships
**Branch**: shortFix1 · **Depth**: standard brownfield feature (auto-adopt)
**User request**: "tag로 벡터값 외에도 실질적으로 연관되어 있는 내용들을 추가했으면 좋겠어."
**Scope confirmed (AskUserQuestion)**: derive tags from **code symbols + keywords/keyphrases + path/language/kind + wikilink targets** (all four facets).

## Problem

A chunk's `tags` previously held **only the literal `#hashtags`** a human wrote in the
source (`extractors._find_tags`). Consequently `TagMatchStrategy` had almost nothing to
connect, and "real relatedness" between chunks fell entirely on
`EmbeddingSimilarityStrategy` (vector similarity). The user wanted the tag channel to
carry substantive, content-derived relationships that **complement** vector similarity.

## Change 1 — `TagEnricher` (new: `src/knowledge_store/ingestion/tagging.py`)

Deterministic, LLM-free derivation of **namespaced** tag facets from each chunk's own
content. Namespacing keeps auto-derived tags from colliding with human `#hashtags` and
lets consumers (search, wiki UI) filter by facet:

| Namespace | Meaning | Source |
|-----------|---------|--------|
| *(none)*  | human `#hashtag` (unchanged, preserved) | extractor |
| `kind:`   | chunk kind (code/section/paragraph/table) | chunk |
| `lang:`   | programming language | chunk metadata |
| `mod:`    | source file stem (module) | path |
| `dir:`    | immediate parent directory | path |
| `sym:`    | a symbol the chunk **defines or references** (call sites) | code text |
| `kw:`     | top-6 salient keywords (stopword-filtered, incl. code keywords) | text |
| `link:`   | `[[wikilink]]` / markdown-link target | text |

Keyword tokenisation reuses the U-Hybrid code-aware `tokenize()` so tag terms line up
with BM25 search terms. Wired as a post-pass in `Chunker.chunk()` via
`dataclasses.replace(chunk, tags=enricher.enrich(chunk))`.

**Invariant preserved**: chunk `id` derives from path/ordinal/kind/**text** — never tags —
so enrichment leaves ids untouched; versioning and the PBT-02 serialize round-trip are
unaffected (verified: `test_chunker_pbt.py` still green; new determinism/identity test).

## Change 2 — `TagMatchStrategy` rewrite (`codegraph/relationships.py`)

A naïve "share any tag → link" would flood O(n²) non-substantive edges (every
`lang:python` / `kind:code` chunk linked to every other). Instead each shared tag
contributes a score that is:

- **namespace-weighted** — `sym`/`link`/hashtag = 1.0 (strong), `mod` = 0.7, `kw` = 0.6,
  `dir` = 0.35, and `lang`/`kind` = **0.0** (facet-only: kept on the chunk for
  search/filtering, but never wired as a pairwise edge);
- **selectivity-weighted** — inverse document frequency `1/(df-1)`: a tag shared by
  exactly 2 chunks weighs 1.0, one shared by many decays toward 0.

Per-pair scores accumulate across shared tags; groups with `df > 60` are skipped (too
broad to be substantive, and avoids the O(df²) expansion); only pairs clearing
`min_score = 0.1` are emitted, in **both directions** so `read_relationships` surfaces the
link from either endpoint.

### Behaviour example (module `app.py`: `Service.run` calls `helper`; `helper` calls `compute_total`)

- `Service.run` ↔ `helper` and `helper` ↔ `compute_total` → **score 1.0** (shared rare `sym:` — a caller↔definition link).
- Chunks sharing only `mod:app` + `dir:src` (no symbols) → weak **0.35** ("same module").
- `lang:python` / `kind:code` shared by all → **no edge**.

## Tests

- `tests/ingestion/test_tagging.py` (4): symbol/keyword/path/language facets; hashtag
  preservation + link targets (through the real `MarkdownExtractor`); determinism +
  id-preservation; `<module>` gap chunks.
- `tests/codegraph/test_tag_relationships.py` (4): symbol beats broad facet; rarer tag
  scores higher; low-selectivity pairs dropped below threshold; edges TAG-typed and
  bidirectional.

**Result**: new tests 8/8 pass; full non-eval suite **46 pass**. Search-quality eval is
**unaffected by construction** — enrichment changes `tags` only, never chunk `text` or
`id`, and search indexes `text` — so `semantic_query` recall/MRR are unchanged.

`TagMatchStrategy.build` cost: ~0.04 s over 407 real repo chunks (not a bottleneck; the
pre-existing per-chunk `EmbeddingSimilarityStrategy.search` dominates ingestion time).

## Env note

The local `.venv` had lost `pip`, `pytest`, and `hypothesis`, and the package was a stale
**non-editable** install (so `src/` edits were not picked up). Restored `pip` via
`get-pip.py`, reinstalled `pytest`/`hypothesis`, and `pip install -e .` so the venv now
tracks `src/` live. Run tests with `.venv/bin/python -m pytest`.
