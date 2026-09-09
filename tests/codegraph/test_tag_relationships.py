"""TagMatchStrategy — selectivity-weighted, bidirectional tag relationships.

Increment 3 (U-Tags) makes the tag channel substantive: a shared code symbol or
link is a strong edge; a shared broad facet (lang/kind) is not an edge at all;
rarer shared tags weigh more than common ones; and edges are emitted both ways so
``read_relationships`` finds them from either endpoint.
"""

from knowledge_store.codegraph.relationships import TagMatchStrategy
from knowledge_store.types import Chunk, RelationType


def _chunk(cid: str, tags: tuple[str, ...]) -> Chunk:
    return Chunk(id=cid, text="", source_path="x.py", ordinal=0, kind="code", tags=tags)


def _score(rels, a, b):
    for r in rels:
        if r.src_id == a and r.dst_id == b:
            return r.score
    return None


def test_shared_symbol_beats_shared_broad_facet():
    chunks = [
        _chunk("a", ("sym:compute", "lang:python", "kind:code")),
        _chunk("b", ("sym:compute", "lang:python", "kind:code")),
        _chunk("c", ("lang:python", "kind:code")),  # only broad facets in common
    ]
    rels = TagMatchStrategy().build(chunks)
    # a<->b share a rare symbol -> strong, bidirectional edge
    assert _score(rels, "a", "b") == 1.0
    assert _score(rels, "b", "a") == 1.0
    # c shares only lang/kind with everyone -> no edge (facet-only, zero weight)
    assert _score(rels, "a", "c") is None
    assert _score(rels, "c", "a") is None


def test_rarer_tag_scores_higher_than_common_one():
    # 'sym:rare' shared by exactly 2 chunks; 'sym:common' shared by 4.
    chunks = [
        _chunk("a", ("sym:rare", "sym:common")),
        _chunk("b", ("sym:rare", "sym:common")),
        _chunk("c", ("sym:common",)),
        _chunk("d", ("sym:common",)),
    ]
    rels = TagMatchStrategy().build(chunks)
    ab = _score(rels, "a", "b")   # shares rare (df2 ->1.0) + common (df4 ->1/3), capped at 1.0
    cd = _score(rels, "c", "d")   # shares only common (df4 -> 1/3)
    assert ab == 1.0
    assert 0.3 < cd < 0.4
    assert ab > cd


def test_low_selectivity_pairs_below_threshold_are_dropped():
    # A keyword shared by many chunks yields a tiny per-pair score -> filtered out.
    chunks = [_chunk(str(i), ("kw:widget",)) for i in range(9)]
    rels = TagMatchStrategy(min_score=0.1).build(chunks)
    assert rels == []  # kw weight 0.6 / (9-1) = 0.075 < 0.1


def test_all_edges_are_tag_typed_and_bidirectional():
    chunks = [
        _chunk("a", ("sym:x",)),
        _chunk("b", ("sym:x",)),
    ]
    rels = TagMatchStrategy().build(chunks)
    assert {(r.src_id, r.dst_id) for r in rels} == {("a", "b"), ("b", "a")}
    assert all(r.type == RelationType.TAG for r in rels)
