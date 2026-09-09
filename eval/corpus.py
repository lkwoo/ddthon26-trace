"""Corpus resolution — expand dataset ``corpus`` entries into concrete files.

Each entry (relative to a root) may be a single file, a directory (expanded to
its ``*.py``/``*.md``/``*.txt``/``*.rst`` files, recursively), or a glob. Results
are de-duplicated and returned as root-relative POSIX paths so they line up with
gold labels.
"""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_EXTS = (".py", ".md", ".txt", ".rst")


def resolve_corpus(root: str | Path, entries: list[str],
                   exts: tuple[str, ...] = _DEFAULT_EXTS) -> list[str]:
    root_path = Path(root).resolve()
    found: list[str] = []
    seen: set[str] = set()

    def add(p: Path) -> None:
        if not p.is_file():
            return
        rel = os.path.relpath(p.resolve(), root_path).replace(os.sep, "/")
        if rel not in seen:
            seen.add(rel)
            found.append(rel)

    for entry in entries:
        base = (root_path / entry)
        if base.is_dir():
            for ext in exts:
                for p in sorted(base.rglob(f"*{ext}")):
                    add(p)
        elif base.is_file():
            add(base)
        else:
            # Treat as a glob relative to root.
            for p in sorted(root_path.glob(entry)):
                add(p)
    return sorted(found)
