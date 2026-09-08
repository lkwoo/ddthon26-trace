"""CLI subcommand handlers — thin delegation to the assembled app (BR-CA2).

Handlers return a process exit code. Sync/ingest print a scale+duration report
(US-N7); server commands start U2/U3 servers (BR-CA3).
"""

from __future__ import annotations

import json
import os
import sys

from ....config import AssembledApp
from ....domain.models import SyncReport


def _require_project(app: AssembledApp) -> None:
    """Fail fast on a missing project root (fatal, exit 1 via main). BR-CA7."""
    if not os.path.isdir(app.config.project_root):
        raise ValueError(f"project root not found: {app.config.project_root}")


def print_report(report: SyncReport, as_json: bool) -> None:
    """Emit sync scale/duration (US-N7, BR-CA6)."""
    if as_json:
        sys.stdout.write(json.dumps(report.to_dict(), sort_keys=True) + "\n")
        return
    sys.stdout.write(
        f"files={report.files_total} symbols={report.symbols_total} "
        f"skipped={len(report.skipped)} failures={len(report.failures)} "
        f"elapsed={report.duration_ms}ms\n"
    )
    for line in report.skipped:
        sys.stdout.write(f"  skip: {line}\n")
    for line in report.failures:
        sys.stderr.write(f"  fail: {line}\n")


def cmd_ingest(app: AssembledApp, args) -> int:
    _require_project(app)
    report = app.sync.run(app.config.project_root, mode="full")
    print_report(report, getattr(args, "json", False))
    return 0


def cmd_sync(app: AssembledApp, args) -> int:
    _require_project(app)
    mode = "full" if getattr(args, "full", False) else "resync"
    report = app.sync.run(app.config.project_root, mode=mode)
    print_report(report, getattr(args, "json", False))
    return 0


def cmd_serve_mcp(app: AssembledApp, args) -> int:  # pragma: no cover - live server
    from ..mcp.server import StdioServer

    StdioServer(app.mcp_bundle).run()
    return 0


def cmd_serve_web(app: AssembledApp, args) -> int:  # pragma: no cover - live server
    from ..web.app import WebServer

    server = WebServer(app.web_app, host=app.config.host, port=app.config.port)
    sys.stdout.write(f"serving web viewer on http://{app.config.host}:{app.config.port}\n")
    server.serve_forever()
    return 0


HANDLERS = {
    "ingest": cmd_ingest,
    "sync": cmd_sync,
    "serve-mcp": cmd_serve_mcp,
    "serve-web": cmd_serve_web,
}
