"""UOW-05 MCP 어댑터 테스트 — 도구/리소스 등록 + stdio 디스패치 (mcp 2.x).

mcp 패키지가 없으면 스킵한다(코어 로직은 mcp 비의존).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("mcp.server.mcpserver")

DEMO = Path(__file__).resolve().parents[1] / "demo"
REPLAY = DEMO / "replay"


@pytest.fixture()
def replay_env(tmp_path, monkeypatch):
    monkeypatch.setenv("TRACE_LLM_BACKEND", "replay")
    monkeypatch.setenv("TRACE_REPLAY_DIR", str(REPLAY))
    monkeypatch.setenv("TRACE_HOME", str(tmp_path))
    from traceki.mcp_server import build_server

    return build_server()


def _payload(call_result) -> dict:
    """CallToolResult에서 도구가 반환한 JSON dict를 꺼낸다."""
    if call_result.structured_content:
        return call_result.structured_content
    return json.loads(call_result.content[0].text)


def test_core_tools_registered(replay_env):
    tools = asyncio.run(replay_env.list_tools())
    names = {t.name for t in tools}
    assert names == {
        "analyze_project",
        "list_features",
        "get_feature_knowledge",
        "get_conflicts",
        "analyze_task_impact",
        "generate_onboarding_map",
    }


def test_knowledge_resources_exposed(replay_env):
    resources = asyncio.run(replay_env.list_resources())
    templates = asyncio.run(replay_env.list_resource_templates())
    assert any(str(r.uri) == "trace://features" for r in resources)
    assert any(str(r.uri) == "trace://overview" for r in resources)
    assert any("trace://feature/" in t.uri_template for t in templates)


def test_onboarding_map_tool_dispatch(replay_env):
    result = _payload(
        asyncio.run(replay_env.call_tool("generate_onboarding_map", {"path": str(DEMO), "refresh": True}))
    )
    assert result["meta"]["ok"] is True
    assert result["data"]["entry_points"]
    assert result["data"]["mermaid"]["dependency"].startswith("flowchart LR")


def test_tool_dispatch_hero_flow(replay_env):
    async def flow():
        await replay_env.call_tool("analyze_project", {"path": str(DEMO), "refresh": True})
        conflicts = _payload(await replay_env.call_tool("get_conflicts", {}))
        impact = _payload(
            await replay_env.call_tool(
                "analyze_task_impact", {"task": "Add SMS verification to Owner registration"}
            )
        )
        return conflicts, impact

    conflicts, impact = asyncio.run(flow())
    # 충돌 도구는 Hero value_mismatch를 노출
    assert conflicts["meta"]["conflicts_count"] == 1
    assert conflicts["conflicts"][0]["claim"] == "Owner.telephone.max_length"
    # 결과 봉투 키 순서 (summary 우선, NFR-MCP-UX-002)
    assert list(conflicts.keys())[0] == "summary"
    # 영향 도구는 must_change + change_plan 노출
    assert impact["impact"]["must_change"]
    assert impact["impact"]["change_plan"]


def test_feature_resource_reads_markdown(replay_env):
    async def flow():
        await replay_env.call_tool("analyze_project", {"path": str(DEMO), "refresh": True})
        return await replay_env.read_resource("trace://feature/owner-registration")

    content = asyncio.run(flow())
    text = content if isinstance(content, str) else content[0].content
    assert "Owner Registration" in str(text)
