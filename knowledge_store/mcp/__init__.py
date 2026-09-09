"""U6 — Thin MCP adapter (Application Design Q2).

Exposes the system to agents as self-describing MCP Resources + Tools over
stdio. Contains no business logic: it deserializes tool inputs, calls a service,
and serializes typed results into token-efficient envelopes.
"""

from knowledge_store.mcp.tools import ToolRegistry, ToolSpec, build_registry

__all__ = ["ToolRegistry", "ToolSpec", "build_registry"]
