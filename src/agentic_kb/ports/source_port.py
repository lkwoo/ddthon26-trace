"""FileSourcePort — abstract contract for discovering and reading source files."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..domain.models import SourceFile


@dataclass(frozen=True)
class SourceFilter:
    """Discovery filter. Only supported extensions are collected (US-E1 AC-2)."""

    extensions: frozenset[str] = frozenset()
    exclude_dirs: frozenset[str] = field(
        default=frozenset({".git", ".agentic_kb", "__pycache__", ".venv", "node_modules"})
    )


class FileSourcePort(ABC):
    @abstractmethod
    def discover(self, root: str, filters: SourceFilter) -> list[SourceFile]:
        """Return supported files under root; unsupported are skipped."""

    @abstractmethod
    def read(self, path: str) -> str:
        """Read a file's text content."""
