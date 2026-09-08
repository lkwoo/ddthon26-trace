"""Deterministic structured extraction (US-E3, NFR-C3).

Produces a `ModuleSummary` from a `ParsedUnit` using only local, deterministic
processing — no LLM / external calls (BR-5). Identical input yields identical
output (US-E3 AC-3).
"""

from __future__ import annotations

from ..domain.models import ModuleSummary, ParsedUnit

# Deterministic cap on representative comments retained per module.
_MAX_COMMENTS = 20


def extract(unit: ParsedUnit) -> ModuleSummary:
    signatures = tuple(
        _signature(sym)
        for sym in sorted(unit.symbols, key=lambda s: (s.location.start_line, s.id))
        if sym.kind in ("function", "class", "method")
    )

    docstrings = tuple(
        el.text.strip()
        for el in sorted(unit.doc_elements, key=_doc_key)
        if el.kind == "docstring" and el.text.strip()
    )

    headings = tuple(
        _heading(el)
        for el in sorted(unit.doc_elements, key=_doc_key)
        if el.kind == "heading"
    )

    comments_all = [
        el.text.strip()
        for el in sorted(unit.doc_elements, key=_doc_key)
        if el.kind == "comment" and el.text.strip()
    ]
    comments = tuple(comments_all[:_MAX_COMMENTS])

    return ModuleSummary(
        target=unit.file.path,
        signatures=signatures,
        docstrings=docstrings,
        headings=headings,
        comments=comments,
    )


def _doc_key(el) -> tuple[int, int]:
    return (el.location.start_line, el.location.start_col)


def _signature(sym) -> str:
    return f"{sym.kind} {sym.qualified_name}"


def _heading(el) -> str:
    level = el.level or 1
    return f"{'#' * level} {el.text.strip()}"
