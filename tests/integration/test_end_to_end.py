"""Integration tests: exercise U1↔U2↔U3↔U4 together over a real project.

These verify the units interoperate through the assembled composition root:
ingest (U4→U1) → MCP tools/resources (U2→U1) → web viewer (U3→U1), with agent
notes persisted across a re-sync (US-A4/E5, engine-first).
"""

import pytest

from agentic_kb.config import AppConfig, assemble


@pytest.fixture()
def app(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "svc.py").write_text(
        '"""Service module."""\n\n\ndef load():\n    return parse()\n\n\ndef parse():\n    return 1\n',
        encoding="utf-8",
    )
    (proj / "docs.md").write_text("# Guide\n\n## Setup\n\nrun it.\n", encoding="utf-8")
    cfg = AppConfig(project_root=str(proj), store_dir=str(tmp_path / "kb"))
    application = assemble(cfg)
    application.sync.run(cfg.project_root, mode="full")  # U4→U1 ingest
    return application


# --- U4→U1 ingest feeds U2 MCP surface --------------------------------
def test_mcp_resources_after_ingest(app):
    structure = app.mcp_bundle.resources.resolve("agentic-kb://structure")
    assert structure  # non-empty
    summary = app.mcp_bundle.resources.resolve("agentic-kb://summary/svc.py")
    assert summary["target"] == "svc.py"
    graph = app.mcp_bundle.resources.resolve("agentic-kb://relationships")
    assert graph["nodes"]


def test_mcp_query_and_snippet_tools(app):
    q = app.mcp_bundle.tools.dispatch("query", {"query": "parse", "mode": "keyword"})
    assert q.is_error is False and q.content["results"]
    s = app.mcp_bundle.tools.dispatch("snippet", {"target": "svc.py", "token_budget": 30})
    assert s.is_error is False and s.content["estimated_tokens"] <= 30


# --- U2 update note -> visible in U3 web viewer (engine-first merge) ---
def test_agent_note_flows_from_mcp_to_web(app):
    res = app.mcp_bundle.tools.dispatch(
        "update_note",
        {"target": "svc.py", "body_md": "Deep design note.", "author": "agent",
         "created_at": "2026-09-08T00:00:00Z"},
    )
    assert res.is_error is False

    page = app.web_app.handle("/summary/svc.py")
    assert page.status == 200
    assert "Deep design note." in page.body
    assert "엔진 자동 생성" in page.body  # engine section present too


# --- re-sync preserves agent notes (US-E5 engine-first, BR-9) ---------
def test_resync_preserves_notes_and_regenerates_engine(app):
    app.mcp_bundle.tools.dispatch(
        "update_note",
        {"target": "svc.py", "body_md": "kept", "author": "a",
         "created_at": "2026-09-08T00:00:00Z"},
    )
    app.sync.run(app.config.project_root, mode="full")  # re-sync
    merged = app.read.get_summary("svc.py")
    assert merged is not None
    assert merged.engine is not None  # engine regenerated
    assert any(n.body_md == "kept" for n in merged.agent_notes)  # note preserved


# --- web tree + graph render after ingest -----------------------------
def test_web_tree_and_graph_render(app):
    tree = app.web_app.handle("/")
    assert tree.status == 200 and "svc.py" in tree.body
    graph = app.web_app.handle("/graph")
    assert graph.status == 200 and "Dependency Graph" in graph.body
