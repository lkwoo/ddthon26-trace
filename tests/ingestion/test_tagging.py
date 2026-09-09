"""TagEnricher — content-derived tag facets (Increment 3, U-Tags).

Verifies that chunk tags are enriched beyond literal ``#hashtags`` with the
selected facets (code symbols, keywords, path/language/kind, link targets),
that enrichment is deterministic and preserves chunk identity, and that human
hashtags survive untouched.
"""

from knowledge_store.ingestion.chunker import Chunker
from knowledge_store.ingestion.extractors import MarkdownExtractor
from knowledge_store.ingestion.tagging import TagEnricher
from knowledge_store.types import Chunk, ExtractionResult, Status


def _code(text: str, path: str = "src/pkg/app.py") -> list[Chunk]:
    ex = ExtractionResult(status=Status.OK, source_path=path, format="code",
                          text=text, is_code=True, language="python")
    return Chunker().chunk(ex)


def test_code_chunk_gets_symbol_language_path_and_keyword_facets():
    chunks = _code(
        "def compute_total(a, b):\n    return a + b\n\n"
        "def caller():\n    return compute_total(1, 2)\n"
    )
    by_symbol = {c.metadata.get("symbol"): set(c.tags) for c in chunks}

    caller_tags = by_symbol["caller"]
    # defines-or-references symbols
    assert "sym:caller" in caller_tags
    assert "sym:compute_total" in caller_tags  # call site linked to the definition
    # path / language / kind facets
    assert "lang:python" in caller_tags
    assert "kind:code" in caller_tags
    assert "mod:app" in caller_tags
    assert "dir:pkg" in caller_tags
    # a salient keyword, but no bare language keywords as noise
    assert any(t.startswith("kw:") for t in caller_tags)
    assert "kw:def" not in caller_tags and "kw:return" not in caller_tags


def test_hashtags_preserved_and_link_targets_tagged(tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("# Notes\nSee [[Design Doc]] here.\n#alpha\n", encoding="utf-8")
    ex = MarkdownExtractor().extract(p)
    assert "alpha" in ex.tags  # extractor found the #hashtag
    chunks = Chunker().chunk(ex)
    all_tags = set().union(*(set(c.tags) for c in chunks))
    assert "alpha" in all_tags               # human #hashtag survives, unprefixed
    assert "link:design doc" in all_tags     # wikilink target normalized to a link facet
    assert "kind:section" in all_tags or "kind:paragraph" in all_tags


def test_enrichment_is_deterministic_and_preserves_id():
    text = "def f():\n    return helper()\n"
    first = _code(text)
    second = _code(text)
    assert [c.id for c in first] == [c.id for c in second]
    assert [c.tags for c in first] == [c.tags for c in second]
    # id is derived from path/ordinal/kind/text, never tags: enrich() must not move it
    enricher = TagEnricher()
    for c in first:
        assert set(c.tags) >= set(enricher.enrich(c))  # idempotent superset (already enriched)


def test_module_gap_chunk_has_no_own_symbol_but_still_faceted():
    chunks = _code("import os\n\ndef f():\n    return 1\n")
    module_chunks = [c for c in chunks if c.metadata.get("symbol") == "<module>"]
    assert module_chunks, "import region should form a <module> chunk"
    tags = set(module_chunks[0].tags)
    assert "sym:<module>" not in tags        # placeholder is never a symbol tag
    assert "lang:python" in tags and "mod:app" in tags
