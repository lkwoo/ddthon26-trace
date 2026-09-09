"""describe_relations — 온보딩 서술 LLM step (UOW-07, C3 계약, US-07.5).

정적 그래프(진입점·의존·호출·Feature 매핑)를 컨텍스트로 주입하고, LLM에게 신입 개발자용
내러티브·관계 주해·핵심 흐름을 요청한다. 근거 없는 주장은 채택하지 않으며 저신뢰는 LOW로
표기한다(규칙 2·3, FR-MAP-007 / NFR-AI-003).

replay step_key: ``describe_relations``.
"""

from __future__ import annotations

from typing import Any

from traceki.common import get_logger
from traceki.llm import LLMService
from traceki.map.models import EntryPoint, FeatureFileMap, RelationGraph
from traceki.prompts import get_prompt

_log = get_logger("trace.map.describe")

_MAX_EDGES = 60  # 프롬프트 비용 방어


def build_context(
    entry_points: list[EntryPoint],
    graph: RelationGraph,
    feature_maps: list[FeatureFileMap],
) -> str:
    """정적 추출 결과를 프롬프트용 텍스트 컨텍스트로 렌더한다."""
    lines: list[str] = ["## Entry points"]
    lines += [f"- [{e.kind}] {e.symbol} @ {e.file} ({e.reason})" for e in entry_points] or ["- (none found)"]

    lines.append("\n## Dependencies (file -> module)")
    dep = [f"- {e.src} -> {e.dst}" for e in graph.dep_edges[:_MAX_EDGES]] or ["- (none)"]
    lines += dep

    lines.append("\n## Calls (caller -> callee)")
    calls = [f"- {e.caller} -> {e.callee} @ {e.file}" for e in graph.call_edges[:_MAX_EDGES]] or ["- (none)"]
    lines += calls

    lines.append("\n## Features -> files")
    for m in feature_maps:
        files = ", ".join(f["path"] for f in m.files) or "(none)"
        lines.append(f"- {m.title} ({m.feature_id}): {files}")

    if graph.unresolved:
        lines.append("\n## Unresolved (static parse unavailable — infer from paths only)")
        lines += [f"- {p}" for p in graph.unresolved]
    return "\n".join(lines)


def describe_relations(context: str, llm: LLMService) -> dict:
    """온보딩 내러티브·관계 주해·핵심 흐름을 생성한다.

    반환 dict: {narrative, relation_notes:[{relation,note,evidence}], key_flow:[{step,file,symbol,note}]}.
    LLM/replay 실패는 호출자(오케스트레이션)가 warning으로 흡수한다.
    """
    prompt = get_prompt("onboarding_map", context=context)
    raw = llm.structured("describe_relations", prompt)
    return _normalize(raw)


def _normalize(raw: Any) -> dict:
    if not isinstance(raw, dict):
        return {"narrative": "", "relation_notes": [], "key_flow": []}
    narrative = str(raw.get("narrative", "")).strip()
    relation_notes = [
        {
            "relation": str(n.get("relation", "")),
            "note": str(n.get("note", "")),
            "evidence": [str(e) for e in n.get("evidence", [])],
        }
        for n in raw.get("relation_notes", [])
        if isinstance(n, dict)
    ]
    key_flow = [
        {
            "step": str(s.get("step", "")),
            "file": str(s.get("file", "")),
            "symbol": str(s.get("symbol", "")),
            "note": str(s.get("note", "")),
        }
        for s in raw.get("key_flow", [])
        if isinstance(s, dict)
    ]
    return {"narrative": narrative, "relation_notes": relation_notes, "key_flow": key_flow}


__all__ = ["describe_relations", "build_context"]
