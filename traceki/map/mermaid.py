"""Mermaid 렌더 — 의존 flowchart · 핵심 흐름 sequenceDiagram (UOW-07, FR-MAP-005).

라벨의 특수문자·개행·따옴표를 이스케이프해 문법 파손을 막는다(규칙 8, content-validation).
`render_dependency_graph`는 dep_edge가 참조하는 모든 노드를 출력에 포함한다(불변식, PBT P1).
`_sanitize_label`/`_node_id`는 멱등이다(PBT P4).
"""

from __future__ import annotations

import re

from traceki.map.models import RelationGraph

_ID_UNSAFE = re.compile(r"[^A-Za-z0-9_]+")


def _node_id(path: str) -> str:
    """Mermaid 노드 id로 안전한 식별자. 멱등(안전 문자만 남김)."""
    safe = _ID_UNSAFE.sub("_", path).strip("_")
    return "n_" + (safe or "node")


def _sanitize_label(text: str) -> str:
    """라벨 안전화: 개행·따옴표·대괄호를 무해한 형태로. 멱등(P4)."""
    out = str(text).replace("\r", " ").replace("\n", " ")
    out = out.replace('"', "'").replace("[", "(").replace("]", ")")
    out = re.sub(r"\s+", " ", out).strip()
    return out or "node"


def render_dependency_graph(graph: RelationGraph) -> str:
    """의존 관계를 `flowchart LR`로 렌더한다.

    dep_edge가 참조하는 노드(src/dst)는 그래프 nodes에 없더라도 반드시 선언된다(P1).
    """
    lines = ["flowchart LR"]
    declared: dict[str, str] = {}

    def declare(path: str, label: str | None = None) -> str:
        if path not in declared:
            nid = _node_id(path)
            declared[path] = nid
            lines.append(f'    {nid}["{_sanitize_label(label or path)}"]')
        return declared[path]

    for n in graph.nodes:
        declare(n.path, f"{n.module or n.path} ({n.type})")
    # 엣지가 참조하는 모든 노드 보장(P1)
    for e in graph.dep_edges:
        declare(e.src)
        declare(e.dst)
    for e in graph.dep_edges:
        lines.append(f"    {declared[e.src]} --> {declared[e.dst]}")
    if len(lines) == 1:
        lines.append("    empty[\"(관계 정보 없음)\"]")
    return "\n".join(lines)


def render_sequence(key_flow: list[dict]) -> str:
    """핵심 흐름을 `sequenceDiagram`으로 렌더한다.

    key_flow 항목: {step, file, symbol, note}. 없으면 최소 다이어그램을 반환한다.
    """
    lines = ["sequenceDiagram"]
    if not key_flow:
        lines.append("    participant App")
        lines.append("    Note over App: (핵심 흐름 정보 없음)")
        return "\n".join(lines)

    actors: list[str] = []
    steps: list[tuple[str, str]] = []
    for item in key_flow:
        if not isinstance(item, dict):
            continue
        actor = _actor_id(str(item.get("file") or item.get("symbol") or "step"))
        label = _sanitize_label(item.get("symbol") or item.get("step") or item.get("note") or "")
        if actor not in actors:
            actors.append(actor)
        steps.append((actor, label))
    for a in actors:
        lines.append(f"    participant {a}")
    prev = None
    for actor, label in steps:
        if prev is None:
            lines.append(f"    Note over {actor}: {label}")
        else:
            lines.append(f"    {prev}->>{actor}: {label}")
        prev = actor
    return "\n".join(lines)


def _actor_id(text: str) -> str:
    safe = _ID_UNSAFE.sub("_", text.rsplit("/", 1)[-1]).strip("_")
    return (safe or "step")[:40]


__all__ = ["render_dependency_graph", "render_sequence", "_node_id", "_sanitize_label"]
