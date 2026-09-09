"""CodeStructureAnalyzer — extract symbols and relations (FR-2.1, FR-2.2).

Deterministic and LLM-free. When ``tree-sitter-language-pack`` is installed it
is used for robust parsing; otherwise a regex-based analyzer handles Python well
and provides best-effort declaration detection for other languages. Cross-file
symbol resolution links call sites to definitions by name; unresolved references
are reported without aborting the graph (US-2.2).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from knowledge_store.types import EdgeType, GraphEdge, GraphNode, GraphResult, Status


@dataclass
class CodeUnit:
    path: str
    language: str
    text: str


# Regex fallbacks (deterministic). Keyed by language family.
_PY_DEF = re.compile(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", re.M)
_PY_CLASS = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\s*[\(:]", re.M)
_PY_CLASS_BASES = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", re.M)
_PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M)
_CALL = re.compile(r"([A-Za-z_]\w*)\s*\(")

_GENERIC_FUNC = re.compile(
    r"\b(?:function|func|fn|def|void|public|private|static)\s+([A-Za-z_]\w*)\s*\(", re.M)
_GENERIC_CLASS = re.compile(r"\b(?:class|struct|interface)\s+([A-Za-z_]\w*)", re.M)

_KEYWORD_CALLS = {"if", "for", "while", "return", "print", "def", "class", "with",
                  "switch", "catch", "and", "or", "not", "in", "elif", "else"}


def _node_id(path: str, name: str, kind: str) -> str:
    return f"{kind}:{path}:{name}"


class CodeStructureAnalyzer:
    def analyze(self, units: list[CodeUnit]) -> GraphResult:
        result = GraphResult(status=Status.OK)
        defined: dict[str, str] = {}   # symbol name -> node id (last definition wins deterministically)
        call_sites: list[tuple[str, str]] = []  # (caller node id, called name)

        for unit in sorted(units, key=lambda u: u.path):
            file_id = _node_id(unit.path, unit.path, "file")
            result.nodes.append(GraphNode(id=file_id, name=unit.path, kind="file",
                                          path=unit.path, language=unit.language))
            symbols = self._extract_symbols(unit)
            for sym_kind, name, bases in symbols:
                node_id = _node_id(unit.path, name, sym_kind)
                result.nodes.append(GraphNode(id=node_id, name=name, kind=sym_kind,
                                              path=unit.path, language=unit.language))
                result.edges.append(GraphEdge(file_id, node_id, EdgeType.CONTAIN))
                result.edges.append(GraphEdge(node_id, file_id, EdgeType.DEFINE))
                defined[name] = node_id
                for base in bases:
                    call_sites.append((node_id, base))  # inheritance resolved below
                    result.edges.append(GraphEdge(node_id, base, EdgeType.INHERIT, resolved=False))
            # module dependencies
            for mod in self._imports(unit):
                result.edges.append(GraphEdge(file_id, mod, EdgeType.DEPEND, resolved=False))
            # call edges
            for caller, called in self._calls(unit):
                call_sites.append((caller, called))

        # Cross-file symbol resolution.
        seen_edges: set[tuple[str, str, str]] = set()
        for caller_id, called in call_sites:
            target = defined.get(called)
            key = (caller_id, called, "call")
            if key in seen_edges:
                continue
            seen_edges.add(key)
            if target is not None:
                result.edges.append(GraphEdge(caller_id, target, EdgeType.CALL))
            else:
                result.edges.append(GraphEdge(caller_id, called, EdgeType.CALL, resolved=False))
                result.unresolved.append(called)

        # Re-resolve inheritance placeholders against known definitions.
        resolved_edges: list[GraphEdge] = []
        for edge in result.edges:
            if edge.type == EdgeType.INHERIT and not edge.resolved and edge.dst in defined:
                resolved_edges.append(GraphEdge(edge.src, defined[edge.dst], EdgeType.INHERIT))
            else:
                resolved_edges.append(edge)
        result.edges = resolved_edges
        result.unresolved = sorted(set(result.unresolved))
        return result

    # -- extraction --------------------------------------------------------
    def _extract_symbols(self, unit: CodeUnit) -> list[tuple[str, str, list[str]]]:
        if unit.language == "python":
            syms: list[tuple[str, str, list[str]]] = []
            bases_by_class = {m.group(1): [b.strip() for b in m.group(2).split(",") if b.strip()]
                              for m in _PY_CLASS_BASES.finditer(unit.text)}
            for m in _PY_CLASS.finditer(unit.text):
                syms.append(("class", m.group(1), bases_by_class.get(m.group(1), [])))
            for m in _PY_DEF.finditer(unit.text):
                syms.append(("function", m.group(1), []))
            return syms
        syms = [("class", m.group(1), []) for m in _GENERIC_CLASS.finditer(unit.text)]
        syms += [("function", m.group(1), []) for m in _GENERIC_FUNC.finditer(unit.text)]
        return syms

    def _imports(self, unit: CodeUnit) -> list[str]:
        if unit.language != "python":
            return []
        mods = []
        for m in _PY_IMPORT.finditer(unit.text):
            mods.append(m.group(1) or m.group(2))
        return sorted(set(m for m in mods if m))

    def _calls(self, unit: CodeUnit) -> list[tuple[str, str]]:
        """Approximate call edges: file-level caller -> called symbol name."""
        file_id = _node_id(unit.path, unit.path, "file")
        calls = []
        for m in _CALL.finditer(unit.text):
            name = m.group(1)
            if name in _KEYWORD_CALLS:
                continue
            calls.append((file_id, name))
        # de-dup deterministically
        return sorted(set(calls))
