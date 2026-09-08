"""Entry point: ``python -m agentic_kb`` / console script ``agentic-kb``.

Humble Object: parse args → build config → assemble → dispatch. Fatal errors
map to exit 1, usage errors to exit 2 (argparse), partial file failures stay 0
(reported in the sync output). (BR-CA7, NFR-U4-R1)
"""

from __future__ import annotations

import argparse
import sys

from .adapters.inbound.cli.commands import HANDLERS
from .config import AppConfig, assemble


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-kb",
        description="Agentic Knowledge Base — MCP + web viewer over a local code/doc engine.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", default=".", help="project source root (default: cwd)")
        p.add_argument("--store", default=".agentic_kb", help="knowledge base directory")

    p_ingest = sub.add_parser("ingest", help="full ingestion of a project (US-E1)")
    _add_common(p_ingest)
    p_ingest.add_argument("--json", action="store_true", help="emit SyncReport as JSON")

    p_sync = sub.add_parser("sync", help="re-sync the knowledge base (US-E5)")
    _add_common(p_sync)
    p_sync.add_argument("--full", action="store_true", help="force full re-ingestion")
    p_sync.add_argument("--json", action="store_true", help="emit SyncReport as JSON")

    p_mcp = sub.add_parser("serve-mcp", help="run the stdio MCP server (US-A6)")
    _add_common(p_mcp)

    p_web = sub.add_parser("serve-web", help="run the web viewer (US-H*)")
    _add_common(p_web)
    p_web.add_argument("--host", default="127.0.0.1", help="bind host")
    p_web.add_argument("--port", type=int, default=8080, help="bind port")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is None:  # pragma: no cover - argparse enforces choices
        parser.error(f"unknown command: {args.command}")

    try:
        config = AppConfig.from_args(args)
        app = assemble(config)
        return handler(app, args)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
