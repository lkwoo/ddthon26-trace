"""SummaryStore — Agent-driven summarization support (Epic 5, FR-5).

The server never calls an LLM (NFR-3.1). It returns content for the agent to
summarize (US-5.1) and persists/retrieves agent-authored summaries (US-5.2).
"""

from __future__ import annotations

from typing import Optional

from knowledge_store.store.repositories import Repositories
from knowledge_store.types import Content, Status, Summary


class SummaryStore:
    def __init__(self, repos: Repositories) -> None:
        self._repos = repos

    def extract_for_summary(self, ref_id: str) -> Optional[Content]:
        """Return the content the agent should summarize for a chunk id."""
        chunk = self._repos.chunks.get(ref_id)
        if chunk is None:
            return None
        return Content(ref_id=ref_id, text=chunk.text, kind=chunk.kind)

    def store_summary(self, chunk_id: str, text: str) -> Status:
        if self._repos.chunks.get(chunk_id) is None:
            return Status.NOT_FOUND
        self._repos.summaries.put(chunk_id, text)
        return Status.OK

    def get_summary(self, chunk_id: str) -> Optional[Summary]:
        return self._repos.summaries.get(chunk_id)

    def pending(self) -> list[str]:
        """Chunk ids that have no stored summary yet."""
        summarized = {s.chunk_id for s in self._repos.summaries.all()}
        return [c.id for c in self._repos.chunks.all_latest() if c.id not in summarized]
