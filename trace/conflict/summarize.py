"""충돌 → 출력 DTO 변환 (UOW-03, C5, NFR Design P6, BR-OUT)."""

from __future__ import annotations

from trace.models.domain import Conflict
from trace.models.result import ConflictOut


def summarize_conflicts(conflicts: list[Conflict]) -> list[ConflictOut]:
    """Conflict 목록을 get_conflicts/analyze_project 출력용 ConflictOut로 변환한다."""
    return [
        ConflictOut(
            type=c.type.value,
            claim=c.claim,
            values=[
                {"value": cv.value, "source": cv.source, "location": cv.location}
                for cv in c.values
            ],
            interpretation=c.interpretation,
        )
        for c in conflicts
    ]


__all__ = ["summarize_conflicts"]
