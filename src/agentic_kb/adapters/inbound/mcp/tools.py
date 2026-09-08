"""ToolsProvider — dispatches MCP tool calls to U1 application services.

SDK-independent pure mapping. Argument-shape validation happens here (BR-M6);
final payload validation for notes lives in U1 ``UpdateService`` (BR-21). All
handler bodies are wrapped in ``measure`` for surface latency (US-N1). Any
lower-level exception is translated into an ``isError`` result so a single bad
call never terminates the server (BR-M8).
"""

from __future__ import annotations

from dataclasses import dataclass

from ....application.measurement import measure
from ....application.payloads import AgentNotePayload
from ....application.query_service import QueryService
from ....application.snippet_service import SnippetService
from ....application.sync_service import SyncService
from ....application.update_service import UpdateService


@dataclass(frozen=True)
class ToolResult:
    """Structured tool result. ``is_error`` carries validation/runtime failures."""

    content: dict
    is_error: bool = False

    def to_dict(self) -> dict:
        return {"isError": self.is_error, "content": self.content}


TOOL_NAMES = ("query", "snippet", "update_note", "sync")


class ToolsProvider:
    def __init__(
        self,
        query: QueryService,
        snippet: SnippetService,
        update: UpdateService,
        sync: SyncService,
    ) -> None:
        self._query = query
        self._snippet = snippet
        self._update = update
        self._sync = sync

    def list_tools(self) -> list[str]:
        return list(TOOL_NAMES)

    def dispatch(self, name: str, args: dict) -> ToolResult:
        handler = {
            "query": self._do_query,
            "snippet": self._do_snippet,
            "update_note": self._do_update,
            "sync": self._do_sync,
        }.get(name)
        if handler is None:
            return ToolResult({"error": f"unknown tool: {name}"}, is_error=True)
        with measure(f"mcp.tool.{name}"):
            try:
                return handler(args)
            except (KeyError, TypeError, ValueError) as exc:
                return ToolResult({"error": str(exc)}, is_error=True)

    # --- handlers -------------------------------------------------------
    def _do_query(self, args: dict) -> ToolResult:
        query = _require_str(args, "query")
        mode = args.get("mode", "auto")
        if mode not in ("auto", "keyword", "graph"):
            return ToolResult({"error": f"invalid mode: {mode}"}, is_error=True)
        results = self._query.query(query, mode=mode)
        return ToolResult({"results": [r.to_dict() for r in results]})

    def _do_snippet(self, args: dict) -> ToolResult:
        target = _require_str(args, "target")
        budget = args.get("token_budget")
        if not isinstance(budget, int) or budget < 0:
            return ToolResult(
                {"error": "token_budget must be a non-negative integer"}, is_error=True
            )
        snip = self._snippet.snippet(target, budget)
        return ToolResult(snip.to_dict())

    def _do_update(self, args: dict) -> ToolResult:
        payload = AgentNotePayload(
            target=_require_str(args, "target"),
            body_md=_require_str(args, "body_md"),
            author=_require_str(args, "author"),
            created_at=_require_str(args, "created_at"),
        )
        result = self._update.apply_note(payload)
        return ToolResult(result.to_dict(), is_error=not result.ok)

    def _do_sync(self, args: dict) -> ToolResult:
        project_root = _require_str(args, "project_root")
        mode = args.get("mode", "resync")
        if mode not in ("full", "resync"):
            return ToolResult({"error": f"invalid mode: {mode}"}, is_error=True)
        report = self._sync.run(project_root, mode=mode)
        return ToolResult(report.to_dict())


def _require_str(args: dict, key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"missing or invalid field: {key}")
    return value
