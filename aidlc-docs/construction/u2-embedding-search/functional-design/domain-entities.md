# U2 Embedding & Semantic Search — Domain Entities

U2 owns no tables; it produces vectors persisted via U1's `EmbeddingRepository`
(`embeddings_vec` / `embeddings`). It defines/uses the following types.

## Provider types (`knowledge_store/embedding/provider.py`)

### EmbeddingProvider (Protocol, runtime-checkable)
- `dimension: int` (property)
- `embed(texts: list[str]) -> list[list[float]]`
- Contract only; both concrete providers structurally satisfy it.

### HashingEmbeddingProvider
- Fields: `_dim` (default 256).
- Deterministic feature-hashing embedding; `_embed_one`, `embed`.

### LocalEmbeddingProvider
- Fields: `_fallback` (HashingEmbeddingProvider), `_model` (fastembed
  `TextEmbedding` or None), `_dim` (probed or 256).
- `is_learned` -> True when the model loaded.
- Module singleton: `_DEFAULT`, accessed via `get_default_provider()`.

## Search types (`knowledge_store/embedding/search.py`)

### SearchEngine
- Fields: `_repos` (U1 `Repositories`), `_provider` (`EmbeddingProvider`).
- Ops: `index`, `index_many`, `search`.

### SearchHit (from `knowledge_store/types/results.py`)
- `ref_id: str`, `kind: str` (chunk|symbol), `score: float`, `preview: str=""`.
- The ranked result element returned by `search`.

## Vector representation
- A vector is a `list[float]` (Python list). Fixed length per provider.
- Persistence (packing to float32 BLOB / vec0) is U1's concern; U2 hands raw
  float lists to `EmbeddingRepository.upsert`/`search`.

## Testable Properties (PBT-01)

| Property | Category | Target | Status under PBT Partial |
|---|---|---|---|
| Determinism: `embed([t]) == embed([t])` for any text `t` | Invariant | `HashingEmbeddingProvider` | Enforced-eligible (PBT-03) — pure, deterministic function |
| Fixed dimension: every returned vector has length == `dimension` | Invariant / Range | `HashingEmbeddingProvider.embed` | Enforced-eligible (PBT-03) |
| L2-normalization: `norm(embed([t])[0]) approx 1.0` for non-empty `t` | Invariant | `_embed_one` | Enforced-eligible (PBT-03) |
| Empty input -> empty output: `embed([]) == []` | Invariant | provider `embed` | Enforced-eligible (PBT-03) |
| Empty intent -> `search` returns `[]` | Invariant | `SearchEngine.search` | Advisory (touches DB/repos) |
| Self-similarity ranks a chunk first for its own text | Oracle | `SearchEngine.search` | Advisory (PBT-05 not in Partial set) |

Under PBT Partial (PBT-02/03/07/08/09), the pure-function invariants of the
hashing provider (determinism, fixed dimension, normalization, empty-input) are
the blocking-eligible candidates and use Hypothesis-generated text with
domain-appropriate generators (PBT-07). Search-level and oracle properties that
require the store are advisory and are pinned by example-based pipeline tests.
