# U2 Embedding & Semantic Search — NFR Design Patterns

## Protocol-based provider (pluggability)
`EmbeddingProvider` is a runtime-checkable `typing.Protocol` exposing `dimension`
+ `embed`. Any implementation that matches the shape is usable; `SearchEngine`
depends on the protocol, not a concrete class. This lets the learned and hashing
providers be swapped with no engine change (App Design Q6).

## Optional-dependency capability detection with graceful degradation
`LocalEmbeddingProvider` probes `fastembed` at construction and records
capability via `is_learned` / `_model`. On any import/init failure it silently
delegates to `HashingEmbeddingProvider`. Combined with U1's sqlite-vec detection,
the whole vector path degrades gracefully while staying offline (NFR-3/NFR-4).

## Deterministic hashing (reproducibility)
The fallback embedding is a pure function of its input (md5 feature hashing,
signed buckets, log term weighting, L2 normalization). Determinism makes indexing,
relationship-building, and versioning reproducible and testable (supports NFR-8).

## Singleton default provider
`get_default_provider()` memoizes a single process-wide provider (`_DEFAULT`) so
indexing and querying share the same embedding space and the (potentially heavy)
model loads at most once — bounding latency and memory.

## Delegated ranking + storage abstraction
`SearchEngine` delegates persistence and ranking to U1's `EmbeddingRepository`,
so the vec/cosine strategy and score normalization stay behind the repository
boundary. The engine focuses on embed -> search -> preview enrichment.

## Token-efficient result shaping
`search` enriches hits with a bounded (<=160-char) preview rather than full text,
directly serving NFR-1.2 token efficiency at the design level.
