# U2 Embedding & Semantic Search — Logical Components

Concrete classes/modules realizing the design, mapped to components.md.

| Class / module | File | Maps to | Role (one line) |
|---|---|---|---|
| `EmbeddingProvider` (Protocol) | `embedding/provider.py` | C11 EmbeddingProvider (interface) | Runtime-checkable contract: `dimension` + `embed(texts)`. |
| `HashingEmbeddingProvider` | `embedding/provider.py` | C11 (default concrete) | Deterministic, dependency-free feature-hashing embedding (offline fallback). |
| `LocalEmbeddingProvider` | `embedding/provider.py` | C11 LocalEmbeddingProvider | Wraps offline `fastembed` when installed; delegates to hashing provider otherwise. |
| `get_default_provider()` | `embedding/provider.py` | C11 (factory) | Process-wide singleton provider selection. |
| `SearchEngine` | `embedding/search.py` | C9 SearchEngine | Intent-based semantic search + indexing; embeds and delegates storage/ranking to U1. |
| `_tokenize` / `_TOKEN_RE` | `embedding/provider.py` | C11 (helper) | Lowercase alphanumeric tokenizer feeding the hashing embedding. |
| `SearchHit` | `types/results.py` | shared result type | Ranked search result element (`ref_id`, `kind`, `score`, `preview`). |
| package exports | `embedding/__init__.py` | C9/C11 | Public surface: providers, `get_default_provider`, `SearchEngine`. |

Dependencies: `SearchEngine` consumes U1 `Repositories` (`embeddings`, `chunks`).
