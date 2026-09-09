"""UOW-05 MCP 서버 구성 테스트 (NFR-05-IF/RUN, importorskip)."""

from __future__ import annotations

import asyncio
import inspect

import pytest

pytest.importorskip("mcp", reason="mcp SDK 미설치 시 서버 테스트 skip (코어는 무의존)")

from trace.mcp_server.server import _root, build_server  # noqa: E402


def _await(value):  # type: ignore[no-untyped-def]
    if inspect.iscoroutine(value):
        return asyncio.new_event_loop().run_until_complete(value)
    return value


def test_build_server_registers_five_tools() -> None:
    server = build_server()
    tools = _await(server.list_tools())
    names = {t.name for t in tools}
    assert names == {
        "trace_analyze_project", "trace_list_features", "trace_get_feature_knowledge",
        "trace_get_conflicts", "trace_analyze_task_impact",
    }


def test_build_server_registers_prompt() -> None:
    server = build_server()
    prompts = _await(server.list_prompts())
    assert any(p.name == "review_before_implementation" for p in prompts)


def test_root_prefers_env(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("TRACE_PROJECT_ROOT", "/custom/root")
    assert _root() == "/custom/root"
    monkeypatch.delenv("TRACE_PROJECT_ROOT", raising=False)
    assert _root() == __import__("os").getcwd()


def test_main_importable() -> None:
    from trace.mcp_server.__main__ import main
    assert callable(main)
