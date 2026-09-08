# Build Instructions

## Prerequisites
- **Build Tool**: Python packaging (PEP 517), backend **hatchling**. `pyproject.toml` at repo root.
- **Runtime**: **Python ≥ 3.11** (validated on 3.14). Engine core (U1) has **zero required runtime deps** beyond the stdlib.
- **Optional dependencies**:
  - `[mcp]` — `mcp>=1.0` (only for `serve-mcp` / U2 live server)
  - `[treesitter]` — future multi-language parsers (not needed for MVP; MVP uses stdlib `ast`)
  - `[web]` — empty (U3 web viewer is stdlib-only)
  - `[dev]` — `pytest>=8.0`, `hypothesis>=6.100` (PBT-09)
- **Environment Variables**: none required. Optional `HYPOTHESIS_PROFILE=ci|dev` for PBT runs.
- **System Requirements**: any OS with CPython ≥ 3.11; negligible memory/disk (file-based KB).

## Build Steps

### 1. Create a virtual environment
```bash
python3 -m venv .venv
```

### 2. Install (editable) with dev dependencies
```bash
.venv/bin/python -m pip install -e ".[dev]"
# add MCP server support when needed:
.venv/bin/python -m pip install -e ".[dev,mcp]"
```

### 3. Build distribution artifacts (optional)
```bash
.venv/bin/python -m pip install build
.venv/bin/python -m build          # produces dist/*.whl and dist/*.tar.gz
```

### 4. Verify Build Success
- **Expected Output**: editable install completes; `agentic-kb --help` lists subcommands `{ingest, sync, serve-mcp, serve-web}`.
- **Build Artifacts**: console script `agentic-kb` (from `[project.scripts]`); wheel/sdist under `dist/` if `build` was run.
- **Common Warnings**: none expected.

## Troubleshooting

### `No module named pip` / `ensurepip` missing (minimal Python)
- **Cause**: some distributions ship Python without pip/ensurepip.
- **Solution**: bootstrap pip into the venv:
  ```bash
  python3 -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py','/tmp/get-pip.py')"
  .venv/bin/python /tmp/get-pip.py
  ```

### `serve-mcp` fails with a RuntimeError about the `[mcp]` extra
- **Cause**: optional `mcp` SDK not installed.
- **Solution**: `pip install -e ".[mcp]"`.
