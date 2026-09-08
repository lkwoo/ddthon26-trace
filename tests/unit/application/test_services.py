"""Application service tests: sync pipeline, read merge, query, snippet, update."""

import os

import pytest

from agentic_kb.adapters.outbound.filesystem_source import FileSystemSource
from agentic_kb.adapters.outbound.filesystem_store import FileSystemKnowledgeStore
from agentic_kb.adapters.outbound.parsers import default_registry
from agentic_kb.application.payloads import AgentNotePayload
from agentic_kb.application.query_service import QueryService
from agentic_kb.application.read_service import KnowledgeReadService
from agentic_kb.application.snippet_service import SnippetService
from agentic_kb.application.sync_service import SyncService
from agentic_kb.application.update_service import UpdateService


@pytest.fixture()
def project(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "a.py").write_text(
        'def helper():\n    return 1\n\n\ndef caller():\n    return helper()\n',
        encoding="utf-8",
    )
    (proj / "README.md").write_text("# Proj\n\n## Usage\n", encoding="utf-8")
    (proj / "data.bin").write_text("ignored", encoding="utf-8")  # unsupported ext
    return proj


@pytest.fixture()
def wired(tmp_path, project):
    store = FileSystemKnowledgeStore(str(tmp_path / "kb"))
    source = FileSystemSource(str(project))
    registry = default_registry()
    sync = SyncService(source, registry, store)
    return store, source, sync, str(project)


def test_sync_reports_scale_and_skips_unsupported(wired):
    store, source, sync, root = wired
    report = sync.run(root, mode="full")
    assert report.files_total >= 2  # a.py + README.md (data.bin excluded by discover)
    assert report.symbols_total > 0
    assert not report.failures


def test_resync_skips_unchanged(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    report2 = sync.run(root, mode="resync")
    assert any("unchanged" in s for s in report2.skipped)


def test_read_merges_engine_and_agent_notes(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    read = KnowledgeReadService(store)

    tree = read.get_structure()
    assert tree is not None

    merged = read.get_summary("a.py")
    assert merged is not None
    assert merged.engine is not None
    assert merged.engine_first is True

    # missing target -> None (BR-13)
    assert read.get_summary("does/not/exist.py") is None


def test_query_keyword_and_graph(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    q = QueryService(store)
    assert q.query("helper", mode="keyword")
    assert q.query("no_such_symbol_zzz", mode="keyword") == []


def test_snippet_respects_budget(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    snip = SnippetService(store, source).snippet("a.py", token_budget=5)
    assert snip.estimated_tokens <= 5


def test_update_note_validation_and_persist(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    upd = UpdateService(store)

    bad = upd.apply_note(AgentNotePayload(target="", body_md="", author="", created_at="nope"))
    assert bad.ok is False and bad.errors

    good = upd.apply_note(
        AgentNotePayload(target="a.py", body_md="Deep dive.", author="agent1",
                         created_at="2026-09-08T00:00:00Z")
    )
    assert good.ok is True and good.note_id

    # note is merged on read, engine artifacts untouched
    merged = KnowledgeReadService(store).get_summary("a.py")
    assert merged is not None and len(merged.agent_notes) == 1


def test_agent_notes_preserved_across_resync(wired):
    store, source, sync, root = wired
    sync.run(root, mode="full")
    UpdateService(store).apply_note(
        AgentNotePayload(target="a.py", body_md="note", author="a",
                         created_at="2026-09-08T00:00:00Z")
    )
    sync.run(root, mode="full")  # re-sync must not delete notes (BR-9)
    merged = KnowledgeReadService(store).get_summary("a.py")
    assert merged is not None and len(merged.agent_notes) == 1
