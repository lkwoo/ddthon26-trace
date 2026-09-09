"""Orchestrator services (Application Design Q3).

Each service holds orchestration only: it sequences engine components and
repositories and returns typed reports/results. No service issues SQL or calls
an LLM (NFR-3.1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from knowledge_store.codegraph.analyzer import CodeUnit
from knowledge_store.services.system import KnowledgeSystem
from knowledge_store.types import (
    Content,
    ExportResult,
    IngestionReport,
    SearchHit,
    SnippetResult,
    Status,
    Summary,
)


class WikiExportService:
    """Regenerate the static viewer artifacts (US-7.4, NFR-2.1)."""

    def __init__(self, system: KnowledgeSystem) -> None:
        self._sys = system

    def regenerate(self, export_dir: Optional[str | Path] = None) -> ExportResult:
        target = Path(export_dir) if export_dir else self._sys.wiki_dir
        return self._sys.exporter.export(target)


class IngestionService:
    """Deterministic ingest -> chunk -> version -> graph -> embed -> relate ->
    persist -> wiki export pipeline (interactive, agent-driven)."""

    def __init__(self, system: KnowledgeSystem,
                 wiki_export: Optional[WikiExportService] = None) -> None:
        self._sys = system
        self._wiki = wiki_export or WikiExportService(system)

    def ingest(self, paths: list[str], *, export: bool = True) -> IngestionReport:
        report = IngestionReport(status=Status.OK)
        code_units: list[CodeUnit] = []

        for raw in paths:
            path = Path(raw)
            if not path.exists():
                report.unsupported.append(f"{raw} (not found)")
                continue
            extraction = self._sys.registry.extract(path)
            if extraction.status == Status.UNSUPPORTED:
                report.unsupported.append(raw)
                continue
            if extraction.status == Status.ERROR:
                report.unsupported.append(f"{raw} ({extraction.message})")
                continue

            report.ingested_files += 1
            if extraction.is_code:
                code_units.append(CodeUnit(path=str(path), language=extraction.language,
                                           text=extraction.text))

            # chunk -> version (match against existing chunks from same source)
            new_chunks = self._sys.chunker.chunk(extraction)
            candidates = self._sys.repos.chunks.by_source(str(path))
            for chunk in new_chunks:
                match = self._sys.versioner.match(chunk, candidates)
                version = self._sys.versioner.apply_version(chunk, match)
                if version.is_new:
                    report.chunks_new += 1
                else:
                    report.chunks_updated += 1

        # code graph
        if code_units:
            graph = self._sys.analyzer.analyze(code_units)
            for node in graph.nodes:
                self._sys.repos.graph.add_node(node)
            for edge in graph.edges:
                self._sys.repos.graph.add_edge(edge)
            self._sys.repos.graph.commit()
            report.unresolved.extend(graph.unresolved)

        # embed all latest chunks + build relationships
        latest = self._sys.repos.chunks.all_latest()
        self._sys.search.index_many([(c.id, c.text) for c in latest])
        rels = self._sys.relationship_builder.build(latest)
        self._sys.repos.relationships.add_many(rels)
        report.unresolved.extend(r.dst_id for r in rels if not r.resolved)

        # summaries still needed
        report.pending_summaries = self._sys.summary_store.pending()
        report.unresolved = sorted(set(report.unresolved))

        if export:
            self._wiki.regenerate()
        return report


class QueryService:
    """Low-latency, token-efficient reads (NFR-1)."""

    def __init__(self, system: KnowledgeSystem) -> None:
        self._sys = system

    def semantic_query(self, intent: str, limit: int = 5) -> list[SearchHit]:
        return self._sys.search.search(intent, limit=limit)

    def smart_snippet(self, target_id: str, token_budget: int) -> SnippetResult:
        chunk = self._sys.repos.chunks.get(target_id)
        if chunk is None:
            return SnippetResult(status=Status.NOT_FOUND, token_budget=token_budget)
        return self._sys.snippet_builder.build(chunk.text, token_budget)

    def read_structure(self) -> dict:
        return {
            "nodes": [n.__dict__ for n in self._sys.repos.graph.nodes()],
            "edges": [{"src": e.src, "dst": e.dst, "type": e.type.value,
                       "resolved": e.resolved} for e in self._sys.repos.graph.edges()],
        }

    def read_relationships(self, src_id: str) -> list[dict]:
        return [{"dst": r.dst_id, "type": r.type.value, "score": r.score,
                 "resolved": r.resolved}
                for r in self._sys.repos.relationships.for_source(src_id)]

    def read_summary(self, chunk_id: str) -> Optional[str]:
        summary = self._sys.repos.summaries.get(chunk_id)
        return summary.text if summary else None


class SummarizationService:
    """Agent-driven summaries; the server never generates summary text (FR-5)."""

    def __init__(self, system: KnowledgeSystem) -> None:
        self._sys = system

    def get_content_to_summarize(self, ref_id: str) -> Optional[Content]:
        return self._sys.summary_store.extract_for_summary(ref_id)

    def store_summary(self, chunk_id: str, text: str) -> Status:
        return self._sys.summary_store.store_summary(chunk_id, text)

    def get_summary(self, chunk_id: str) -> Optional[Summary]:
        return self._sys.summary_store.get_summary(chunk_id)
