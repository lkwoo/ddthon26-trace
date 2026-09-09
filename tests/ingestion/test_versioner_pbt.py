"""PBT-03 — ChunkVersioner signature determinism & matching invariants.

Properties:
  * identical text always yields an identical MinHash signature (reproducible)
  * a signature is fully self-similar (Jaccard estimate == 1.0) when non-empty
  * two chunks with identical text match with similarity 1.0
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from knowledge_store.ingestion.versioner import (
    ChunkVersioner, estimate_jaccard, minhash_signature,
)
from knowledge_store.types import Chunk, Status
from tests import generators as gen


@given(text=gen.text_fragments)
@settings(max_examples=200)
def test_signature_is_deterministic(text):
    assert minhash_signature(text) == minhash_signature(text)


@given(text=gen.text_fragments)
@settings(max_examples=200)
def test_signature_self_similarity(text):
    sig = minhash_signature(text)
    # Non-empty content is fully self-similar; empty content degenerates to 0-vec.
    if any(sig):
        assert estimate_jaccard(sig, sig) == 1.0


@given(text=st.text(min_size=6, max_size=200))
@settings(max_examples=100)
def test_identical_chunks_match(text):
    a = Chunk.make(text=text, source_path="a.md", ordinal=0, kind="paragraph")
    b = Chunk.make(text=text, source_path="a.md", ordinal=0, kind="paragraph")
    versioner = ChunkVersioner(chunk_repo=None)  # match() needs no repo
    result = versioner.match(b, [a])
    assert result.status == Status.OK
    assert result.similarity == 1.0
    assert result.matched_chunk_id == a.id
