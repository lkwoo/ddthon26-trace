"""PBT-02 — Chunker serialize/deserialize round-trip (NFR-8.2).

Property: for any well-formed chunk list, ``deserialize(serialize(chunks))``
reproduces the exact chunk list. Also verified on chunks emitted by the chunker
from arbitrary document text (end-to-end round-trip).
"""

from hypothesis import given, settings

from knowledge_store.ingestion.chunker import Chunker
from knowledge_store.types import ExtractionResult, Status
from tests import generators as gen


@given(chunks=gen.chunks())
@settings(max_examples=200)
def test_serialize_deserialize_round_trip(chunks):
    chunker = Chunker()
    restored = chunker.deserialize(chunker.serialize(chunks))
    assert restored == chunks


@given(chunks=gen.chunks())
@settings(max_examples=100)
def test_serialize_is_deterministic(chunks):
    chunker = Chunker()
    assert chunker.serialize(chunks) == chunker.serialize(chunks)


@given(text=gen.document_text)
@settings(max_examples=150)
def test_chunk_then_round_trip(text):
    chunker = Chunker()
    ex = ExtractionResult(status=Status.OK, source_path="doc.md", format="md", text=text)
    produced = chunker.chunk(ex)
    restored = chunker.deserialize(chunker.serialize(produced))
    assert restored == produced
