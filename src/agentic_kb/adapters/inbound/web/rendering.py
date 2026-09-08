"""Pure SSR rendering functions for the web viewer (US-H1..H4).

Deterministic, dependency-free (stdlib only). Every dynamic value is passed
through :func:`html.escape`; the Markdown renderer emits only a fixed allow-list
of elements, so no raw HTML flows through (BR-W6/W7). These functions take U1
domain objects and return HTML strings — no live server needed to test them.
"""

from __future__ import annotations

import html
from urllib.parse import quote

from ....domain.models import MergedSummary, RelationshipGraph, StructureTree, TreeNode
from .assets import CSS


# --------------------------------------------------------------------------
# Markdown subset -> HTML
# --------------------------------------------------------------------------
def markdown_to_html(md: str) -> str:
    """Render a deterministic Markdown subset to safe HTML (BR-W6/W7).

    Supports ATX headings, fenced code blocks, unordered lists, paragraphs and
    inline ``code``. All text is HTML-escaped; unknown syntax degrades to text.
    """
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    para: list[str] = []
    items: list[str] = []

    def flush_para() -> None:
        if para:
            out.append("<p>" + _inline("\n".join(para)) + "</p>")
            para.clear()

    def flush_list() -> None:
        if items:
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
            items.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            flush_list()
            i += 1
            code: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
            continue

        if stripped.startswith("#"):
            flush_para()
            flush_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(max(level, 1), 6)
            text = stripped[level:].strip()
            out.append(f"<h{level}>{_inline(text)}</h{level}>")
            i += 1
            continue

        if stripped.startswith(("- ", "* ")):
            flush_para()
            items.append(stripped[2:])
            i += 1
            continue

        if stripped == "":
            flush_para()
            flush_list()
            i += 1
            continue

        flush_list()
        para.append(line)
        i += 1

    flush_para()
    flush_list()
    return "\n".join(out)


def _inline(text: str) -> str:
    """Escape text and render inline ``code`` spans only."""
    parts = text.split("`")
    rendered: list[str] = []
    for idx, part in enumerate(parts):
        esc = html.escape(part)
        # odd indices are inside backticks (only when a closing tick exists)
        if idx % 2 == 1 and idx < len(parts) - (0 if len(parts) % 2 else 1):
            rendered.append(f"<code>{esc}</code>")
        elif idx % 2 == 1:
            rendered.append("`" + esc)  # unmatched backtick -> literal
        else:
            rendered.append(esc)
    return "".join(rendered)


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------
def layout(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html><html lang=\"en\"><head>"
        f"<meta charset=\"utf-8\"><title>{html.escape(title)}</title>"
        "<link rel=\"stylesheet\" href=\"/static/style.css\"></head><body>"
        "<nav><a href=\"/\">Tree</a> · <a href=\"/graph\">Graph</a></nav>"
        f"<main>{body}</main>"
        "<footer>엔진 자동 생성 콘텐츠는 재동기화 시 소스 기준으로 재생성됩니다 "
        "(engine-first, FR-C1).</footer>"
        "</body></html>"
    )


def render_index(tree: StructureTree | None) -> str:
    if tree is None:
        return layout("Agentic KB", "<p class=\"empty\">지식 베이스가 비어 있습니다. 먼저 <code>sync</code>를 실행하세요.</p>")
    return layout("Project Structure", "<h1>Project Structure</h1>" + _tree_node(tree.root))


def _tree_node(node: TreeNode) -> str:
    name = html.escape(node.name or node.path or "/")
    if node.kind == "file":
        href = "/summary/" + quote(node.path)
        return f"<li class=\"file\"><a href=\"{href}\">{name}</a></li>"
    children = "".join(_tree_node(c) for c in node.children)
    return (
        f"<details open><summary>{name}</summary>"
        f"<ul>{children}</ul></details>"
    )


def render_wiki(merged: MergedSummary) -> str:
    target = html.escape(merged.target)
    banner = (
        "<div class=\"banner\">이 페이지의 <b>엔진 섹션</b>은 소스에서 자동 생성되어 "
        "재동기화 시 재생성됩니다. <b>에이전트 노트</b>는 별도로 보존됩니다. (FR-C1)</div>"
    )
    engine_html = _engine_section(merged)
    notes_html = _notes_section(merged)
    body_order = [engine_html, notes_html] if merged.engine_first else [notes_html, engine_html]
    return layout(
        f"Wiki · {merged.target}",
        f"<h1>{target}</h1>{banner}" + "".join(body_order),
    )


def _engine_section(merged: MergedSummary) -> str:
    if merged.engine is None:
        return "<section class=\"engine\"><span class=\"badge engine\">엔진 자동 생성 · 재생성</span><p>엔진 요약 없음.</p></section>"
    e = merged.engine
    md_parts: list[str] = []
    if e.signatures:
        md_parts.append("## Signatures\n" + "\n".join(f"- `{s}`" for s in e.signatures))
    if e.docstrings:
        md_parts.append("## Docstrings\n" + "\n\n".join(e.docstrings))
    if e.headings:
        md_parts.append("## Headings\n" + "\n".join(f"- {h}" for h in e.headings))
    if e.comments:
        md_parts.append("## Comments\n" + "\n".join(f"- {c}" for c in e.comments))
    content = markdown_to_html("\n\n".join(md_parts)) if md_parts else "<p>(비어 있음)</p>"
    return (
        "<section class=\"engine\">"
        "<span class=\"badge engine\">엔진 자동 생성 · 재생성</span>"
        f"{content}</section>"
    )


def _notes_section(merged: MergedSummary) -> str:
    if not merged.agent_notes:
        return ""
    notes = []
    for note in merged.agent_notes:
        meta = html.escape(f"{note.author} · {note.created_at}")
        notes.append(
            f"<article class=\"note\"><div class=\"meta\">{meta}</div>"
            f"{markdown_to_html(note.body_md)}</article>"
        )
    return (
        "<section class=\"notes\">"
        "<span class=\"badge note\">에이전트 작성 · 보존</span>"
        + "".join(notes)
        + "</section>"
    )


def render_graph(graph: RelationshipGraph | None) -> str:
    if graph is None or not graph.nodes:
        return layout("Dependency Graph", "<h1>Dependency Graph</h1><p class=\"empty\">관계 데이터가 없습니다.</p>")
    node_items = "".join(
        f"<li><a href=\"/summary/{quote(_node_path(n.id))}\">{html.escape(n.name)}</a> "
        f"<span class=\"kind\">{html.escape(n.kind)}</span></li>"
        for n in graph.nodes
    )
    edge_items = "".join(
        f"<li>{html.escape(e.src)} → {html.escape(e.dst)} "
        f"<span class=\"kind\">{html.escape(e.kind)}</span></li>"
        for e in graph.edges
    )
    svg = _graph_svg(graph)
    body = (
        "<h1>Dependency Graph</h1>"
        f"{svg}"
        f"<h2>Nodes</h2><ul class=\"nodes\">{node_items}</ul>"
        f"<h2>Edges</h2><ul class=\"edges\">{edge_items or '<li>(none)</li>'}</ul>"
    )
    return layout("Dependency Graph", body)


def _graph_svg(graph: RelationshipGraph) -> str:
    """Deterministic lightweight SVG: nodes on a vertical axis, edges as lines."""
    nodes = list(graph.nodes)
    positions = {n.id: (60, 40 + idx * 40) for idx, n in enumerate(nodes)}
    height = max(80, 40 + len(nodes) * 40)
    lines = []
    for e in graph.edges:
        if e.src in positions and e.dst in positions:
            x1, y1 = positions[e.src]
            x2, y2 = positions[e.dst]
            lines.append(f"<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" stroke=\"#888\"/>")
    circles = []
    for n in nodes:
        x, y = positions[n.id]
        circles.append(
            f"<circle cx=\"{x}\" cy=\"{y}\" r=\"6\" fill=\"#36c\"/>"
            f"<text x=\"{x + 12}\" y=\"{y + 4}\">{html.escape(n.name)}</text>"
        )
    return (
        f"<svg class=\"graph\" width=\"400\" height=\"{height}\" role=\"img\">"
        + "".join(lines)
        + "".join(circles)
        + "</svg>"
    )


def _node_path(symbol_id: str) -> str:
    """Symbol ids are ``path::kind::qualified_name``; the wiki is keyed by file
    path, so link to the path component (US-H3 AC-2 -> WikiPage)."""
    return symbol_id.split("::", 1)[0]


def render_not_found(target: str) -> str:
    return layout(
        "Not Found",
        f"<h1>404 — Not Found</h1><p>대상을 찾을 수 없습니다: <code>{html.escape(target)}</code></p>"
        "<p><a href=\"/\">트리로 돌아가기</a></p>",
    )


def render_css() -> str:
    return CSS
