"""UpdateService — persist agent-authored notes (US-A4).

Validates the payload (BR-21); on failure the knowledge base is left unchanged
(BR-22). Notes are written to the separate agent-note namespace only — engine
artifacts are never modified (BR-23).
"""

from __future__ import annotations

import re
from datetime import datetime

from ..domain.models import AgentNote
from ..ports.store_port import KnowledgeStorePort
from .measurement import measure
from .payloads import AgentNotePayload, UpdateResult

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T")


class UpdateService:
    def __init__(self, store: KnowledgeStorePort) -> None:
        self._store = store

    def apply_note(self, payload: AgentNotePayload) -> UpdateResult:
        with measure("update.note"):
            errors = self._validate(payload)
            if errors:
                return UpdateResult(ok=False, errors=tuple(errors))
            note = AgentNote(
                target=payload.target,
                body_md=payload.body_md,
                author=payload.author,
                created_at=payload.created_at,
            )
            self._store.save_agent_note(note)
            return UpdateResult(ok=True, note_id=note.note_id)

    @staticmethod
    def _validate(p: AgentNotePayload) -> list[str]:
        errors: list[str] = []
        if not p.target or not p.target.strip():
            errors.append("target is required")
        if not p.body_md or not p.body_md.strip():
            errors.append("body_md is required")
        if not p.author or not p.author.strip():
            errors.append("author is required")
        if not p.created_at or not _ISO_RE.match(p.created_at):
            errors.append("created_at must be ISO 8601 (YYYY-MM-DDT...)")
        else:
            try:
                datetime.fromisoformat(p.created_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append("created_at is not a valid ISO 8601 timestamp")
        return errors
