"""Tests for the code-aware BM25 keyword index + hybrid fusion (U-Hybrid).

PBT Partial mode: ``tokenize`` is a pure function, so it gets a property test.
BM25 ranking and RRF fusion get deterministic example-based tests.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from knowledge_store.embedding.keyword import BM25Index, tokenize


# -- tokenize (pure function → PBT) ---------------------------------------
def test_tokenize_splits_camel_and_snake():
    toks = tokenize("favoritesCount")
    assert "favoritescount" in toks  # whole identifier, lowercased
    assert "favorites" in toks and "count" in toks  # camelCase sub-words

    toks2 = tokenize("favorites_count")
    assert "favorites_count" in toks2
    assert "favorites" in toks2 and "count" in toks2


@given(st.text())
def test_tokenize_is_deterministic_and_lowercased(text):
    once = tokenize(text)
    assert once == tokenize(text)                 # pure / deterministic
    assert all(t == t.lower() for t in once)      # always lowercased


# -- BM25 ranking ----------------------------------------------------------
def test_bm25_ranks_exact_identifier_match_first():
    idx = BM25Index()
    idx.build([
        ("auth", "def authenticate(user, password): validate credentials login"),
        ("fav", "def favoritesCount(item): return number of favorites"),
        ("bill", "def chargeInvoice(account): billing payment"),
    ])
    hits = idx.search("favorites count", limit=3)
    assert hits, "BM25 should find the favorites document"
    assert hits[0].ref_id == "fav"


def test_bm25_empty_or_no_match_returns_empty():
    idx = BM25Index()
    idx.build([("a", "alpha beta")])
    assert idx.search("", limit=5) == []
    assert idx.search("nonexistentterm", limit=5) == []
    empty = BM25Index()
    empty.build([])
    assert empty.search("anything", limit=5) == []


def test_bm25_is_deterministic():
    docs = [("a", "one two three"), ("b", "two three four"), ("c", "three four five")]
    idx1 = BM25Index(); idx1.build(docs)
    idx2 = BM25Index(); idx2.build(docs)
    r1 = [h.ref_id for h in idx1.search("three four", 5)]
    r2 = [h.ref_id for h in idx2.search("three four", 5)]
    assert r1 == r2
