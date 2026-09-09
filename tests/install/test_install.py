"""PBT-10 tests for the installer (Epic 8, US-8.2/8.3, NFR-4)."""

import json
from pathlib import Path

from knowledge_store.install import InstallService, manual_snippet
from knowledge_store.store import DEFAULT_STORE_DIRNAME
from knowledge_store.types import Status


def test_install_initializes_isolated_store(tmp_path: Path):
    report = InstallService().run(str(tmp_path))
    assert report.status == Status.OK
    assert (tmp_path / DEFAULT_STORE_DIRNAME).exists()


def test_no_client_detected_yields_manual_snippet(tmp_path: Path):
    report = InstallService().run(str(tmp_path))
    assert report.configured_clients == []
    assert report.manual_snippet
    parsed = json.loads(report.manual_snippet)
    assert "knowledge-store" in parsed["mcpServers"]


def test_detects_and_configures_claude(tmp_path: Path):
    (tmp_path / ".mcp.json").write_text("{}", encoding="utf-8")
    report = InstallService().run(str(tmp_path))
    assert "claude-code" in report.configured_clients
    cfg = json.loads((tmp_path / ".mcp.json").read_text(encoding="utf-8"))
    assert cfg["mcpServers"]["knowledge-store"]["command"] == "knowledge-store-mcp"


def test_configure_preserves_existing_entries(tmp_path: Path):
    (tmp_path / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"other": {"command": "x"}}}), encoding="utf-8")
    InstallService().run(str(tmp_path))
    cfg = json.loads((tmp_path / ".mcp.json").read_text(encoding="utf-8"))
    assert "other" in cfg["mcpServers"]
    assert "knowledge-store" in cfg["mcpServers"]


def test_manual_snippet_is_valid_json():
    parsed = json.loads(manual_snippet("/some/target"))
    assert parsed["mcpServers"]["knowledge-store"]["env"]["KNOWLEDGE_STORE_TARGET"] == "/some/target"
