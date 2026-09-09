#!/usr/bin/env bash
# Uninstaller for knowledge-store (Linux / macOS).
#
# By default this removes the pip package from the local virtual environment.
# Pass --purge to also delete the .venv directory created by install.sh.
#
# Your ingested data (each project's .knowledge-store/ directory) is NEVER
# touched by this script.
#
# Usage:
#   ./uninstall.sh            # remove the package, keep the .venv
#   ./uninstall.sh --purge    # remove the package AND delete .venv
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PURGE=0
if [ "${1:-}" = "--purge" ]; then
  PURGE=1
fi

VENV_DIR="$SCRIPT_DIR/.venv"
if [ -x "$VENV_DIR/bin/python" ]; then
  echo "Uninstalling knowledge-store from $VENV_DIR ..."
  "$VENV_DIR/bin/python" -m pip uninstall -y knowledge-store || true
else
  echo "No local .venv found; attempting uninstall with system pip..."
  python3 -m pip uninstall -y knowledge-store || true
fi

if [ "$PURGE" -eq 1 ] && [ -d "$VENV_DIR" ]; then
  echo "Removing virtual environment $VENV_DIR ..."
  rm -rf "$VENV_DIR"
fi

echo "Done."
echo "Note: ingested data in each project's .knowledge-store/ directory was left untouched."
