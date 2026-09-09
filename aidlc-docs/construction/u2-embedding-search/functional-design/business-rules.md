# U2 Embedding & Semantic Search — Business Rules

Rules the code enforces. Source: `knowledge_store/embedding/{provider,search}.py`.

## BR-U2-1 — Deterministic offline embedding (NFR-3.1, US-3.1, supports NFR-8)
`HashingEmbeddingProvider._embed_one` maps identical text to an identical vector:
tokens are lowercased via a fixed regex, hashed with `md5`, bucketed by
`int.from_bytes(h[:4]) % dim`, signed by `h[4] & 1`, weighted `1 + log(count)`,
then L2-normalized. No randomness, no state, no network — so relationship and
versioning behaviour downstream is reproducible.

## BR-U2-2 — LLM-free / no external API (NFR-3.1, FR-3.1)
Neither provider calls a remote service. `fastembed` (when used) runs a small
model locally; the default path needs no model download at all. `embed([])`
returns `[]` (empty-input guard).

## BR-U2-3 — Graceful fastembed fallback (NFR-4, NFR-3.1)
`LocalEmbeddingProvider.__init__` tries `from fastembed import TextEmbedding`;
any exception leaves `self._model = None`. `embed()` then delegates to the
`HashingEmbeddingProvider`. `is_learned` reports which path is active. The system
therefore runs dependency-light with zero downloads, or upgrades to a learned
model transparently when `fastembed` is installed.

## BR-U2-4 — Dimension consistency with the vec table (FR-3.1, FR-6.2)
`LocalEmbeddingProvider` probes its real dimension once at init (`len(probe[0])`)
and exposes it via `dimension`; the hashing fallback uses a fixed 256. The store
creates the `vec0` table with `float[dimension]` from the provider's dimension
(U1 `init_schema(embedding_dimension)`), so indexed and queried vectors share one
width. All vectors from a single provider are the same length.

## BR-U2-5 — Empty-intent short circuit (NFR-1)
`SearchEngine.search` returns `[]` immediately when `intent.strip()` is empty —
no embedding call, no DB scan.

## BR-U2-6 — Ranking rules (US-6.2, NFR-1)
Ranking is delegated to `EmbeddingRepository.search`: with sqlite-vec, results
come `ORDER BY distance` with score `1/(1+distance)` (higher = closer); without
it, brute-force cosine sorted descending. Either way `SearchEngine` returns at
most `limit` `SearchHit`s, most-relevant first.

## BR-U2-7 — Token-efficient previews (NFR-1.2, US-9.3)
After ranking, `search` attaches only a <=160-char `preview` per hit from the
chunk store (when the ref resolves), never full text — minimizing tokens
returned to the agent.

## BR-U2-8 — Single default provider (consistency)
`get_default_provider()` memoizes one process-wide provider so indexing and
querying use the same embedding space; `SearchEngine` defaults to it when none is
injected.

## Requirement coverage
FR-3.1, FR-6.2; NFR-1, NFR-1.2, NFR-3.1, NFR-4; US-3.1, US-6.2, US-9.3.
