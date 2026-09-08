"""Composition Root — the single place that binds concrete implementations.

``assemble`` wires U1 outbound adapters + application services and U2/U3 inbound
adapters into an :class:`AssembledApp`. Everything else depends only on ports
(BR-CA1, NFR-U4-M1).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .adapters.inbound.mcp.server import ProviderBundle
from .adapters.inbound.web.app import WebApp
from .adapters.outbound.filesystem_source import FileSystemSource
from .adapters.outbound.filesystem_store import FileSystemKnowledgeStore
from .adapters.outbound.parsers import default_registry
from .application.query_service import QueryService
from .application.read_service import KnowledgeReadService
from .application.snippet_service import SnippetService
from .application.sync_service import SyncService
from .application.update_service import UpdateService


@dataclass(frozen=True)
class AppConfig:
    project_root: str = "."
    store_dir: str = ".agentic_kb"
    host: str = "127.0.0.1"
    port: int = 8080

    @classmethod
    def from_args(cls, args) -> "AppConfig":
        return cls(
            project_root=os.path.abspath(getattr(args, "project", ".") or "."),
            store_dir=getattr(args, "store", ".agentic_kb") or ".agentic_kb",
            host=getattr(args, "host", "127.0.0.1") or "127.0.0.1",
            port=int(getattr(args, "port", 8080) or 8080),
        )


@dataclass(frozen=True)
class AssembledApp:
    config: AppConfig
    sync: SyncService
    read: KnowledgeReadService
    query: QueryService
    snippet: SnippetService
    update: UpdateService
    mcp_bundle: ProviderBundle
    web_app: WebApp


def assemble(config: AppConfig) -> AssembledApp:
    """Bind concrete adapters/services for ``config`` (Composition Root)."""
    store = FileSystemKnowledgeStore(config.store_dir)
    source = FileSystemSource(config.project_root)
    registry = default_registry()

    sync = SyncService(source, registry, store)
    read = KnowledgeReadService(store)
    query = QueryService(store)
    snippet = SnippetService(store, source)
    update = UpdateService(store)

    mcp_bundle = ProviderBundle.from_services(
        read=read, query=query, snippet=snippet, update=update, sync=sync
    )
    web_app = WebApp(read)

    return AssembledApp(
        config=config,
        sync=sync,
        read=read,
        query=query,
        snippet=snippet,
        update=update,
        mcp_bundle=mcp_bundle,
        web_app=web_app,
    )
