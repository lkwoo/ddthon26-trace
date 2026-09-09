"""Labeled evaluation dataset — questions with file-level gold labels.

Gold labels are **file-level** for now (Increment 2, Q2=C). The schema already
carries optional ``gold_symbols`` / ``gold_lines`` fields so it can be upgraded
to symbol/line granularity once U-Chunking attaches line/symbol metadata to
chunks — without breaking existing datasets.

Datasets are JSON so they are easy to hand-edit and round-trip losslessly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvalQuestion:
    """A single evaluation question with its gold (relevant) file labels."""

    id: str
    intent: str
    gold_files: tuple[str, ...]
    # Forward-compatible, optional finer-grained labels (unused until U-Chunking):
    gold_symbols: tuple[str, ...] = ()
    gold_lines: tuple[tuple[str, int, int], ...] = ()  # (file, start, end)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "intent": self.intent,
            "gold_files": list(self.gold_files),
        }
        if self.gold_symbols:
            d["gold_symbols"] = list(self.gold_symbols)
        if self.gold_lines:
            d["gold_lines"] = [list(t) for t in self.gold_lines]
        if self.note:
            d["note"] = self.note
        return d

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "EvalQuestion":
        return EvalQuestion(
            id=str(d["id"]),
            intent=str(d["intent"]),
            gold_files=tuple(d.get("gold_files", ())),
            gold_symbols=tuple(d.get("gold_symbols", ())),
            gold_lines=tuple((str(f), int(s), int(e)) for f, s, e in d.get("gold_lines", ())),
            note=str(d.get("note", "")),
        )


@dataclass
class EvalDataset:
    """A named set of evaluation questions plus optional corpus hints."""

    name: str
    questions: list[EvalQuestion] = field(default_factory=list)
    # Optional list of corpus file globs/paths (relative to the dataset root):
    corpus: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "corpus": list(self.corpus),
            "questions": [q.to_dict() for q in self.questions],
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "EvalDataset":
        return EvalDataset(
            name=str(d.get("name", "unnamed")),
            corpus=list(d.get("corpus", [])),
            questions=[EvalQuestion.from_dict(q) for q in d.get("questions", [])],
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def from_json(text: str) -> "EvalDataset":
        return EvalDataset.from_dict(json.loads(text))

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @staticmethod
    def load(path: str | Path) -> "EvalDataset":
        return EvalDataset.from_json(Path(path).read_text(encoding="utf-8"))
