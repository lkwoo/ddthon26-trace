"""Reusable Hypothesis domain generators (PBT-07: centralized, structured).

These produce realistic domain objects (documents, chunk lists) that respect the
constraints of the knowledge store, rather than raw primitives.
"""

from __future__ import annotations

from hypothesis import strategies as st

from knowledge_store.types import Chunk

# Text that resembles document/code content: words, punctuation, unicode, and
# structural markers, including boundary cases (empty-ish, whitespace).
text_fragments = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=0x2FFF,
                           blacklist_categories=("Cs",)),
    min_size=0, max_size=120,
)

source_paths = st.builds(
    lambda stem, ext: f"{stem}.{ext}",
    stem=st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=8),
    ext=st.sampled_from(["md", "txt", "py", "rst"]),
)

tag_sets = st.lists(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=6),
    min_size=0, max_size=4,
).map(lambda ts: tuple(sorted(set(ts))))


@st.composite
def chunks(draw, min_size: int = 0, max_size: int = 8) -> list[Chunk]:
    """A list of well-formed chunks with unique ordinals from one source."""
    source = draw(source_paths)
    tags = draw(tag_sets)
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    out: list[Chunk] = []
    for i in range(n):
        text = draw(text_fragments)
        kind = draw(st.sampled_from(["paragraph", "section", "table", "code"]))
        out.append(Chunk.make(text=text, source_path=source, ordinal=i, kind=kind, tags=tags))
    return out


# Multi-paragraph document text used to exercise the chunker.
document_text = st.lists(text_fragments, min_size=0, max_size=10).map(
    lambda paras: "\n\n".join(p for p in paras if p.strip())
)
