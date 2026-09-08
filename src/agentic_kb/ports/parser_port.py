"""LanguageParserPort — abstract contract for language parsers (NFR-C2)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain.models import ParsedUnit, SourceFile


class LanguageParserPort(ABC):
    @abstractmethod
    def parse(self, file: SourceFile) -> ParsedUnit:
        """Parse a source file into symbols, references, and doc elements."""

    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """Return the set of file extensions this parser handles (e.g. {'.py'})."""
