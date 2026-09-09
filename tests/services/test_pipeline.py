"""PBT-10 end-to-end pipeline tests through the orchestrator services.

Exercises ingest -> chunk -> version -> graph -> embed -> relate -> query and the
agent-driven summarization contract (server never authors summaries, FR-5).
"""

from pathlib import Path

import pytest

from knowledge_store.services import (
    IngestionService,
    KnowledgeSystem,
    QueryService,
    SummarizationService,
)
from knowledge_store.types import Status


@pytest.fixture()
def system(tmp_path: Path):
    sys = KnowledgeSystem(tmp_path)
    yield sys
    sys.close()


def _write_project(root: Path) -> list[str]:
    (root / "notes.md").write_text(
        "# Auth\nThe auth module handles login. See [[users]].\n#security\n", encoding="utf-8")
    (root / "users.md").write_text("# Users\nUser records.\n#security\n", encoding="utf-8")
    (root / "app.py").write_text(
        "class Service:\n    def run(self):\n        helper()\n\ndef helper():\n    return 1\n",
        encoding="utf-8")
    return [str(root / "notes.md"), str(root / "users.md"), str(root / "app.py")]


def test_full_ingest_and_query(system, tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    paths = _write_project(proj)

    report = IngestionService(system).ingest(paths, export=False)
    assert report.status == Status.OK
    assert report.ingested_files == 3
    assert report.chunks_new > 0

    query = QueryService(system)
    hits = query.semantic_query("login authentication", limit=5)
    assert isinstance(hits, list)

    structure = query.read_structure()
    node_names = {n["name"] for n in structure["nodes"]}
    assert {"Service", "helper"} <= node_names


def test_unsupported_and_missing_files_are_reported(system, tmp_path: Path):
    missing = str(tmp_path / "nope.md")
    weird = tmp_path / "x.heic"
    weird.write_bytes(b"\x00")
    report = IngestionService(system).ingest([missing, str(weird)], export=False)
    assert report.ingested_files == 0
    assert any("nope.md" in u for u in report.unsupported)
    assert any("x.heic" in u for u in report.unsupported)


def test_directory_is_walked_recursively(system, tmp_path: Path):
    proj = tmp_path / "proj"
    (proj / "sub").mkdir(parents=True)
    (proj / "top.md").write_text("# Top\nTop level note.\n", encoding="utf-8")
    (proj / "sub" / "nested.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (proj / "sub" / "schema.sql").write_text("CREATE TABLE t (id INT);\n", encoding="utf-8")
    # hidden dirs are skipped
    (proj / ".git").mkdir()
    (proj / ".git" / "config.md").write_text("# hidden\nshould be ignored\n", encoding="utf-8")
    # unsupported files under a directory are skipped silently (not reported)
    (proj / "sub" / "image.heic").write_bytes(b"\x00")

    report = IngestionService(system).ingest([str(proj)], export=False)
    assert report.status == Status.OK
    assert report.ingested_files == 3  # top.md, nested.py, schema.sql
    assert report.unsupported == []


def test_reingest_bumps_version_not_duplicate(system, tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    note = proj / "n.md"
    note.write_text("# A\nStable paragraph content here.\n", encoding="utf-8")
    svc = IngestionService(system)

    first = svc.ingest([str(note)], export=False)
    assert first.chunks_new >= 1

    second = svc.ingest([str(note)], export=False)
    # identical content matches -> updated, not a brand-new chunk
    assert second.chunks_updated >= 1
    assert second.chunks_new == 0


def test_summarization_is_agent_driven(system, tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    note = proj / "n.md"
    note.write_text("# Topic\nSome content to summarize.\n", encoding="utf-8")
    IngestionService(system).ingest([str(note)], export=False)

    summarize = SummarizationService(system)
    pending = system.summary_store.pending()
    assert pending, "expected chunks awaiting summaries"

    # pending() yields chunk ids awaiting a summary.
    chunk_id = pending[0]
    content = summarize.get_content_to_summarize(chunk_id)
    assert content is not None

    assert summarize.store_summary(chunk_id, "A concise agent summary.") == Status.OK
    stored = summarize.get_summary(chunk_id)
    assert stored is not None and "concise" in stored.text
