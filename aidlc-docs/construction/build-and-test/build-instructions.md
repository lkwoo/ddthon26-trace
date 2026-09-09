# Build Instructions — Dual-Interface Knowledge Store

Single installable Python package (`knowledge-store`), zero mandatory runtime
dependencies. All heavy/optional capabilities degrade gracefully.

## Prerequisites
- Python **3.10+** (developed/verified on CPython 3.14)
- No network, GPU, or system services required for a core build/test

## 1. Obtain pip (environments without pip)
Some minimal Python installs ship without `pip`/`ensurepip`. Bootstrap into a
local virtualenv:

```bash
python3 -m venv .venv
# if ensurepip is missing, bootstrap pip:
python3 -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py','/tmp/get-pip.py')"
.venv/bin/python /tmp/get-pip.py
```

If `python3 -m venv` already provides pip, skip the get-pip step.

## 2. Install the package
```bash
.venv/bin/python -m pip install .            # core (no optional deps)
# optional extras (install only what you need):
.venv/bin/python -m pip install ".[mcp]"        # MCP stdio server
.venv/bin/python -m pip install ".[embeddings]" # fastembed learned embeddings
.venv/bin/python -m pip install ".[vec]"        # sqlite-vec vector index
.venv/bin/python -m pip install ".[code]"       # tree-sitter parsing
.venv/bin/python -m pip install ".[docs]"       # pypdf + openpyxl
.venv/bin/python -m pip install ".[all]"        # everything
.venv/bin/python -m pip install ".[test]"       # pytest + hypothesis
```

## 3. Verify entry points
```bash
knowledge-store --help          # installer/ingest/manifest CLI
knowledge-store-mcp --manifest  # prints self-describing tool manifest JSON
```

## 4. Build a distribution (optional)
```bash
.venv/bin/python -m pip install build
.venv/bin/python -m build       # produces sdist + wheel in dist/
```

## Fallback matrix (verifies NFR-3 LLM-free / NFR-4 dependency-light)
| Optional dep | When present | When absent (fallback) |
|---|---|---|
| sqlite-vec | vec0 vector index | pure-Python brute-force cosine |
| fastembed | learned local embeddings | deterministic hashing embedding |
| tree-sitter | robust multi-lang parsing | regex-based analyzer |
| pypdf / openpyxl | PDF / xlsx extraction | typed ERROR status (no crash) |
| mcp | stdio MCP server | prints manifest + install hint |

A core install (no extras) builds and passes the full test suite.
