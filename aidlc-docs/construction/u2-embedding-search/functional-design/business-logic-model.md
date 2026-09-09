# U2 Embedding & Semantic Search — Business Logic Model

**Unit**: u2-embedding-search
**Bounded context**: Semantic Retrieval (vector layer)
**Components**: C11 EmbeddingProvider, C9 SearchEngine
**Source**: `knowledge_store/embedding/{provider,search,__init__}.py`
**Depends on**: U1 (`EmbeddingRepository` via `Repositories`)

## Responsibilities

- Produce local, offline embeddings for text (`embed`) and report vector
  `dimension` — no network, no external LLM/API (NFR-3.1).
- Provide two interchangeable providers behind one `EmbeddingProvider` protocol:
  a learned model (`LocalEmbeddingProvider` via optional `fastembed`) and a
  deterministic dependency-free fallback (`HashingEmbeddingProvider`).
- Index chunk/symbol text into the vector store and run intent-based semantic
  search with ranking (`SearchEngine`), delegating storage to U1's
  `EmbeddingRepository`.

## Key classes and methods

- `EmbeddingProvider` (runtime-checkable `Protocol`) — `dimension` (property),
  `embed(texts) -> list[list[float]]`.
- `HashingEmbeddingProvider(dimension=256)` — `_embed_one()`, `embed()`;
  deterministic feature-hashing (md5-hashed tokens, signed, log term-weighted,
  L2-normalized).
- `LocalEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5")` — wraps
  `fastembed.TextEmbedding` when importable, probes dimension once; `is_learned`
  property; `embed()` uses the model or delegates to the hashing fallback.
- `get_default_provider()` — process-wide singleton (learned if available, else
  hashing).
- `SearchEngine(repos, provider=None)` — `provider` (property),
  `index(ref_id, text, kind)`, `index_many(items, kind)`, `search(intent, limit)`.

## Operation flow

Index path:
1. `SearchEngine.index_many([(ref_id, text), ...])` -> `provider.embed(texts)`.
2. Each vector is written via `repos.embeddings.upsert(ref_id, vector, kind)`.

Query path (`search(intent, limit)`):
1. Empty/whitespace intent -> return `[]` (guard).
2. `provider.embed([intent])[0]` -> query vector.
3. `repos.embeddings.search(query_vec, limit)` -> ranked `list[SearchHit]`
   (vec0 or cosine fallback, decided in U1).
4. Attach a <=160-char `preview` from `repos.chunks.get(ref_id)` when available
   (token-efficient, NFR-1.2).

## Component / interaction sketch (plain ASCII)

```
   QueryService.semantic_query(intent, limit)
                |
                v
           SearchEngine
        +-------+--------+
        |                |
        v                v
  EmbeddingProvider   Repositories.embeddings   Repositories.chunks
  (protocol)          (U1: upsert/search)        (preview text)
     |     \
     |      \-- LocalEmbeddingProvider (fastembed, optional)
     |             |
     |             \-- fallback -->
     \--------------------------- HashingEmbeddingProvider (deterministic)
```
