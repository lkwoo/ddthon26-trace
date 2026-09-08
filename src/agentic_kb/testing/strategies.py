"""Centralized, reusable Hypothesis strategies for domain objects (PBT-07).

These generators respect domain constraints (valid Span ranges, relative
confined paths, graph edge endpoints in the node set) so property tests exercise
realistic, structurally valid inputs rather than raw primitives.
"""

from __future__ import annotations

from hypothesis import strategies as st

from ..domain.models import (
    AgentNote,
    DocElement,
    Edge,
    ModuleSummary,
    ParsedUnit,
    Reference,
    RelationshipGraph,
    SearchResult,
    SourceFile,
    Snippet,
    Span,
    StructureTree,
    Symbol,
    SyncReport,
    TreeNode,
    make_symbol_id,
)

_text = st.text(max_size=40)
_ident = st.text(alphabet="abcdefghijklmnop_", min_size=1, max_size=8)
_path_seg = st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=6)


@st.composite
def spans(draw) -> Span:
    start_line = draw(st.integers(min_value=1, max_value=1000))
    start_col = draw(st.integers(min_value=0, max_value=200))
    delta = draw(st.integers(min_value=0, max_value=50))
    end_line = start_line + delta
    if delta == 0:
        end_col = draw(st.integers(min_value=start_col, max_value=400))
    else:
        end_col = draw(st.integers(min_value=0, max_value=400))
    return Span(start_line, start_col, end_line, end_col)


@st.composite
def rel_paths(draw) -> str:
    segs = draw(st.lists(_path_seg, min_size=1, max_size=4))
    return "/".join(segs) + ".py"


@st.composite
def source_files(draw) -> SourceFile:
    return SourceFile(
        path=draw(rel_paths()),
        language=draw(st.sampled_from(["python", "markdown", "unknown"])),
        content=draw(_text),
    )


@st.composite
def symbols(draw) -> Symbol:
    path = draw(rel_paths())
    kind = draw(st.sampled_from(["file", "function", "class", "method"]))
    qname = draw(_ident)
    return Symbol(
        id=make_symbol_id(path, kind, qname),
        kind=kind,
        name=qname,
        qualified_name=qname,
        location=draw(spans()),
    )


@st.composite
def doc_elements(draw) -> DocElement:
    kind = draw(st.sampled_from(["docstring", "comment", "heading"]))
    level = draw(st.integers(min_value=1, max_value=6)) if kind == "heading" else None
    return DocElement(kind=kind, text=draw(_text), location=draw(spans()), level=level)


@st.composite
def module_summaries(draw) -> ModuleSummary:
    strs = st.lists(_text, max_size=4).map(tuple)
    return ModuleSummary(
        target=draw(rel_paths()),
        signatures=draw(strs),
        docstrings=draw(strs),
        headings=draw(strs),
        comments=draw(strs),
    )


@st.composite
def agent_notes(draw) -> AgentNote:
    return AgentNote(
        target=draw(rel_paths()),
        body_md=draw(st.text(min_size=1, max_size=40)),
        author=draw(_ident),
        created_at=draw(st.sampled_from(["2026-09-08T00:00:00Z", "2026-01-01T12:30:00+00:00"])),
    )


@st.composite
def snippets(draw) -> Snippet:
    text = draw(_text)
    return Snippet(text=text, estimated_tokens=draw(st.integers(0, 1000)), truncated=draw(st.booleans()))


@st.composite
def search_results(draw) -> SearchResult:
    return SearchResult(
        target=draw(rel_paths()),
        score=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False)),
        kind=draw(st.sampled_from(["keyword", "graph"])),
        matched_on=draw(st.sampled_from(["name", "signature", "doc", "body", "edge"])),
    )


@st.composite
def sync_reports(draw) -> SyncReport:
    return SyncReport(
        files_total=draw(st.integers(0, 10000)),
        symbols_total=draw(st.integers(0, 100000)),
        skipped=draw(st.lists(_text, max_size=4).map(tuple)),
        failures=draw(st.lists(_text, max_size=4).map(tuple)),
        duration_ms=draw(st.integers(0, 10**7)),
    )


@st.composite
def relationship_graphs(draw) -> RelationshipGraph:
    node_list = draw(st.lists(symbols(), max_size=6, unique_by=lambda s: s.id))
    ids = [n.id for n in node_list]
    if ids:
        edge_strat = st.builds(
            Edge,
            src=st.sampled_from(ids),
            dst=st.sampled_from(ids),
            kind=st.sampled_from(["call", "dependency", "import"]),
        )
        edges = draw(st.lists(edge_strat, max_size=6))
    else:
        edges = []
    return RelationshipGraph(nodes=tuple(node_list), edges=tuple(set(edges)))


@st.composite
def parsed_units(draw) -> ParsedUnit:
    return ParsedUnit(
        file=draw(source_files()),
        symbols=draw(st.lists(symbols(), max_size=4).map(tuple)),
        references=draw(
            st.lists(
                st.builds(
                    Reference,
                    src_symbol=_ident,
                    dst_name=_ident,
                    kind=st.sampled_from(["call", "dependency", "import"]),
                    location=spans(),
                ),
                max_size=4,
            ).map(tuple)
        ),
        doc_elements=draw(st.lists(doc_elements(), max_size=4).map(tuple)),
    )


def structure_trees() -> st.SearchStrategy[StructureTree]:
    leaves = st.builds(
        TreeNode, path=rel_paths(), kind=st.just("file"), name=_path_seg, children=st.just(())
    )
    tree = st.recursive(
        leaves,
        lambda children: st.builds(
            TreeNode,
            path=_path_seg,
            kind=st.just("dir"),
            name=_path_seg,
            children=st.lists(children, max_size=3).map(tuple),
        ),
        max_leaves=6,
    )
    return tree.map(lambda root: StructureTree(root=root))
