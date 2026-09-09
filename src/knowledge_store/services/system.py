"""KnowledgeSystem — wires the store, components and services for one target.

A single assembly point so the MCP server and installer construct the whole
pipeline consistently. Embedding dimension is taken from the provider so the
sqlite-vec table (when available) matches.
"""

from __future__ import annotations

from pathlib import Path

from knowledge_store.codegraph import (
    CodeStructureAnalyzer,
    EmbeddingSimilarityStrategy,
    MarkdownLinkStrategy,
    RelationshipBuilder,
    TagMatchStrategy,
)
from knowledge_store.embedding import SearchEngine, get_default_provider
from knowledge_store.ingestion import ChunkVersioner, Chunker, default_registry
from knowledge_store.retrieval import SnippetBuilder, SummaryStore, TokenEstimator
from knowledge_store.store import KnowledgeStore, Repositories
from knowledge_store.wiki import WikiExporter


class KnowledgeSystem:
    def __init__(self, target_dir: str | Path, *, in_memory: bool = False) -> None:
        self.provider = get_default_provider()
        self.store = KnowledgeStore(target_dir, in_memory=in_memory)
        self.store.connect()
        self.store.init_schema(embedding_dimension=self.provider.dimension)
        self.repos = Repositories(self.store)

        # engine components
        self.registry = default_registry()
        self.chunker = Chunker()
        self.versioner = ChunkVersioner(self.repos.chunks)
        self.search = SearchEngine(self.repos, self.provider)
        self.analyzer = CodeStructureAnalyzer()
        self.token_estimator = TokenEstimator()
        self.snippet_builder = SnippetBuilder(self.token_estimator)
        self.summary_store = SummaryStore(self.repos)
        self.exporter = WikiExporter(self.repos)
        self.relationship_builder = RelationshipBuilder([
            EmbeddingSimilarityStrategy(self.search),
            MarkdownLinkStrategy(),
            TagMatchStrategy(),
        ])

    @property
    def wiki_dir(self) -> Path:
        return self.store.store_dir / "wiki"

    def close(self) -> None:
        self.store.close()
