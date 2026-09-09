# knowledge-store — Dual-Interface Knowledge Store

A local, **LLM-free** knowledge base for a codebase and its docs, with two
interfaces over one store:

- **Agent interface** — an **MCP server over stdio** with self-describing,
  token-efficient tools (search by intent, budgeted snippets, code-structure
  and relationship reads, agent-authored summaries).
- **Human interface** — a **static HTML + D3** wiki viewer (structure tree,
  dependency graph, wiki) served straight from files, no build step.

The server never calls an LLM and never downloads a model to run. Embeddings,
chunking, versioning, and code analysis are all deterministic, with optional
accelerators (sqlite-vec, fastembed, tree-sitter, pypdf, openpyxl) that degrade
gracefully when absent.

## Requirements

- Python **3.10+** (no network or GPU required for core features)
- Zero mandatory third-party dependencies

## Install

```bash
# from the project root
pip install .
# optional accelerators / interfaces:
pip install ".[mcp]"          # MCP stdio server (the 'mcp' package)
pip install ".[embeddings]"   # learned local embeddings (fastembed)
pip install ".[vec]"          # sqlite-vec vector index
pip install ".[code]"         # tree-sitter code parsing
pip install ".[docs]"         # PDF (pypdf) + xlsx (openpyxl) extraction
pip install ".[all]"          # everything above
pip install ".[test]"         # pytest + hypothesis (for running the test suite)
```

## Quick start

```bash
# 1) initialize the store + auto-configure any detected MCP client
knowledge-store install /path/to/your/project

# 2) ingest the whole project (extract -> chunk -> version -> code graph -> embed -> link -> wiki)
#    directories are walked recursively; hidden dirs (.git, ...) and unsupported files are skipped
knowledge-store ingest /path/to/your/project --target /path/to/your/project

#    ...or narrow to specific files/subdirs if you prefer:
knowledge-store ingest src/ docs/README.md --target /path/to/your/project

# 3) open the human wiki viewer (static files, any static server works)
python -m http.server -d /path/to/your/project/.knowledge-store/wiki
```

All data lives in `<project>/.knowledge-store/` (SQLite DB + generated wiki
assets). Nothing is written outside that directory.

## Supported file formats

Ingestion resolves each file to the first matching extractor. Unrecognized
extensions are skipped (reported as `UNSUPPORTED`), never fatal. Extraction of
the formats below works with the **core** install; only PDF and xlsx need the
optional `docs` extra.

| Category | Extensions | Extra required |
|----------|-----------|----------------|
| Prose / docs | `.md`, `.markdown`, `.txt`, `.rst` | — (core) |
| Source code | `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.java`, `.go`, `.rs`, `.c`, `.h`, `.cpp`, `.cc`, `.hpp`, `.rb`, `.php`, `.cs`, `.kt`, `.swift`, `.scala`, `.sql` | — (core) |
| Markup | `.xml` | — (core) |
| Tabular | `.csv` | — (core) |
| Spreadsheet | `.xlsx` | `.[docs]` (openpyxl) |
| PDF | `.pdf` | `.[docs]` (pypdf) |

Source files are also parsed into a **code graph** (functions, classes, calls,
imports) when the `code` extra (tree-sitter) is installed; without it, code is
still ingested and searchable as text.

## Connect an AI agent (MCP over stdio)

`knowledge-store install` auto-detects **Claude Code** (`.mcp.json` / `.claude`)
and **opencode** (`opencode.json`), and merges an MCP server entry without
touching your other servers. If no client is detected, add this manually:

```json
{
  "mcpServers": {
    "knowledge-store": {
      "command": "knowledge-store-mcp",
      "args": [],
      "env": { "KNOWLEDGE_STORE_TARGET": "/path/to/your/project" }
    }
  }
}
```

Inspect the self-describing tool manifest at any time:

```bash
knowledge-store-mcp --manifest      # or: knowledge-store manifest
```

### Tools exposed to the agent

| Tool | Purpose |
|------|---------|
| `ingest` | Add/update files; refresh chunks, graph, relationships, wiki |
| `semantic_query` | Intent-based search; ranked hits with short previews |
| `smart_snippet` | Most relevant minimal scope for a chunk, within a token budget |
| `get_content_to_summarize` | Raw content for the agent to summarize |
| `store_summary` / `get_summary` | Persist / reuse agent-authored summaries |
| `read_structure` | Code graph (define/call/depend/inherit/contain) |
| `read_relationships` | Code↔document links (embedding/link/tag) |
| `regenerate_wiki` | Rebuild the static human viewer |

Each tool carries a description **and explicit "when to use" guidance**, so an
agent can discover and time calls without extra instructions.

## Testing

```bash
pip install ".[test]"
pytest
```

The suite includes property-based tests (Hypothesis) for the enforced
invariants: chunk serialize/deserialize round-trip, MinHash signature
determinism, token-estimate monotonicity, and the snippet token-budget bound.

## License & attribution

Apache License 2.0 — see [LICENSE](LICENSE). This project references and
partially ports logic from **Graphify** (Apache-2.0) and **obsidian-wiki**
(MIT); their notices are preserved in [NOTICE](NOTICE).
