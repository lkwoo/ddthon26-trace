"""Installer CLI (``knowledge-store``).

Subcommands:
  install [TARGET]   initialize the store and auto-configure detected MCP clients
  init    [TARGET]   initialize the store only
  ingest  PATH...    ingest files/directories into the store at TARGET (or cwd); directories are walked recursively
  manifest           print the self-describing MCP tool manifest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from knowledge_store.install.service import InstallService


def _cmd_install(args: argparse.Namespace) -> int:
    report = InstallService().run(args.target, init_store=not args.no_store)
    print(f"Installed into: {report.target_dir}")
    if report.store_dir:
        print(f"Knowledge store: {report.store_dir}")
    print(report.message)
    if report.manual_snippet:
        print("\nManual MCP config snippet:\n" + report.manual_snippet)
    return 0 if report.status.value == "ok" else 1


def _cmd_init(args: argparse.Namespace) -> int:
    from knowledge_store.store import KnowledgeStore

    store = KnowledgeStore(args.target)
    store.connect()
    store.init_schema()
    store.close()
    print(f"Initialized knowledge store under: {args.target}")
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    from knowledge_store.services import IngestionService, KnowledgeSystem

    system = KnowledgeSystem(args.target)
    report = IngestionService(system).ingest(args.paths)
    print(json.dumps({
        "status": report.status.value,
        "ingested_files": report.ingested_files,
        "chunks_new": report.chunks_new,
        "chunks_updated": report.chunks_updated,
        "unsupported": report.unsupported,
        "pending_summaries": len(report.pending_summaries),
    }, indent=2))
    system.close()
    return 0


def _cmd_manifest(args: argparse.Namespace) -> int:
    from knowledge_store.mcp.tools import build_registry
    from knowledge_store.services import KnowledgeSystem

    system = KnowledgeSystem(args.target, in_memory=True)
    print(json.dumps(build_registry(system).manifest(), indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="knowledge-store",
                                     description="Dual-Interface Knowledge Store")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="init store + auto-configure MCP clients")
    p_install.add_argument("target", nargs="?", default=os.getcwd())
    p_install.add_argument("--no-store", action="store_true", help="skip store initialization")
    p_install.set_defaults(func=_cmd_install)

    p_init = sub.add_parser("init", help="initialize the knowledge store only")
    p_init.add_argument("target", nargs="?", default=os.getcwd())
    p_init.set_defaults(func=_cmd_init)

    p_ingest = sub.add_parser("ingest", help="ingest files/directories into the store")
    p_ingest.add_argument("paths", nargs="+",
                          help="files or directories (directories are walked recursively)")
    p_ingest.add_argument("--target", default=os.getcwd())
    p_ingest.set_defaults(func=_cmd_ingest)

    p_manifest = sub.add_parser("manifest", help="print the MCP tool manifest")
    p_manifest.add_argument("--target", default=os.getcwd())
    p_manifest.set_defaults(func=_cmd_manifest)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
