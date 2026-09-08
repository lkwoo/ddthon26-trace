"""http.server binding for the web viewer (Humble Object, NFR-U3-M1).

The pure dispatch logic lives in :func:`WebApp.handle` (testable without a live
server); :class:`_Handler` is the thin ``BaseHTTPRequestHandler`` shell. A single
request failure is isolated into a 404/error page — the server never crashes
(BR-W8).
"""

from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ....application.measurement import measure
from ....application.read_service import KnowledgeReadService
from . import rendering, routing


@dataclass(frozen=True)
class Response:
    status: int
    content_type: str
    body: str

    def encoded(self) -> bytes:
        return self.body.encode("utf-8")


class WebApp:
    """Maps HTTP paths to rendered responses by delegating to U1 read service."""

    def __init__(self, read: KnowledgeReadService) -> None:
        self._read = read

    def handle(self, path: str) -> Response:
        route = routing.match(path)
        try:
            with measure(f"web.{route.view}"):
                return self._dispatch(route)
        except Exception:  # noqa: BLE001 - isolate any failure into a page (BR-W8)
            return Response(500, "text/html; charset=utf-8",
                            rendering.render_not_found(path))

    def _dispatch(self, route: routing.Route) -> Response:
        if route.view == "static":
            return Response(200, "text/css; charset=utf-8", rendering.render_css())
        if route.view == "index":
            return Response(200, "text/html; charset=utf-8",
                            rendering.render_index(self._read.get_structure()))
        if route.view == "summary":
            merged = self._read.get_summary(route.target or "")
            if merged is None:
                return Response(404, "text/html; charset=utf-8",
                                rendering.render_not_found(route.target or ""))
            return Response(200, "text/html; charset=utf-8", rendering.render_wiki(merged))
        if route.view == "graph":
            graph = self._read.get_relationships(route.target)
            return Response(200, "text/html; charset=utf-8", rendering.render_graph(graph))
        return Response(404, "text/html; charset=utf-8",
                        rendering.render_not_found(route.target or ""))


class WebServer:
    """Binds a :class:`WebApp` to ``ThreadingHTTPServer`` (US-H*, FR-H5)."""

    def __init__(self, app: WebApp, host: str = "127.0.0.1", port: int = 8080) -> None:
        self._app = app
        self._host = host
        self._port = port

    def serve_forever(self) -> None:  # pragma: no cover - live server loop
        app = self._app

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - http.server API
                response = app.handle(self.path)
                payload = response.encoded()
                self.send_response(response.status)
                self.send_header("Content-Type", response.content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args) -> None:  # silence default stderr logging
                pass

        server = ThreadingHTTPServer((self._host, self._port), _Handler)
        server.serve_forever()
