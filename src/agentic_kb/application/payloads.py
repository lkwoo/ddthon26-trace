"""Service-layer payload / result value objects."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentNotePayload:
    target: str
    body_md: str
    author: str
    created_at: str


@dataclass(frozen=True)
class UpdateResult:
    ok: bool
    note_id: str | None = None
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {"ok": self.ok, "note_id": self.note_id, "errors": list(self.errors)}
