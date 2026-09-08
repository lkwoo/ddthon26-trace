"""U2 MCP provider tests: URI resolution, tool dispatch, prompts, error mapping.

Providers are exercised with real U1 services over a filesystem store/source
(no MCP SDK needed) so the delegation contract is verified end-to-end.
"""

import pytest

from agentic_kb.adapters.inbound.mcp.prompts import PromptNotFound, PromptsProvider
from agentic_kb.adapters.inbound.mcp.resources import ResourceNotFound, ResourcesProvider
from agentic_kb.adapters.inbound.mcp.server import ProviderBundle
from agentic_kb.adapters.inbound.mcp.tools import ToolsProvider
from agentic_kb.adapters.outbound.filesystem_source import FileSystemSource
from agentic_kb.adapters.outbound.filesystem_store import FileSystemKnowledgeStore
from agentic_kb.adapters.outbound.parsers import default_registry
from agentic_kb.application.query_service import QueryService
from agentic_kb.application.read_service import KnowledgeReadService
from agentic_kb.application.snippet_service import SnippetService
from agentic_kb.application.sync_service import SyncService
from agentic_kb.application.update_service import UpdateService


@pytest.fixture()
def bundle(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "a.py").write_text(
        "def helper():\n    return 1\n\n\ndef caller():\n    return helper()\n",
        encoding="utf-8",
    )
    (proj / "README.md").write_text("# Proj\n\n## Usage\n", encoding="utf-8")

    store = FileSystemKnowledgeStore(str(tmp_path / "kb"))
    source = FileSystemSource(str(proj))
    sync = SyncService(source, default_registry(), store)
    sync.run(str(proj), mode="full")

    return ProviderBundle.from_services(
        read=KnowledgeReadService(store),
        query=QueryService(store),
        snippet=SnippetService(store, source),
        update=UpdateService(store),
        sync=sync,
    ), str(proj)


# --- Resources (US-A1) ------------------------------------------------
def test_resource_structure_and_summary(bundle):
    b, _ = bundle
    r: ResourcesProvider = b.resources
    assert r.resolve("agentic-kb://structure")  # non-empty dict
    summary = r.resolve("agentic-kb://summary/a.py")
    assert summary["target"] == "a.py"
    assert r.resolve("agentic-kb://relationships")


def test_resource_missing_and_bad_uri_raise_not_found(bundle):
    b, _ = bundle
    r = b.resources
    with pytest.raises(ResourceNotFound):
        r.resolve("agentic-kb://summary/does/not/exist.py")
    with pytest.raises(ResourceNotFound):
        r.resolve("http://wrong-scheme")
    with pytest.raises(ResourceNotFound):
        r.resolve("agentic-kb://unknown")


# --- Tools (US-A2/A3/A4 + sync) --------------------------------------
def test_tool_query_keyword_and_empty(bundle):
    b, _ = bundle
    t: ToolsProvider = b.tools
    res = t.dispatch("query", {"query": "helper", "mode": "keyword"})
    assert res.is_error is False and res.content["results"]
    empty = t.dispatch("query", {"query": "zzz_no_match", "mode": "keyword"})
    assert empty.is_error is False and empty.content["results"] == []


def test_tool_snippet_respects_budget(bundle):
    b, _ = bundle
    res = b.tools.dispatch("snippet", {"target": "a.py", "token_budget": 5})
    assert res.is_error is False
    assert res.content["estimated_tokens"] <= 5


def test_tool_update_note_validation_and_persist(bundle):
    b, _ = bundle
    bad = b.tools.dispatch("update_note", {"target": "a.py"})  # missing fields
    assert bad.is_error is True
    good = b.tools.dispatch(
        "update_note",
        {"target": "a.py", "body_md": "note", "author": "agent",
         "created_at": "2026-09-08T00:00:00Z"},
    )
    assert good.is_error is False and good.content["ok"] is True


def test_tool_invalid_mode_and_unknown_tool(bundle):
    b, _ = bundle
    assert b.tools.dispatch("query", {"query": "x", "mode": "bogus"}).is_error
    assert b.tools.dispatch("snippet", {"target": "a.py", "token_budget": -1}).is_error
    assert b.tools.dispatch("does_not_exist", {}).is_error


def test_tool_sync_reports(bundle):
    b, root = bundle
    res = b.tools.dispatch("sync", {"project_root": root, "mode": "resync"})
    assert res.is_error is False
    assert res.content["files_total"] >= 2


# --- Prompts (US-A5) --------------------------------------------------
def test_prompts_render_and_unknown():
    p = PromptsProvider()
    assert "agentic-kb://structure" in p.render("onboarding")
    assert "write_unit_test" in p.render("task", {"task_kind": "write_unit_test"})
    with pytest.raises(PromptNotFound):
        p.render("nope")


def test_result_to_dict_shape(bundle):
    b, _ = bundle
    res = b.tools.dispatch("query", {"query": "helper"})
    d = res.to_dict()
    assert set(d) == {"isError", "content"}
