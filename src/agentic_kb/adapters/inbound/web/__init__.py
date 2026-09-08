"""adapters/inbound/web — U3 Web Viewer (SSR, stdlib-only, read-only over U1)."""

from .app import Response, WebApp, WebServer
from .routing import Route, match

__all__ = ["WebApp", "WebServer", "Response", "Route", "match"]
