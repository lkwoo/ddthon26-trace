"""PBT-02 round-trip properties: from_dict(to_dict(x)) == x for every entity."""

import json

from hypothesis import given

from agentic_kb.domain.models import (
    AgentNote,
    ModuleSummary,
    ParsedUnit,
    RelationshipGraph,
    SearchResult,
    Snippet,
    SourceFile,
    StructureTree,
    Symbol,
    SyncReport,
)
from agentic_kb.testing import strategies as ge


def _roundtrip(cls, x):
    assert cls.from_dict(x.to_dict()) == x
    # also survives a JSON encode/decode cycle (storage fidelity)
    assert cls.from_dict(json.loads(json.dumps(x.to_dict()))) == x


@given(ge.source_files())
def test_source_file_roundtrip(x):
    _roundtrip(SourceFile, x)


@given(ge.symbols())
def test_symbol_roundtrip(x):
    _roundtrip(Symbol, x)


@given(ge.module_summaries())
def test_module_summary_roundtrip(x):
    _roundtrip(ModuleSummary, x)


@given(ge.agent_notes())
def test_agent_note_roundtrip(x):
    _roundtrip(AgentNote, x)


@given(ge.snippets())
def test_snippet_roundtrip(x):
    _roundtrip(Snippet, x)


@given(ge.search_results())
def test_search_result_roundtrip(x):
    _roundtrip(SearchResult, x)


@given(ge.sync_reports())
def test_sync_report_roundtrip(x):
    _roundtrip(SyncReport, x)


@given(ge.relationship_graphs())
def test_relationship_graph_roundtrip(x):
    _roundtrip(RelationshipGraph, x)


@given(ge.parsed_units())
def test_parsed_unit_roundtrip(x):
    _roundtrip(ParsedUnit, x)


@given(ge.structure_trees())
def test_structure_tree_roundtrip(x):
    _roundtrip(StructureTree, x)
