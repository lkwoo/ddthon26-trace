"""MCP stdio server entry point (thin adapter).

Runs an MCP server over stdio when the ``mcp`` package is installed, mapping
each :class:`ToolSpec` to an MCP tool. Without ``mcp`` installed, ``main`` prints
the self-describing tool manifest (JSON) so the interface is still inspectable.
"""

from __future__ import annotations

import json
import os
import sys

from knowledge_store.mcp.tools import build_registry
from knowledge_store.services.system import KnowledgeSystem


def _target_dir() -> str:
    return os.environ.get("KNOWLEDGE_STORE_TARGET", os.getcwd())


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    system = KnowledgeSystem(_target_dir())
    registry = build_registry(system)

    if "--manifest" in argv:
        print(json.dumps(registry.manifest(), ensure_ascii=False, indent=2))
        return 0

    try:
        return _run_stdio(system, registry)
    except ImportError:
        sys.stderr.write(
            "The 'mcp' package is not installed. Install with: pip install 'knowledge-store[mcp]'\n"
            "Tool manifest (for manual configuration):\n"
        )
        print(json.dumps(registry.manifest(), ensure_ascii=False, indent=2))
        return 0


def _run_stdio(system: KnowledgeSystem, registry) -> int:
    import asyncio

    from mcp.server import Server  # type: ignore
    from mcp.server.stdio import stdio_server  # type: ignore
    from mcp.types import TextContent, Tool  # type: ignore

    server = Server("knowledge-store")

    @server.list_tools()
    async def list_tools() -> list["Tool"]:
        return [
            Tool(name=spec["name"],
                 description=f"{spec['description']} When to use: {spec['when_to_use']}",
                 inputSchema=spec["inputSchema"])
            for spec in registry.manifest()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list["TextContent"]:
        result = registry.call(name, arguments or {})
        return [TextContent(type="text", text=result.to_json())]

    async def _serve() -> None:
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(_serve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
