"""PBT-10 tests for the static wiki export (U7, US-7.4, NFR-2.1).

Verifies the static-export contract end-to-end: after ingest, the exporter
writes valid JSON data files and copies the viewer assets so the human D3
viewer loads over file:// without a server.
"""

import json
from pathlib import Path

import pytest

from knowledge_store.services import IngestionService, KnowledgeSystem, WikiExportService
from knowledge_store.types import Status


@pytest.fixture()
def system(tmp_path: Path):
    sys = KnowledgeSystem(tmp_path)
    yield sys
    sys.close()


def test_export_writes_data_and_assets(system, tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "app.py").write_text(
        "class Service:\n    def run(self):\n        helper()\n\ndef helper():\n    return 1\n",
        encoding="utf-8")
    (proj / "notes.md").write_text("# Notes\nSee [[app]].\n#topic\n", encoding="utf-8")
    IngestionService(system).ingest([str(proj / "app.py"), str(proj / "notes.md")], export=False)

    out = tmp_path / "wiki_out"
    result = WikiExportService(system).regenerate(export_dir=out)
    assert result.status == Status.OK

    for name in ("structure.json", "relationships.json", "wiki.json"):
        p = out / name
        assert p.exists(), f"missing {name}"
        json.loads(p.read_text(encoding="utf-8"))  # valid JSON

    # viewer assets copied for file:// loading
    assert (out / "index.html").exists()
    assert (out / "app.js").exists()


def test_structure_json_contains_code_nodes(system, tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "m.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    IngestionService(system).ingest([str(proj / "m.py")], export=False)

    out = tmp_path / "wiki_out"
    WikiExportService(system).regenerate(export_dir=out)
    structure = json.loads((out / "structure.json").read_text(encoding="utf-8"))
    names = {n["name"] for n in structure["nodes"]}
    assert "alpha" in names
