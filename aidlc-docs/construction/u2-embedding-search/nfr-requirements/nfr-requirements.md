# U2 Embedding & Semantic Search — NFR Requirements

## NFR-1 Performance / Latency (NFR-1.1 ~1s, NFR-1.2 token efficiency)
- Single query embed + one indexed vector lookup per `search`. sqlite-vec `MATCH`
  provides native ANN; the fallback is a bounded in-memory cosine scan.
- Empty-intent short circuit avoids needless work.
- `search` returns at most `limit` hits, each with a <=160-char preview only,
  minimizing tokens returned to the agent (NFR-1.2, US-9.3).
- Batch indexing (`index_many`) embeds all texts in one provider call.

## NFR-3 LLM-free / Offline (NFR-3.1)
- No network or external API. `HashingEmbeddingProvider` needs no model at all;
  `LocalEmbeddingProvider` runs `fastembed` locally when present. Embeddings are
  computed on local compute only.

## NFR-4 Dependency-light / Installability
- `fastembed` is an optional extra (`[embeddings]` in `pyproject.toml`). With it
  absent, `LocalEmbeddingProvider` transparently uses the stdlib-only hashing
  provider (`hashlib`, `math`, `re`). The unit installs and runs with zero extras.

## NFR-8 Testing (PBT Partial)
- The hashing provider's determinism, fixed dimension, normalization, and
  empty-input behaviour are pure-function properties suited to Hypothesis
  (PBT-02/03/07/08/09). See functional-design/domain-entities.md.

## Marked N/A
- **Security Baseline** — extension OFF. No auth/crypto/PII handling in a local
  embedding/search path.
- **Resiliency Baseline** — extension OFF. In-process, no remote calls to retry
  or circuit-break; the fastembed fallback already provides graceful degradation
  as a functional design choice, not a resiliency-extension requirement.
