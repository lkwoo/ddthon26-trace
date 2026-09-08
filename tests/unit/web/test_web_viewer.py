"""U3 Web Viewer tests: routing, pure rendering, and WebApp dispatch.

No live HTTP server needed — WebApp.handle is exercised directly over real U1
services (US-H1..H4, BR-W*).
"""

import pytest

from agentic_kb.adapters.inbound.web import routing
from agentic_kb.adapters.inbound.web.app import WebApp
from agentic_kb.adapters.inbound.web.rendering import markdown_to_html, render_wiki
from agentic_kb.adapters.outbound.filesystem_source import FileSystemSource
from agentic_kb.adapters.outbound.filesystem_store import FileSystemKnowledgeStore
from agentic_kb.adapters.outbound.parsers import default_registry
from agentic_kb.application.payloads import AgentNotePayload
from agentic_kb.application.read_service import KnowledgeReadService
from agentic_kb.application.sync_service import SyncService
from agentic_kb.application.update_service import UpdateService
from agentic_kb.domain.models import AgentNote, MergedSummary, ModuleSummary


# --- routing ----------------------------------------------------------
def test_routing_table():
    assert routing.match("/").view == "index"
    assert routing.match("/static/style.css").view == "static"
    r = routing.match("/summary/a.py")
    assert r.view == "summary" and r.target == "a.py"
    assert routing.match("/graph").view == "graph"
    assert routing.match("/graph/a.py").target == "a.py"
    assert routing.match("/bogus").view == "not_found"
    # query string stripped
    assert routing.match("/graph?x=1").view == "graph"


# --- markdown subset --------------------------------------------------
def test_markdown_escapes_and_renders():
    html = markdown_to_html("# Title\n\nsome `code` & <b>x</b>\n\n- one\n- two")
    assert "<h1>Title</h1>" in html
    assert "<code>code</code>" in html
    assert "&lt;b&gt;" in html  # raw HTML escaped (BR-W6)
    assert "<ul><li>one</li><li>two</li></ul>" in html


def test_markdown_code_fence():
    html = markdown_to_html("```\ndef f():\n    return 1\n```")
    assert "<pre><code>" in html and "def f()" in html


def test_markdown_deterministic():
    md = "# H\n\ntext\n\n- a"
    assert markdown_to_html(md) == markdown_to_html(md)


# --- wiki provenance --------------------------------------------------
def test_render_wiki_shows_engine_and_notes_with_banner():
    merged = MergedSummary(
        target="a.py",
        engine=ModuleSummary(target="a.py", signatures=("def caller()",)),
        agent_notes=(AgentNote(target="a.py", body_md="deep note", author="ag",
                               created_at="2026-09-08T00:00:00Z", note_id="n1"),),
        engine_first=True,
    )
    html = render_wiki(merged)
    assert "engine-first" in html or "FR-C1" in html  # provenance banner (BR-W5)
    assert "엔진 자동 생성" in html
    assert "에이전트 작성" in html
    assert "deep note" in html
    # engine section precedes notes section when engine_first
    assert html.index("badge engine") < html.index("badge note")


# --- WebApp dispatch over real services -------------------------------
@pytest.fixture()
def app(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "a.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
    (proj / "README.md").write_text("# Proj\n", encoding="utf-8")
    store = FileSystemKnowledgeStore(str(tmp_path / "kb"))
    source = FileSystemSource(str(proj))
    SyncService(source, default_registry(), store).run(str(proj), mode="full")
    UpdateService(store).apply_note(
        AgentNotePayload(target="a.py", body_md="agent note", author="ag",
                         created_at="2026-09-08T00:00:00Z")
    )
    return WebApp(KnowledgeReadService(store))


def test_app_index_and_static(app):
    idx = app.handle("/")
    assert idx.status == 200 and "Project Structure" in idx.body
    css = app.handle("/static/style.css")
    assert css.status == 200 and css.content_type.startswith("text/css")


def test_app_summary_ok_and_missing(app):
    ok = app.handle("/summary/a.py")
    assert ok.status == 200 and "agent note" in ok.body
    missing = app.handle("/summary/nope.py")
    assert missing.status == 404 and "Not Found" in missing.body


def test_app_graph(app):
    res = app.handle("/graph")
    assert res.status == 200 and "Dependency Graph" in res.body


def test_app_unknown_route(app):
    res = app.handle("/totally/unknown")
    assert res.status == 404
