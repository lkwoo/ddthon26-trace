#!/usr/bin/env bash
# Convenience installer for knowledge-store (Linux / macOS).
#
# Creates a local virtual environment (.venv) next to this script and installs
# the package into it. Safe to re-run (idempotent).
#
# Usage:
#   ./install.sh            # install with all optional features ([all])
#   ./install.sh mcp        # install a single extra, e.g. just the MCP server
#   ./install.sh none       # install core only (no optional dependencies)
#
# Valid extras: all (default), mcp, embeddings, vec, code, docs, test, none.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

EXTRAS="${1:-all}"

# 1) locate a Python >= 3.10 interpreter
PYTHON=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PYTHON="$cand"
      break
    fi
  fi
done
if [ -z "$PYTHON" ]; then
  echo "ERROR: Python 3.10+ is required but was not found on PATH." >&2
  exit 1
fi
echo "Using Python: $($PYTHON --version) ($(command -v "$PYTHON"))"

# 2) create the virtual environment (idempotent)
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment at $VENV_DIR"
  if ! "$PYTHON" -m venv "$VENV_DIR"; then
    echo "ERROR: failed to create the virtual environment (see message above)." >&2
    echo "On Debian/Ubuntu/WSL, install the venv package first, e.g.:" >&2
    echo "    sudo apt install python3-venv" >&2
    exit 1
  fi
fi
VENV_PY="$VENV_DIR/bin/python"

# ensure pip is available inside the venv (ensurepip is missing on some distros)
if ! "$VENV_PY" -m pip --version >/dev/null 2>&1; then
  echo "pip not found in the virtual environment; bootstrapping with ensurepip..."
  if ! "$VENV_PY" -m ensurepip --upgrade >/dev/null 2>&1; then
    echo "ERROR: pip is unavailable and ensurepip failed." >&2
    echo "On Debian/Ubuntu/WSL, install the venv package: sudo apt install python3-venv" >&2
    exit 1
  fi
fi

# 3) install the package
"$VENV_PY" -m pip install --upgrade pip >/dev/null
if [ "$EXTRAS" = "none" ]; then
  echo "Installing knowledge-store (core only)..."
  "$VENV_PY" -m pip install .
else
  echo "Installing knowledge-store with extra: [$EXTRAS] ..."
  "$VENV_PY" -m pip install ".[$EXTRAS]"
fi

echo
echo "Done. knowledge-store is installed in $VENV_DIR"
echo
echo "Run it directly:"
echo "  $VENV_DIR/bin/knowledge-store --help"
echo
echo "...or activate the environment first:"
echo "  source $VENV_DIR/bin/activate"
echo "  knowledge-store install /path/to/your/project"
echo "  knowledge-store ingest  /path/to/your/project --target /path/to/your/project"
