"""Concrete language parsers + registry (US-E2, US-N4).

MVP ships a stdlib-`ast` Python parser and a regex Markdown parser — both
deterministic and dependency-free (NFR-C3). New languages (e.g. tree-sitter)
plug in via `ParserRegistry.register` with no core changes (NFR-C2, BR-2).
"""

from __future__ import annotations

import ast
import re

from ...domain.models import (
    DocElement,
    ParsedUnit,
    Reference,
    SourceFile,
    Span,
    Symbol,
    make_symbol_id,
)
from ...ports.parser_port import LanguageParserPort


# --------------------------------------------------------------------------- #
# Python (stdlib ast)
# --------------------------------------------------------------------------- #
class PythonAstParser(LanguageParserPort):
    def supported_extensions(self) -> set[str]:
        return {".py"}

    def parse(self, file: SourceFile) -> ParsedUnit:
        tree = ast.parse(file.content)  # SyntaxError propagates -> caller isolates
        path = file.path
        file_id = make_symbol_id(path, "file", path)
        symbols: list[Symbol] = [
            Symbol(
                id=file_id,
                kind="file",
                name=path.rsplit("/", 1)[-1],
                qualified_name=path,
                location=Span(1, 0, max(1, _last_line(tree)), 0),
            )
        ]
        references: list[Reference] = []
        docs: list[DocElement] = []

        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            docs.append(DocElement("docstring", mod_doc, Span(1, 0, 1, 0)))

        self._visit_body(tree.body, path, prefix="", enclosing=file_id,
                         symbols=symbols, references=references, docs=docs)

        # Module-level imports attributed to the file symbol.
        for node in tree.body:
            self._collect_imports(node, file_id, references)

        return ParsedUnit(
            file=file,
            symbols=tuple(symbols),
            references=tuple(references),
            doc_elements=tuple(docs),
        )

    def _visit_body(self, body, path, prefix, enclosing, symbols, references, docs):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qname = f"{prefix}{node.name}" if prefix else node.name
                is_class = isinstance(node, ast.ClassDef)
                kind = "class" if is_class else ("method" if prefix else "function")
                sym_id = make_symbol_id(path, kind, qname)
                span = Span(node.lineno, node.col_offset,
                            getattr(node, "end_lineno", node.lineno) or node.lineno,
                            getattr(node, "end_col_offset", 0) or 0)
                symbols.append(Symbol(sym_id, kind, node.name, qname, span))

                doc = ast.get_docstring(node)
                if doc:
                    docs.append(DocElement("docstring", doc, span))

                # Calls within this definition are attributed to it.
                for callee, loc in _iter_calls(node):
                    references.append(Reference(sym_id, callee, "call", loc))

                # Recurse for nested defs / methods.
                nested_prefix = f"{qname}." if is_class else f"{qname}."
                self._visit_body(node.body, path, nested_prefix, sym_id,
                                 symbols, references, docs)

    @staticmethod
    def _collect_imports(node, file_id, references):
        if isinstance(node, ast.Import):
            for alias in node.names:
                references.append(
                    Reference(file_id, alias.name, "import",
                              Span(node.lineno, node.col_offset, node.lineno, node.col_offset))
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            references.append(
                Reference(file_id, mod, "dependency",
                          Span(node.lineno, node.col_offset, node.lineno, node.col_offset))
            )


def _iter_calls(defn):
    """Yield (callee_name, span) for direct calls inside a definition body,
    excluding calls nested inside further function/class defs."""
    for child in defn.body:
        for node in ast.walk(child):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # nested defs handled by recursion; skip their inner calls here
                continue
            if isinstance(node, ast.Call):
                name = _call_name(node.func)
                if name:
                    loc = Span(getattr(node, "lineno", 1), getattr(node, "col_offset", 0),
                               getattr(node, "lineno", 1), getattr(node, "col_offset", 0))
                    yield name, loc


def _call_name(func) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _last_line(tree) -> int:
    lines = [getattr(n, "end_lineno", 0) or 0 for n in ast.walk(tree)]
    return max(lines) if lines else 1


# --------------------------------------------------------------------------- #
# Markdown (regex headings)
# --------------------------------------------------------------------------- #
_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


class MarkdownParser(LanguageParserPort):
    def supported_extensions(self) -> set[str]:
        return {".md", ".markdown"}

    def parse(self, file: SourceFile) -> ParsedUnit:
        path = file.path
        file_id = make_symbol_id(path, "file", path)
        symbols = (
            Symbol(file_id, "file", path.rsplit("/", 1)[-1], path,
                   Span(1, 0, max(1, file.content.count("\n") + 1), 0)),
        )
        docs: list[DocElement] = []
        for i, line in enumerate(file.content.splitlines(), start=1):
            m = _HEADING.match(line)
            if m:
                level = len(m.group(1))
                docs.append(DocElement("heading", m.group(2), Span(i, 0, i, len(line)), level))
        return ParsedUnit(file=file, symbols=symbols, references=(), doc_elements=tuple(docs))


# --------------------------------------------------------------------------- #
# Registry (Strategy pattern)
# --------------------------------------------------------------------------- #
class ParserRegistry:
    def __init__(self) -> None:
        self._by_ext: dict[str, LanguageParserPort] = {}

    def register(self, parser: LanguageParserPort) -> None:
        for ext in parser.supported_extensions():
            self._by_ext[ext.lower()] = parser

    def for_file(self, path: str) -> LanguageParserPort | None:
        dot = path.rfind(".")
        if dot < 0:
            return None
        return self._by_ext.get(path[dot:].lower())

    def supported_extensions(self) -> set[str]:
        return set(self._by_ext.keys())


def default_registry() -> ParserRegistry:
    reg = ParserRegistry()
    reg.register(PythonAstParser())
    reg.register(MarkdownParser())
    return reg
