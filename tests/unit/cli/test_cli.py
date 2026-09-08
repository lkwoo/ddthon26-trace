"""U4 CLI & Assembly tests: assemble() wiring + main(argv) exit codes/output."""

import json

import pytest

from agentic_kb.__main__ import build_parser, main
from agentic_kb.config import AppConfig, AssembledApp, assemble


@pytest.fixture()
def project(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "a.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
    (proj / "README.md").write_text("# Proj\n", encoding="utf-8")
    return proj


def _argv(cmd, proj, store, *extra):
    return [cmd, "--project", str(proj), "--store", str(store), *extra]


# --- assembly ---------------------------------------------------------
def test_assemble_wires_all_components(tmp_path, project):
    cfg = AppConfig(project_root=str(project), store_dir=str(tmp_path / "kb"))
    app = assemble(cfg)
    assert isinstance(app, AssembledApp)
    assert app.sync and app.read and app.query and app.snippet and app.update
    assert app.mcp_bundle and app.web_app


# --- parser -----------------------------------------------------------
def test_parser_requires_subcommand():
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([])
    assert exc.value.code == 2  # usage error


# --- ingest / sync ----------------------------------------------------
def test_ingest_reports_and_exit_zero(project, tmp_path, capsys):
    code = main(_argv("ingest", project, tmp_path / "kb"))
    out = capsys.readouterr().out
    assert code == 0
    assert "files=" in out and "symbols=" in out and "elapsed=" in out


def test_ingest_json_output(project, tmp_path, capsys):
    code = main(_argv("ingest", project, tmp_path / "kb", "--json"))
    out = capsys.readouterr().out
    assert code == 0
    payload = json.loads(out.strip())
    assert payload["files_total"] >= 2


def test_sync_resync_after_ingest(project, tmp_path, capsys):
    store = tmp_path / "kb"
    assert main(_argv("ingest", project, store)) == 0
    capsys.readouterr()
    assert main(_argv("sync", project, store)) == 0
    out = capsys.readouterr().out
    assert "skipped=" in out  # resync skips unchanged files


def test_fatal_error_exit_one(tmp_path, capsys):
    # nonexistent project root -> discover raises -> exit 1
    code = main(_argv("ingest", tmp_path / "does_not_exist", tmp_path / "kb"))
    err = capsys.readouterr().err
    assert code == 1 and "error:" in err
