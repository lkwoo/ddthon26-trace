"""TagEnricher — derive substantive tags per chunk (Increment 3, U-Tags).

Historically a chunk's ``tags`` held only the literal ``#hashtags`` a human wrote
in the source, so the tag-match relationship channel was almost always empty and
"real relatedness" fell entirely on embedding similarity. This enricher augments
each chunk with tags derived from its actual content, so the tag relationship
captures substantive links (shared symbols, shared links, shared salient terms)
that complement — not duplicate — vector similarity.

Deterministic and LLM-free (NFR-3.1). Tags are **namespaced** so auto-derived tags
never collide with user ``#hashtags`` and downstream consumers can filter by facet:

  * ``<name>``     — user ``#hashtag`` from the source text (unchanged, unprefixed)
  * ``kind:<k>``   — chunk kind (code | section | paragraph | table | sheet)
  * ``lang:<l>``   — programming language (code chunks)
  * ``mod:<stem>`` — source file stem (module name)
  * ``dir:<name>`` — immediate parent directory
  * ``sym:<name>`` — a code symbol the chunk **defines or references** (call sites)
  * ``kw:<term>``  — the chunk's most salient keyword(s) (frequency, stopword-filtered)
  * ``link:<stem>``— a ``[[wikilink]]`` / markdown-link target the chunk points at
"""

from __future__ import annotations

import re
from collections import Counter

from knowledge_store.embedding.keyword import tokenize
from knowledge_store.types import Chunk

# Reuse the analyzer's call-site shape and keyword set so symbol tags line up with
# the code graph's notion of a "call".
_CALL_RE = re.compile(r"([A-Za-z_]\w*)\s*\(")
_IDENT_RE = re.compile(r"^[A-Za-z_]\w*$")
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_MDLINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

# Language keywords / built-ins that look like calls but carry no relatedness signal.
_CALL_STOPWORDS = frozenset({
    "if", "for", "while", "return", "print", "def", "class", "with", "switch",
    "catch", "and", "or", "not", "in", "elif", "else", "await", "yield", "assert",
    "raise", "try", "except", "finally", "import", "from", "lambda", "super",
    "self", "this", "new", "typeof", "sizeof", "len", "str", "int", "float",
    "list", "dict", "set", "tuple", "range",
})

# Common prose / code-noise words that make poor keyword tags.
_KW_STOPWORDS = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can", "her",
    "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man",
    "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let",
    "put", "say", "she", "too", "use", "that", "this", "with", "from", "they",
    "have", "will", "would", "there", "their", "what", "about", "which", "when",
    "into", "then", "than", "them", "these", "some", "such", "only", "other",
    "also", "each", "must", "should", "could", "been", "being", "were", "where",
    "here", "does", "done", "make", "made", "like", "just", "very", "more", "most",
    "none", "true", "false", "value", "type",
})

_MAX_KEYWORDS = 6
_MAX_SYMBOLS = 12
_MIN_KW_LEN = 3


class TagEnricher:
    """Derive namespaced tags from a chunk's content. Pure and deterministic."""

    def enrich(self, chunk: Chunk) -> tuple[str, ...]:
        """Return the chunk's tags augmented with content-derived facets, sorted."""
        tags: set[str] = set(chunk.tags)  # keep the human #hashtags as-is
        text = chunk.text

        tags.add(f"kind:{chunk.kind}")

        stem, parent = self._path_facets(chunk.source_path)
        if stem:
            tags.add(f"mod:{stem}")
        if parent:
            tags.add(f"dir:{parent}")

        language = chunk.metadata.get("lang") or chunk.metadata.get("language")
        is_code = chunk.kind == "code" or bool(language)
        if language:
            tags.add(f"lang:{language}")

        if is_code:
            own = chunk.metadata.get("symbol")
            if isinstance(own, str) and own not in ("", "<module>") and _IDENT_RE.match(own):
                tags.add(f"sym:{own}")
            for name in self._referenced_symbols(text):
                tags.add(f"sym:{name}")

        for term in self._keywords(text):
            tags.add(f"kw:{term}")

        for target in self._link_targets(text):
            tags.add(f"link:{target}")

        return tuple(sorted(tags))

    # -- facet builders ----------------------------------------------------
    @staticmethod
    def _path_facets(source_path: str) -> tuple[str, str]:
        p = source_path.replace("\\", "/")
        segments = [s for s in p.split("/") if s not in ("", ".")]
        if not segments:
            return "", ""
        stem = segments[-1].rsplit(".", 1)[0].lower()
        parent = segments[-2].lower() if len(segments) >= 2 else ""
        return stem, parent

    @staticmethod
    def _referenced_symbols(text: str) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for name in _CALL_RE.findall(text):
            if len(name) < 2 or name.lower() in _CALL_STOPWORDS or name in seen:
                continue
            seen.add(name)
            names.append(name)
            if len(names) >= _MAX_SYMBOLS:
                break
        return names

    @staticmethod
    def _keywords(text: str) -> list[str]:
        counts: Counter[str] = Counter()
        for token in tokenize(text):
            if len(token) < _MIN_KW_LEN or token.isdigit():
                continue
            if token in _KW_STOPWORDS or token in _CALL_STOPWORDS:
                continue
            counts[token] += 1
        # Deterministic salience: count desc, then term asc.
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [term for term, _ in ordered[:_MAX_KEYWORDS]]

    @staticmethod
    def _link_targets(text: str) -> list[str]:
        targets: list[str] = []
        seen: set[str] = set()
        for raw in _WIKILINK_RE.findall(text) + _MDLINK_RE.findall(text):
            key = raw.strip().rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
            if not key or key in seen:
                continue
            seen.add(key)
            targets.append(key)
        return targets
