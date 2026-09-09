"""U8 — Installer & Packaging.

Copy-style install: initialize the isolated ``.knowledge-store/`` and
auto-configure detected MCP clients (Claude Code / opencode), with a README
manual-config fallback (Epic 8, NFR-4).
"""

from knowledge_store.install.service import InstallService, manual_snippet

__all__ = ["InstallService", "manual_snippet"]
