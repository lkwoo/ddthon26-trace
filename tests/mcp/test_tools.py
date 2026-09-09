"""PBT-10 tests for the self-describing MCP tool registry (FR-6, US-9.1)."""

from pathlib import Path

import pytest

from knowledge_store.mcp.tools import build_registry
from knowledge_store.services import KnowledgeSystem
from knowledge_store.types import Status


@pytest.fixture()
def registry(tmp_path: Path):
    sys = KnowledgeSystem(tmp_path)
    yield build_registry(sys)
    sys.close()


def test_manifest_is_self_describing(registry):
    manifest = registry.manifest()
    names = {t["name"] for t in manifest}
    assert {"ingest", "semantic_query", "smart_snippet", "read_structure"} <= names
    for tool in manifest:
        assert tool["description"]
        assert tool["when_to_use"]
        assert tool["inputSchema"]["type"] == "object"


def test_unknown_tool_returns_typed_not_found(registry):
    result = registry.call("does_not_exist", {})
    assert result.status == Status.NOT_FOUND


def test_missing_required_arg_is_typed_error(registry):
    result = registry.call("semantic_query", {})
    assert result.status == Status.ERROR


def test_read_structure_on_empty_store(registry):
    result = registry.call("read_structure", {})
    assert result.status == Status.OK
    assert result.data["nodes"] == []


def test_result_serializes_to_json(registry):
    result = registry.call("read_structure", {})
    payload = result.to_json()
    assert isinstance(payload, str) and payload.startswith("{")
