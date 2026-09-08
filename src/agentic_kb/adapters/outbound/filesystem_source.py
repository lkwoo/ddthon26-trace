"""FileSystemSource — local filesystem implementation of FileSourcePort.

Walks a project root, collecting only supported extensions (US-E1 AC-2), and
confines all access to within the root (BR-4, path confinement).
"""

from __future__ import annotations

import os

from ...domain.models import SourceFile
from ...ports.source_port import FileSourcePort, SourceFilter


def _detect_language(path: str) -> str:
    ext = path[path.rfind(".") :].lower() if "." in path else ""
    return {
        ".py": "python",
        ".md": "markdown",
        ".markdown": "markdown",
    }.get(ext, "unknown")


class FileSystemSource(FileSourcePort):
    def __init__(self, root: str) -> None:
        self._root = os.path.abspath(root)

    def discover(self, root: str, filters: SourceFilter) -> list[SourceFile]:
        base = os.path.abspath(root)
        files: list[SourceFile] = []
        for dirpath, dirnames, filenames in os.walk(base):
            # prune excluded dirs in-place for efficiency + determinism
            dirnames[:] = sorted(d for d in dirnames if d not in filters.exclude_dirs)
            for fname in sorted(filenames):
                ext = fname[fname.rfind(".") :].lower() if "." in fname else ""
                if filters.extensions and ext not in filters.extensions:
                    continue
                abs_path = os.path.join(dirpath, fname)
                rel = os.path.relpath(abs_path, base).replace(os.sep, "/")
                try:
                    content = self._read_confined(abs_path, base)
                except (OSError, UnicodeDecodeError):
                    continue  # unreadable/binary -> skip (caller records if needed)
                files.append(SourceFile(path=rel, language=_detect_language(rel), content=content))
        return files

    def read(self, path: str) -> str:
        abs_path = os.path.abspath(os.path.join(self._root, path))
        return self._read_confined(abs_path, self._root)

    @staticmethod
    def _read_confined(abs_path: str, base: str) -> str:
        base_real = os.path.realpath(base)
        target_real = os.path.realpath(abs_path)
        if os.path.commonpath([base_real, target_real]) != base_real:
            raise ValueError(f"path escapes project root: {abs_path}")
        with open(target_real, encoding="utf-8") as fh:
            return fh.read()
