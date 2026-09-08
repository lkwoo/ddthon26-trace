# Performance Test Instructions

## Scope
The system is a **local, single-user, file-based** knowledge base (stdio MCP + a
localhost SSR viewer). There is no distributed load, no concurrency contract, and
no throughput SLA. Performance verification is therefore **latency-oriented** and
lightweight, tied to US-N1 / NFR-P1.

## Targets (NFR-P1 / US-N1)
| Operation | Target (typical repo, ≤ a few thousand symbols) | Notes |
|---|---|---|
| MCP tool `query` / `snippet` | interactive (sub-second) | reads from file-based store, in-memory index |
| MCP resource `structure` / `summary` / `relationships` | interactive (sub-second) | deterministic read + merge |
| Web page render (`/`, `/summary/{t}`, `/graph`) | interactive (sub-second) | pure SSR, no external assets |
| Incremental `sync` | proportional to changed files only (US-E2/BR-8) | full sync proportional to project size |

## How latency is observed
All read/tool/resource/web entry points are wrapped in `measure(label)`, which
logs elapsed milliseconds via stdlib `logging` (labels: `mcp.tool.*`,
`mcp.resource.*`, `web.*`). No external APM; the engine never calls an LLM or
network service (NFR-C3 / BR-5), so latency is deterministic and local.

## Run a manual latency check
```bash
# enable timing logs
PYTHONUNBUFFERED=1 agentic-kb ingest --project <path> --store /tmp/kb
# exercise reads and observe the measure() log lines
.venv/bin/python - <<'PY'
import logging, time
logging.basicConfig(level=logging.INFO)
from agentic_kb.config import AppConfig, assemble
app = assemble(AppConfig(project_root="<path>", store_dir="/tmp/kb"))
t0 = time.perf_counter()
app.mcp_bundle.tools.dispatch("query", {"query": "load", "mode": "keyword"})
print("query ms:", (time.perf_counter() - t0) * 1000)
PY
```

## Pass criteria
- Operations complete within interactive latency on a representative repo.
- No unbounded growth: snippet output respects `token_budget` (verified in unit/integration tests).
- **Load / stress / soak testing: N/A** — out of scope for a single-user local tool.
