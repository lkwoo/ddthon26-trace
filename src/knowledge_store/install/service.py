"""InstallService — initialize the store and auto-configure MCP clients (Epic 8).

Deterministic, dependency-light. Detects Claude Code (``.mcp.json`` / ``.claude``)
and opencode (``opencode.json`` / ``.opencode``) in the target project and adds a
stdio MCP server entry; if none is detected it returns a manual snippet for the
README (US-8.3). Data is isolated in ``<target>/.knowledge-store/`` (US-8.2).
"""

from __future__ import annotations

import json
from pathlib import Path

from knowledge_store.store import DEFAULT_STORE_DIRNAME, KnowledgeStore
from knowledge_store.types import InstallReport, Status

_MCP_COMMAND = "knowledge-store-mcp"


def _server_entry(target: str) -> dict:
    return {"command": _MCP_COMMAND, "args": [],
            "env": {"KNOWLEDGE_STORE_TARGET": target}}


def manual_snippet(target: str) -> str:
    """Manual MCP config snippet for the README fallback (US-8.3/US-8.4)."""
    return json.dumps({"mcpServers": {"knowledge-store": _server_entry(target)}}, indent=2)


class InstallService:
    def run(self, target_dir: str, *, init_store: bool = True) -> InstallReport:
        target = Path(target_dir).resolve()
        target.mkdir(parents=True, exist_ok=True)
        report = InstallReport(status=Status.OK, target_dir=str(target))

        # 1) initialize isolated knowledge store (US-8.2)
        if init_store:
            store = KnowledgeStore(target)
            store.connect()
            store.init_schema()
            store.close()
            report.store_dir = str(target / DEFAULT_STORE_DIRNAME)

        # 2) detect + configure MCP clients (US-8.3)
        configured: list[str] = []
        if self._is_claude(target):
            self._configure_claude(target)
            configured.append("claude-code")
        if self._is_opencode(target):
            self._configure_opencode(target)
            configured.append("opencode")

        report.configured_clients = configured
        if not configured:
            report.manual_snippet = manual_snippet(str(target))
            report.message = ("No MCP client detected; add the manual snippet to your "
                              "client config (see README).")
        else:
            report.message = f"Configured MCP clients: {', '.join(configured)}"
        return report

    # -- detection ---------------------------------------------------------
    @staticmethod
    def _is_claude(target: Path) -> bool:
        return (target / ".mcp.json").exists() or (target / ".claude").exists()

    @staticmethod
    def _is_opencode(target: Path) -> bool:
        return any((target / n).exists() for n in ("opencode.json", ".opencode.json", ".opencode"))

    # -- configuration (merge, never clobber unrelated entries) ------------
    def _configure_claude(self, target: Path) -> None:
        path = target / ".mcp.json"
        data = self._load(path)
        servers = data.setdefault("mcpServers", {})
        servers["knowledge-store"] = _server_entry(str(target))
        self._save(path, data)

    def _configure_opencode(self, target: Path) -> None:
        path = target / "opencode.json"
        if not path.exists():
            for alt in (".opencode.json",):
                if (target / alt).exists():
                    path = target / alt
                    break
        data = self._load(path)
        mcp = data.setdefault("mcp", {})
        mcp["knowledge-store"] = {"type": "local", "command": [_MCP_COMMAND],
                                  "environment": {"KNOWLEDGE_STORE_TARGET": str(target)}}
        self._save(path, data)

    @staticmethod
    def _load(path: Path) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    @staticmethod
    def _save(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
