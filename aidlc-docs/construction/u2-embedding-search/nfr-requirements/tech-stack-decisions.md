# U2 Embedding & Semantic Search — Tech Stack Decisions

## Embedding model: optional fastembed, deterministic hashing default
- **Decision**: `LocalEmbeddingProvider` uses `fastembed` (`TextEmbedding`,
  default `BAAI/bge-small-en-v1.5`) when installed; otherwise
  `HashingEmbeddingProvider` (feature-hashing) is the default.
- **Why**: fastembed gives a small, offline, learned embedding without an LLM
  API (Q CQ1); the hashing fallback guarantees the system works with zero model
  downloads — supporting NFR-3 (offline) and NFR-4 (dependency-light).
- **Dependency**: `fastembed>=0.3.0` declared as optional extra `[embeddings]`;
  core `dependencies = []`.

## Vector storage: delegated to U1 (SQLite + optional sqlite-vec, float32)
- U2 emits `list[float]` vectors; U1's `EmbeddingRepository` packs them to
  little-endian float32 and stores/searches via sqlite-vec `vec0` or a
  brute-force cosine fallback. U2 stays storage-agnostic.

## Provider abstraction: typing.Protocol
- `EmbeddingProvider` is a `@runtime_checkable` `Protocol`, enabling structural
  (duck-typed) pluggability without a base class — new providers just implement
  `dimension` + `embed`.

## Fallback strategy and rationale
- Two independent fallbacks combine: (a) provider-level (fastembed -> hashing)
  and (b) storage-level (sqlite-vec -> cosine, in U1). Each degrades silently on
  ImportError/load failure. Rationale: offline install and no external
  dependency are hard requirements (NFR-3/NFR-4); correctness is preserved on
  every path, only quality/speed vary.

## Test stack: pytest + Hypothesis (PBT-09)
- **Hypothesis** is the selected PBT framework for Python — custom text
  strategies/generators (PBT-07), automatic shrinking + seed reproducibility
  (PBT-08), pytest integration. Declared in the `[test]` extra
  (`pytest>=8.0`, `hypothesis>=6.100`). The hashing provider's pure invariants
  are the PBT-eligible targets.
