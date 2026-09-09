"""Self-describing MCP tool/resource registry (FR-6, NFR-5 discoverability).

Each ToolSpec carries a description, input schema and explicit *when to use*
guidance so an agent can discover and time calls without manual instructions
(US-9.1). Handlers dispatch to the orchestrator services and return typed
:class:`ToolResult` envelopes, kept independent of the ``mcp`` package so they
are unit-testable on their own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from knowledge_store.services.services import (
    IngestionService,
    QueryService,
    SummarizationService,
    WikiExportService,
)
from knowledge_store.services.system import KnowledgeSystem
from knowledge_store.types import Status, ToolResult


@dataclass
class ToolSpec:
    name: str
    description: str
    when_to_use: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], ToolResult] = field(repr=False, default=None)  # type: ignore

    def manifest(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "inputSchema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self, specs: list[ToolSpec]) -> None:
        self._specs = {s.name: s for s in specs}

    def names(self) -> list[str]:
        return sorted(self._specs)

    def manifest(self) -> list[dict[str, Any]]:
        return [self._specs[n].manifest() for n in self.names()]

    def get(self, name: str) -> ToolSpec | None:
        return self._specs.get(name)

    def call(self, name: str, args: dict[str, Any]) -> ToolResult:
        spec = self._specs.get(name)
        if spec is None:
            return ToolResult(status=Status.NOT_FOUND, message=f"unknown tool: {name}")
        return spec.handler(args or {})


def build_registry(system: KnowledgeSystem) -> ToolRegistry:
    ingestion = IngestionService(system)
    query = QueryService(system)
    summarize = SummarizationService(system)
    wiki = WikiExportService(system)

    def _ingest(args: dict[str, Any]) -> ToolResult:
        paths = args.get("paths") or ([args["path"]] if args.get("path") else [])
        if not paths:
            return ToolResult(status=Status.ERROR, message="provide 'paths' (list) or 'path'")
        report = ingestion.ingest([str(p) for p in paths], export=bool(args.get("export", True)))
        return ToolResult(status=report.status, data=report)

    def _semantic_query(args: dict[str, Any]) -> ToolResult:
        intent = args.get("intent", "")
        if not intent:
            return ToolResult(status=Status.ERROR, message="provide 'intent'")
        hits = query.semantic_query(intent, int(args.get("limit", 5)))
        return ToolResult(status=Status.OK, data=hits)

    def _smart_snippet(args: dict[str, Any]) -> ToolResult:
        target = args.get("target_id")
        if not target:
            return ToolResult(status=Status.ERROR, message="provide 'target_id'")
        result = query.smart_snippet(target, int(args.get("token_budget", 256)))
        return ToolResult(status=result.status, data=result)

    def _get_content(args: dict[str, Any]) -> ToolResult:
        content = summarize.get_content_to_summarize(args.get("ref_id", ""))
        if content is None:
            return ToolResult(status=Status.NOT_FOUND, message="ref_id not found")
        return ToolResult(status=Status.OK, data=content)

    def _store_summary(args: dict[str, Any]) -> ToolResult:
        status = summarize.store_summary(args.get("chunk_id", ""), args.get("text", ""))
        return ToolResult(status=status)

    def _get_summary(args: dict[str, Any]) -> ToolResult:
        summary = summarize.get_summary(args.get("chunk_id", ""))
        if summary is None:
            return ToolResult(status=Status.NOT_FOUND)
        return ToolResult(status=Status.OK, data=summary)

    def _read_structure(args: dict[str, Any]) -> ToolResult:
        return ToolResult(status=Status.OK, data=query.read_structure())

    def _read_relationships(args: dict[str, Any]) -> ToolResult:
        return ToolResult(status=Status.OK, data=query.read_relationships(args.get("src_id", "")))

    def _regenerate_wiki(args: dict[str, Any]) -> ToolResult:
        return ToolResult(status=Status.OK, data=wiki.regenerate())

    specs = [
        ToolSpec("ingest",
                 "Ingest documents/code (md, txt, pdf, xlsx, csv, xml, sql, source) into the store: extract, chunk, version, build the code graph and relationships, embed, and refresh the wiki. Directory paths are walked recursively.",
                 "Call when the user adds or updates project files and wants them searchable/linked. Accepts individual files or directories (recursed).",
                 {"type": "object", "properties": {
                     "paths": {"type": "array", "items": {"type": "string"}},
                     "path": {"type": "string"},
                     "export": {"type": "boolean", "default": True}},
                  "anyOf": [{"required": ["paths"]}, {"required": ["path"]}]},
                 _ingest),
        ToolSpec("semantic_query",
                 "Intent-based semantic search across stored chunks/symbols; returns ranked hits with short previews (token-efficient).",
                 "Call when you need to find relevant knowledge by meaning rather than keyword.",
                 {"type": "object", "properties": {
                     "intent": {"type": "string"}, "limit": {"type": "integer", "default": 5}},
                  "required": ["intent"]},
                 _semantic_query),
        ToolSpec("smart_snippet",
                 "Return the most relevant minimal code/text scope for a chunk id, not exceeding a token budget while preserving semantic boundaries.",
                 "Call when you need a symbol's context but must respect your remaining token budget.",
                 {"type": "object", "properties": {
                     "target_id": {"type": "string"}, "token_budget": {"type": "integer", "default": 256}},
                  "required": ["target_id"]},
                 _smart_snippet),
        ToolSpec("get_content_to_summarize",
                 "Return the raw content of a chunk/symbol for you (the agent) to summarize. The server never generates summaries itself.",
                 "Call before authoring a summary so you have the exact source content.",
                 {"type": "object", "properties": {"ref_id": {"type": "string"}}, "required": ["ref_id"]},
                 _get_content),
        ToolSpec("store_summary",
                 "Persist an agent-authored summary linked to a chunk id.",
                 "Call after you generate a summary to save it back into the knowledge store.",
                 {"type": "object", "properties": {
                     "chunk_id": {"type": "string"}, "text": {"type": "string"}},
                  "required": ["chunk_id", "text"]},
                 _store_summary),
        ToolSpec("get_summary",
                 "Retrieve a previously stored summary for a chunk id.",
                 "Call to reuse an existing summary instead of re-reading full content.",
                 {"type": "object", "properties": {"chunk_id": {"type": "string"}}, "required": ["chunk_id"]},
                 _get_summary),
        ToolSpec("read_structure",
                 "Read the code structure graph (nodes + edges: define/call/depend/inherit/contain).",
                 "Call to understand a codebase's logical structure and cross-file dependencies.",
                 {"type": "object", "properties": {}},
                 _read_structure),
        ToolSpec("read_relationships",
                 "Read code<->document relationships for a given source id (embedding/link/tag).",
                 "Call to find documents related to a symbol or chunk.",
                 {"type": "object", "properties": {"src_id": {"type": "string"}}, "required": ["src_id"]},
                 _read_relationships),
        ToolSpec("regenerate_wiki",
                 "Regenerate the static wiki export files for the human D3 viewer.",
                 "Call to refresh the reviewer-facing wiki after manual changes.",
                 {"type": "object", "properties": {}},
                 _regenerate_wiki),
    ]
    return ToolRegistry(specs)
