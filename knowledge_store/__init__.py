"""Dual-Interface Knowledge Store.

An LLM-free, local knowledge base exposed to AI agents over MCP (stdio) and to
humans through a static D3 wiki viewer. The server is deterministic and never
calls an external LLM or embedding API; summaries are authored by the agent.

Package layout (one sub-package per unit of work):
    types      U-shared  typed result objects + enums
    store      U1        KnowledgeStore + repositories (SQLite + sqlite-vec)
    embedding  U2        EmbeddingProvider + SearchEngine
    ingestion  U3        extractors, Chunker, ChunkVersioner
    codegraph  U4        CodeStructureAnalyzer, RelationshipBuilder
    retrieval  U5        SnippetBuilder, TokenEstimator, SummaryStore
    services   U6        orchestrator services
    mcp        U6        thin MCP stdio adapter
    wiki       U7        WikiExporter (static export)
    install    U8        InstallService + CLI
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
