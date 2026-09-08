"""FileSystemKnowledgeStore — file-based KnowledgeStorePort (US-E4, US-N5).

Layout (under ``base_dir``, default ``.agentic_kb/``):

    structure.json          engine structure tree
    graph.json              engine relationship graph
    manifest.json           {path: sha} skip-cache (US-N7)
    summaries/<slug>.json   engine ModuleSummary (source of truth, round-trip)
    summaries/<slug>.md     human-readable rendering
    notes/<tslug>/<n>.json  agent notes (separate namespace, preserved, BR-9)

All JSON is written deterministically (sorted-key, stable order) for Git-friendly
diffs (US-E4 AC-2, US-N5 AC-2). Missing targets return None/empty (BR-13).
"""

from __future__ import annotations

import hashlib
import json
import os
import re

from ...domain.models import (
    AgentNote,
    ModuleSummary,
    RelationshipGraph,
    StructureTree,
)
from ...ports.store_port import KnowledgeStorePort

_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(target: str) -> str:
    base = _SLUG_RE.sub("_", target).strip("_")[:60]
    digest = hashlib.sha1(target.encode("utf-8")).hexdigest()[:8]
    return f"{base}.{digest}" if base else digest


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


class FileSystemKnowledgeStore(KnowledgeStorePort):
    def __init__(self, base_dir: str = ".agentic_kb") -> None:
        self._base = os.path.abspath(base_dir)
        self._summaries = os.path.join(self._base, "summaries")
        self._notes = os.path.join(self._base, "notes")

    # --- engine artifacts ---
    def save_structure(self, tree: StructureTree) -> None:
        self._write(os.path.join(self._base, "structure.json"), _dumps(tree.to_dict()))

    def load_structure(self) -> StructureTree | None:
        data = self._read_json(os.path.join(self._base, "structure.json"))
        return StructureTree.from_dict(data) if data is not None else None

    def save_graph(self, graph: RelationshipGraph) -> None:
        self._write(os.path.join(self._base, "graph.json"), _dumps(graph.to_dict()))

    def load_graph(self) -> RelationshipGraph | None:
        data = self._read_json(os.path.join(self._base, "graph.json"))
        return RelationshipGraph.from_dict(data) if data is not None else None

    def save_summary(self, summary: ModuleSummary) -> None:
        slug = _slug(summary.target)
        self._write(os.path.join(self._summaries, f"{slug}.json"), _dumps(summary.to_dict()))
        self._write(os.path.join(self._summaries, f"{slug}.md"), _render_summary_md(summary))

    def load_summary(self, target: str) -> ModuleSummary | None:
        data = self._read_json(os.path.join(self._summaries, f"{_slug(target)}.json"))
        return ModuleSummary.from_dict(data) if data is not None else None

    def all_summaries(self) -> list[ModuleSummary]:
        out: list[ModuleSummary] = []
        if not os.path.isdir(self._summaries):
            return out
        for fname in sorted(os.listdir(self._summaries)):
            if fname.endswith(".json"):
                data = self._read_json(os.path.join(self._summaries, fname))
                if data is not None:
                    out.append(ModuleSummary.from_dict(data))
        return out

    # --- agent notes (separate namespace) ---
    def save_agent_note(self, note: AgentNote) -> None:
        tdir = os.path.join(self._notes, _slug(note.target))
        self._write(os.path.join(tdir, f"{_slug(note.note_id)}.json"), _dumps(note.to_dict()))

    def load_agent_notes(self, target: str) -> list[AgentNote]:
        tdir = os.path.join(self._notes, _slug(target))
        if not os.path.isdir(tdir):
            return []
        notes: list[AgentNote] = []
        for fname in sorted(os.listdir(tdir)):
            if fname.endswith(".json"):
                data = self._read_json(os.path.join(tdir, fname))
                if data is not None:
                    notes.append(AgentNote.from_dict(data))
        notes.sort(key=lambda n: n.created_at)
        return notes

    # --- sha skip-cache ---
    def save_manifest(self, path_to_sha: dict[str, str]) -> None:
        self._write(os.path.join(self._base, "manifest.json"), _dumps(path_to_sha))

    def load_manifest(self) -> dict[str, str]:
        return self._read_json(os.path.join(self._base, "manifest.json")) or {}

    def get_stored_sha(self, path: str) -> str | None:
        return self.load_manifest().get(path)

    def exists(self, target: str) -> bool:
        return os.path.exists(os.path.join(self._summaries, f"{_slug(target)}.json"))

    # --- helpers ---
    @staticmethod
    def _write(path: str, text: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    @staticmethod
    def _read_json(path: str):
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)


def _render_summary_md(s: ModuleSummary) -> str:
    lines = [f"# {s.target}", ""]
    if s.headings:
        lines += ["## Headings", *[f"- {h}" for h in s.headings], ""]
    if s.signatures:
        lines += ["## Signatures", *[f"- `{sig}`" for sig in s.signatures], ""]
    if s.docstrings:
        lines += ["## Docstrings", *[f"> {d}" for d in s.docstrings], ""]
    if s.comments:
        lines += ["## Comments", *[f"- {c}" for c in s.comments], ""]
    return "\n".join(lines) + "\n"
