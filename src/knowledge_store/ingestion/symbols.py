"""SymbolSpanExtractor — deterministic symbol boundaries with line spans.

Increment 2 / U-Chunking (item 1). A reusable, LLM-free component that finds
code symbols (functions, classes, and the **methods inside classes**) and the
*line range* each occupies, including its body. It is shared by:

* the :class:`~knowledge_store.ingestion.chunker.Chunker`, so a function or method
  becomes exactly one focused chunk (instead of being cut at blank lines, and
  without a whole class collapsing into one diluted chunk), and
* the :class:`~knowledge_store.codegraph.analyzer.CodeStructureAnalyzer`, so graph
  nodes carry ``start_line``/``end_line`` (prerequisite for line/symbol-level gold
  labels and, later, ``file:line`` citations).

Granularity is **leaf-first**: a class is decomposed into a small *header* span
(its signature + docstring + class-level attributes, up to the first method) plus
one span per method. Nested classes recurse the same way. The returned spans are
non-overlapping and cover every symbol line exactly once, so a caller can sweep
them in line order. Methods are named ``Class.method`` for readable provenance.

Python is handled precisely via indentation. For other languages no spans are
returned (callers fall back to their prior behaviour) — kept intentionally simple
and deterministic rather than guessing brace scopes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A function or class header at any indentation (matched against the *stripped*
# line; the caller enforces the scope indent).
_DEF = re.compile(r"(?:async\s+def|def|class)\s+([A-Za-z_]\w*)")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


@dataclass(frozen=True)
class SymbolSpan:
    """A code symbol and the 1-indexed inclusive line range it occupies."""

    kind: str          # "function" | "class" | "method"
    name: str          # methods are qualified as "Class.method"
    start_line: int    # 1-indexed, includes leading decorators
    end_line: int      # 1-indexed, inclusive
    text: str          # the exact source slice for [start_line, end_line]


class SymbolSpanExtractor:
    def spans(self, text: str, language: str) -> list[SymbolSpan]:
        if language == "python":
            lines = text.split("\n")
            out: list[SymbolSpan] = []
            self._collect(lines, 0, len(lines), base_indent=0, prefix="",
                          top_kind=None, out=out)
            out.sort(key=lambda s: s.start_line)
            return out
        return []

    # -- python ------------------------------------------------------------
    def _collect(self, lines: list[str], lo: int, hi: int, base_indent: int,
                 prefix: str, top_kind: str | None, out: list[SymbolSpan]) -> None:
        """Emit leaf spans for headers at exactly ``base_indent`` within [lo, hi)."""
        i = lo
        while i < hi:
            stripped = lines[i].strip()
            if stripped == "":
                i += 1
                continue
            if _indent(lines[i]) != base_indent or not _DEF.match(stripped):
                i += 1
                continue

            m = _DEF.match(stripped)
            is_class = stripped.startswith("class")
            name = m.group(1)

            # Include contiguous decorator lines immediately above, at same indent.
            start = i
            while (start - 1 >= lo and lines[start - 1].lstrip().startswith("@")
                   and _indent(lines[start - 1]) == base_indent):
                start -= 1

            # Body: following blank or deeper-indented lines; stops at the next
            # line whose indent is <= base_indent (a sibling or an outer statement).
            j = i + 1
            last_content = i
            while j < hi:
                s2 = lines[j].strip()
                if s2 == "":
                    j += 1
                    continue
                if _indent(lines[j]) <= base_indent:
                    break
                last_content = j
                j += 1
            end = last_content

            if is_class:
                # Decompose the class body into methods (recurse one level deeper).
                child_indent = self._body_indent(lines, i + 1, end + 1, base_indent)
                children: list[SymbolSpan] = []
                if child_indent is not None:
                    self._collect(lines, i + 1, end + 1, child_indent,
                                  prefix + name + ".", top_kind="method", out=children)
                if children:
                    header_end = min(c.start_line for c in children) - 2  # 0-indexed
                    self._emit(lines, start, header_end, "class", prefix + name, out)
                    out.extend(children)
                else:
                    self._emit(lines, start, end, "class", prefix + name, out)
            else:
                kind = top_kind or "function"
                self._emit(lines, start, end, kind, prefix + name, out)
            i = j

    @staticmethod
    def _body_indent(lines: list[str], lo: int, hi: int, base_indent: int) -> int | None:
        """Indent of the class body's statements (min indent > base within range)."""
        best: int | None = None
        for k in range(lo, hi):
            if lines[k].strip() == "":
                continue
            ind = _indent(lines[k])
            if ind > base_indent and (best is None or ind < best):
                best = ind
        return best

    @staticmethod
    def _emit(lines: list[str], start: int, end: int, kind: str, name: str,
              out: list[SymbolSpan]) -> None:
        if end < start:
            return
        slice_text = "\n".join(lines[start:end + 1])
        if not slice_text.strip():
            return
        out.append(SymbolSpan(kind=kind, name=name,
                              start_line=start + 1, end_line=end + 1,
                              text=slice_text))
