# Performance Test Instructions

The store targets **low-latency, token-efficient reads** (NFR-1) on local,
single-user workloads. There is no cloud infra; performance testing is a set of
local micro-benchmarks and budget checks rather than load testing.

## What to measure (NFR-1)
1. **Query latency** — time `QueryService.semantic_query(intent, limit)` on a
   store with N chunks (e.g., N = 1k, 10k). Target: interactive (< ~200 ms with
   sqlite-vec; brute-force fallback scales linearly — acceptable for local N).
2. **Snippet token budget** (NFR-1.2) — `SnippetBuilder.build` must return
   `estimated_tokens <= token_budget`; this is asserted as a property (PBT-03),
   so correctness is already guaranteed; benchmark only its runtime.
3. **Ingest throughput** — files/sec and chunks/sec through
   `IngestionService.ingest` (extract→chunk→version→graph→embed→relate).

## Simple local harness
```bash
.venv/bin/python - <<'PY'
import time, tempfile, pathlib
from knowledge_store.services import KnowledgeSystem, IngestionService, QueryService

d = tempfile.mkdtemp()
proj = pathlib.Path(d, "proj"); proj.mkdir()
for i in range(200):
    (proj / f"doc{i}.md").write_text(f"# Doc {i}\nContent about topic {i} and #tag{i%10}.\n")

sys = KnowledgeSystem(d)
t0 = time.perf_counter()
rep = IngestionService(sys).ingest([str(p) for p in proj.glob('*.md')], export=False)
t1 = time.perf_counter()
q = QueryService(sys)
t2 = time.perf_counter()
for _ in range(50):
    q.semantic_query("topic 42", limit=5)
t3 = time.perf_counter()
print(f"ingest: {rep.ingested_files} files, {rep.chunks_new} chunks in {t1-t0:.3f}s")
print(f"query : 50 queries in {t3-t2:.3f}s ({(t3-t2)/50*1000:.2f} ms/query)")
sys.close()
PY
```

## Accelerators to compare
- Install `.[vec]` (sqlite-vec) and `.[embeddings]` (fastembed) and re-run to
  compare query latency and relevance vs the deterministic fallbacks.

## Notes
- Performance rules are **advisory** for this project (no NFR SLA gate).
- Determinism/round-trip correctness is enforced separately via PBT (see
  unit-test-instructions.md), independent of timing.
