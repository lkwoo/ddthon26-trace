"""SyncService — ingestion/re-sync pipeline orchestration (US-E1, US-E2, US-E5).

Coordinates discover -> parse -> graph/extract -> persist. Isolates per-file
failures (BR-3), skips unchanged files in resync via sha (BR-12), preserves agent
notes (BR-9), and reports scale/duration (US-N7).
"""

from __future__ import annotations

import time

from ..domain import graph_builder
from ..domain.extractor import extract
from ..domain.models import ParsedUnit, SyncReport
from ..domain.structure import build_structure_tree
from ..ports.parser_port import LanguageParserPort
from ..ports.source_port import FileSourcePort, SourceFilter
from ..ports.store_port import KnowledgeStorePort
from .measurement import measure


class ParserRegistryProtocol:
    """Structural type: anything with for_file / supported_extensions."""

    def for_file(self, path: str) -> LanguageParserPort | None: ...  # pragma: no cover
    def supported_extensions(self) -> set[str]: ...  # pragma: no cover


class SyncService:
    def __init__(
        self,
        source: FileSourcePort,
        registry: ParserRegistryProtocol,
        store: KnowledgeStorePort,
    ) -> None:
        self._source = source
        self._registry = registry
        self._store = store

    def run(self, project_root: str, mode: str = "full") -> SyncReport:
        with measure(f"sync.{mode}"):
            return self._run(project_root, mode)

    def _run(self, project_root: str, mode: str) -> SyncReport:
        t0 = time.perf_counter()
        skipped: list[str] = []
        failures: list[str] = []

        filters = SourceFilter(extensions=frozenset(self._registry.supported_extensions()))
        files = self._source.discover(project_root, filters)

        stored_manifest = getattr(self._store, "load_manifest", lambda: {})()
        new_manifest: dict[str, str] = {}
        units: list[ParsedUnit] = []
        symbols_total = 0

        for f in sorted(files, key=lambda x: x.path):
            new_manifest[f.path] = f.sha
            if mode == "resync" and stored_manifest.get(f.path) == f.sha and self._store.exists(f.path):
                skipped.append(f"{f.path}: unchanged")
                # reuse nothing extra here; unchanged artifacts remain persisted
                continue

            parser = self._registry.for_file(f.path)
            if parser is None:
                skipped.append(f"{f.path}: no parser")
                continue

            try:
                unit = parser.parse(f)
            except Exception as exc:  # noqa: BLE001 - isolate per-file failures (BR-3)
                failures.append(f"{f.path}: {type(exc).__name__}: {exc}")
                continue

            units.append(unit)
            symbols_total += len(unit.symbols)
            self._store.save_summary(extract(unit))

        # Graph + structure are rebuilt from the freshly parsed units.
        graph = graph_builder.build(units)
        self._store.save_graph(graph)
        self._store.save_structure(build_structure_tree(files))

        if hasattr(self._store, "save_manifest"):
            self._store.save_manifest(new_manifest)

        # Agent notes namespace is intentionally left untouched (BR-9).

        duration_ms = int((time.perf_counter() - t0) * 1000)
        return SyncReport(
            files_total=len(files),
            symbols_total=symbols_total,
            skipped=tuple(skipped),
            failures=tuple(failures),
            duration_ms=duration_ms,
        )
