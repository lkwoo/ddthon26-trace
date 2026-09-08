"""ResourcesProvider — maps MCP Resource URIs to U1 read-service delegations.

SDK-independent pure mapping (Humble Object). ``server.py`` binds this to the
official ``mcp`` SDK. Unknown/missing targets raise :class:`ResourceNotFound`
so the transport layer can surface a not-found signal without crashing the
server (US-A1 AC-4, BR-M4).
"""

from __future__ import annotations

from urllib.parse import unquote

from ....application.measurement import measure
from ....application.read_service import KnowledgeReadService

SCHEME = "agentic-kb://"


class ResourceNotFound(LookupError):
    """Raised when a resource URI resolves to no stored artifact."""


class ResourcesProvider:
    """Resolve ``agentic-kb://`` URIs into serialized read results."""

    def __init__(self, read: KnowledgeReadService) -> None:
        self._read = read

    def list_uris(self) -> list[str]:
        """Static catalog of resource URI templates (US-A6 handshake listing)."""
        return [
            f"{SCHEME}structure",
            f"{SCHEME}summary/{{target}}",
            f"{SCHEME}relationships",
            f"{SCHEME}relationships/{{target}}",
        ]

    def resolve(self, uri: str) -> dict:
        """Return the ``to_dict`` payload for ``uri`` or raise ResourceNotFound."""
        kind, target = self._parse(uri)
        with measure(f"mcp.resource.{kind}"):
            if kind == "structure":
                obj = self._read.get_structure()
            elif kind == "summary":
                obj = self._read.get_summary(target) if target else None
            elif kind == "relationships":
                obj = self._read.get_relationships(target)
            else:  # pragma: no cover - guarded by _parse
                obj = None
        if obj is None:
            raise ResourceNotFound(uri)
        return obj.to_dict()

    @staticmethod
    def _parse(uri: str) -> tuple[str, str | None]:
        """Parse ``agentic-kb://<kind>[/<target>]`` (BR-M5)."""
        if not uri.startswith(SCHEME):
            raise ResourceNotFound(uri)
        rest = uri[len(SCHEME):]
        head, _, tail = rest.partition("/")
        target = unquote(tail) if tail else None
        if head == "structure":
            return "structure", None
        if head == "summary":
            if not target:
                raise ResourceNotFound(uri)
            return "summary", target
        if head == "relationships":
            return "relationships", target
        raise ResourceNotFound(uri)
