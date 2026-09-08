"""Example-based tests for the Python parser, extractor, and query (PBT-10)."""

from agentic_kb.adapters.outbound.parsers import MarkdownParser, PythonAstParser
from agentic_kb.domain import graph_builder
from agentic_kb.domain.extractor import extract
from agentic_kb.domain.models import SourceFile
from agentic_kb.domain.query import SearchIndex, neighbors, search_keyword

PY = '''\
"""Module doc."""


def helper():
    return 1


def caller():
    return helper()


class Widget:
    def render(self):
        return helper()
'''


def _parse_py(content=PY, path="mod.py"):
    return PythonAstParser().parse(SourceFile(path=path, language="python", content=content))


def test_python_parser_symbols_and_refs():
    unit = _parse_py()
    kinds = {s.kind for s in unit.symbols}
    assert {"file", "function", "class", "method"} <= kinds
    # caller() -> helper() call reference exists
    assert any(r.dst_name == "helper" and r.kind == "call" for r in unit.references)


def test_parser_deterministic():
    assert _parse_py() == _parse_py()


def test_extractor_deterministic_and_signatures():
    unit = _parse_py()
    s1 = extract(unit)
    s2 = extract(unit)
    assert s1 == s2
    assert "Module doc." in s1.docstrings
    assert any("caller" in sig for sig in s1.signatures)


def test_graph_neighbors():
    unit = _parse_py()
    graph = graph_builder.build([unit])
    helper_id = next(n.id for n in graph.nodes if n.name == "helper")
    callers = neighbors(graph, helper_id, "callers")
    assert callers  # helper is called by caller() and Widget.render()


def test_keyword_search_ranks_name_exact_first():
    unit = _parse_py()
    graph = graph_builder.build([unit])
    index = SearchIndex(symbols=tuple(graph.nodes), summaries=(extract(unit),))
    results = search_keyword(index, "helper")
    assert results
    assert results[0].score >= results[-1].score
    assert search_keyword(index, "nonexistent_term_xyz") == []


def test_markdown_parser_headings():
    md = "# Title\n\nsome text\n\n## Section\n"
    unit = MarkdownParser().parse(SourceFile(path="doc.md", language="markdown", content=md))
    headings = [d for d in unit.doc_elements if d.kind == "heading"]
    assert {h.text for h in headings} == {"Title", "Section"}
