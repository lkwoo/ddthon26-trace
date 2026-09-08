"""adapters/inbound/mcp — U2 MCP Server (thin inbound adapter over U1 services).

Providers (resources/tools/prompts) are SDK-independent pure mappings; only
``server`` binds the official ``mcp`` SDK.
"""

from .prompts import PromptNotFound, PromptsProvider
from .resources import ResourceNotFound, ResourcesProvider
from .server import ProviderBundle, StdioServer
from .tools import TOOL_NAMES, ToolResult, ToolsProvider

__all__ = [
    "ResourcesProvider",
    "ResourceNotFound",
    "ToolsProvider",
    "ToolResult",
    "TOOL_NAMES",
    "PromptsProvider",
    "PromptNotFound",
    "ProviderBundle",
    "StdioServer",
]
