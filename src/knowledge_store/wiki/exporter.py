"""WikiExporter — generate the static export artifacts for the Web Viewer.

Writes JSON data files (structure/graph, relationships, wiki content) plus a
copy of the static viewer into ``<store>/wiki/`` so reviewers always see the
latest chunk versions (US-7.4, NFR-2.1). No runtime server is required.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path

from knowledge_store.store.repositories import Repositories
from knowledge_store.types import ExportResult, Status

_VIEWER_SRC = Path(__file__).resolve().parent.parent.parent / "viewer"


class WikiExporter:
    def __init__(self, repos: Repositories) -> None:
        self._repos = repos

    def export(self, export_dir: str | Path) -> ExportResult:
        out = Path(export_dir)
        out.mkdir(parents=True, exist_ok=True)
        written: list[str] = []

        written.append(self._write_json(out / "structure.json", self._structure()))
        written.append(self._write_json(out / "relationships.json", self._relationships()))
        written.append(self._write_json(out / "wiki.json", self._wiki()))

        # Copy the static viewer next to the data so it loads via file://.
        if _VIEWER_SRC.exists():
            for asset in _VIEWER_SRC.iterdir():
                if asset.is_file():
                    shutil.copy2(asset, out / asset.name)
                    written.append(str(out / asset.name))

        return ExportResult(status=Status.OK, export_dir=str(out), files_written=written)

    # -- data builders -----------------------------------------------------
    def _structure(self) -> dict:
        nodes = [asdict(n) | {"kind_type": n.kind} for n in self._repos.graph.nodes()]
        edges = [{"src": e.src, "dst": e.dst, "type": e.type.value, "resolved": e.resolved}
                 for e in self._repos.graph.edges()]
        return {"nodes": [self._node_json(n) for n in self._repos.graph.nodes()],
                "edges": edges}

    @staticmethod
    def _node_json(node) -> dict:
        return {"id": node.id, "name": node.name, "kind": node.kind,
                "path": node.path, "language": node.language}

    def _relationships(self) -> dict:
        return {"relationships": [
            {"src": r.src_id, "dst": r.dst_id, "type": r.type.value,
             "score": r.score, "resolved": r.resolved}
            for r in self._repos.relationships.all()
        ]}

    def _wiki(self) -> dict:
        summaries = {s.chunk_id: s.text for s in self._repos.summaries.all()}
        entries = []
        for chunk in self._repos.chunks.all_latest():
            entries.append({
                "id": chunk.id,
                "source_path": chunk.source_path,
                "kind": chunk.kind,
                "ordinal": chunk.ordinal,
                "tags": list(chunk.tags),
                "latest_version": self._repos.chunks.latest_version(chunk.id),
                "text": chunk.text,
                "summary": summaries.get(chunk.id, ""),
            })
        return {"entries": entries}

    @staticmethod
    def _write_json(path: Path, data: dict) -> str:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
