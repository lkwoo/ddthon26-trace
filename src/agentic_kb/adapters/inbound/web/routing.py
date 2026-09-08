"""Table-driven router: maps a request path to a (view, target) pair.

Server-independent (no http.server import) so it is unit-testable. ``app.py``
consumes the match and dispatches to the U1 read service + renderers.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import unquote


@dataclass(frozen=True)
class Route:
    view: str
    target: str | None = None


def match(path: str) -> Route:
    """Resolve a URL path to a :class:`Route`. Unknown paths -> view ``not_found``."""
    # strip query string, normalize
    path = path.split("?", 1)[0]
    if path in ("", "/"):
        return Route("index")
    if path == "/static/style.css":
        return Route("static")
    if path.startswith("/summary/"):
        target = unquote(path[len("/summary/"):])
        if not target:
            return Route("not_found", "")
        return Route("summary", target)
    if path == "/graph":
        return Route("graph", None)
    if path.startswith("/graph/"):
        target = unquote(path[len("/graph/"):])
        return Route("graph", target or None)
    return Route("not_found", path)
