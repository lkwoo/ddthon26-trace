"""StdioServer — thin binding of U2 providers to the official ``mcp`` SDK.

This is the only module that imports ``mcp`` (Humble Object, NFR-U2-M1). The
import is deferred to :meth:`StdioServer.run` so the package can be imported and
unit-tested without the optional ``mcp`` dependency installed. Providers are
constructed from U1 services by the U4 assembly root (``config.py``).
"""

from __future__ import annotations

from dataclasses import dataclass

from ....application.query_service import QueryService
from ....application.read_service import KnowledgeReadService
from ....application.snippet_service import SnippetService
from ....application.sync_service import SyncService
from ....application.update_service import UpdateService
from .prompts import PromptNotFound, PromptsProvider
from .resources import ResourceNotFound, ResourcesProvider
from .tools import ToolsProvider


@dataclass(frozen=True)
class ProviderBundle:
    """Group of SDK-independent providers, ready to bind to a transport."""

    resources: ResourcesProvider
    tools: ToolsProvider
    prompts: PromptsProvider

    @classmethod
    def from_services(
        cls,
        *,
        read: KnowledgeReadService,
        query: QueryService,
        snippet: SnippetService,
        update: UpdateService,
        sync: SyncService,
    ) -> "ProviderBundle":
        return cls(
            resources=ResourcesProvider(read),
            tools=ToolsProvider(query, snippet, update, sync),
            prompts=PromptsProvider(),
        )


class StdioServer:
    """Binds a :class:`ProviderBundle` to the ``mcp`` stdio transport."""

    SERVER_NAME = "agentic-kb"

    def __init__(self, providers: ProviderBundle) -> None:
        self._providers = providers

    def run(self) -> None:  # pragma: no cover - requires mcp SDK + live stdio
        """Start the stdio MCP server (US-A6). Requires the ``[mcp]`` extra."""
        try:
            import anyio
            import mcp.types as types
            from mcp.server.lowlevel import Server
            from mcp.server.stdio import stdio_server
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError(
                "MCP support requires the optional dependency: pip install 'agentic-kb[mcp]'"
            ) from exc

        server = Server(self.SERVER_NAME)
        p = self._providers

        @server.list_resources()
        async def list_resources():
            return [
                types.Resource(uri=uri, name=uri)
                for uri in p.resources.list_uris()
            ]

        @server.read_resource()
        async def read_resource(uri: str):
            try:
                payload = p.resources.resolve(str(uri))
            except ResourceNotFound:
                raise ValueError(f"resource not found: {uri}")
            import json

            return json.dumps(payload, sort_keys=True, indent=2)

        @server.list_tools()
        async def list_tools():
            return [
                types.Tool(name=name, inputSchema={"type": "object"})
                for name in p.tools.list_tools()
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            result = p.tools.dispatch(name, arguments or {})
            import json

            return [types.TextContent(type="text", text=json.dumps(result.to_dict(), sort_keys=True))]

        @server.list_prompts()
        async def list_prompts():
            return [types.Prompt(name=name) for name in p.prompts.list_prompts()]

        @server.get_prompt()
        async def get_prompt(name: str, arguments: dict | None):
            try:
                text = p.prompts.render(name, arguments)
            except PromptNotFound:
                raise ValueError(f"prompt not found: {name}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=text),
                    )
                ]
            )

        async def _main() -> None:
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream, write_stream, server.create_initialization_options()
                )

        anyio.run(_main)
