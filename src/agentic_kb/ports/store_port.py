"""KnowledgeStorePort — abstract contract for knowledge persistence.

Agent notes are stored in a separate namespace and are never overwritten by
re-sync (BR-9, Q6). Missing targets return None / empty (BR-13).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain.models import (
    AgentNote,
    ModuleSummary,
    RelationshipGraph,
    StructureTree,
)


class KnowledgeStorePort(ABC):
    # --- engine artifacts (overwritten on re-sync, BR-8) ---
    @abstractmethod
    def save_structure(self, tree: StructureTree) -> None: ...

    @abstractmethod
    def save_summary(self, summary: ModuleSummary) -> None: ...

    @abstractmethod
    def save_graph(self, graph: RelationshipGraph) -> None: ...

    @abstractmethod
    def load_structure(self) -> StructureTree | None: ...

    @abstractmethod
    def load_summary(self, target: str) -> ModuleSummary | None: ...

    @abstractmethod
    def load_graph(self) -> RelationshipGraph | None: ...

    @abstractmethod
    def all_summaries(self) -> list[ModuleSummary]:
        """All stored engine summaries (for building a query index)."""

    # --- agent notes (separate namespace, preserved on re-sync, BR-9) ---
    @abstractmethod
    def save_agent_note(self, note: AgentNote) -> None: ...

    @abstractmethod
    def load_agent_notes(self, target: str) -> list[AgentNote]: ...

    # --- sha skip-cache (US-N7 AC-1) ---
    @abstractmethod
    def get_stored_sha(self, path: str) -> str | None: ...

    @abstractmethod
    def exists(self, target: str) -> bool: ...
