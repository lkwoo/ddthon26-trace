"""PBT-10 example-based tests for extractors (US-1.1, Application Design Q5/Q7)."""

from pathlib import Path

from knowledge_store.ingestion.extractors import default_registry
from knowledge_store.types import Status


def test_markdown_extracts_text_and_tags(tmp_path: Path):
    p = tmp_path / "note.md"
    p.write_text("# Title\nBody with #alpha and #beta tags.\n", encoding="utf-8")
    result = default_registry().extract(p)
    assert result.status == Status.OK
    assert result.format == "markdown"
    assert result.tags == ("alpha", "beta")
    assert not result.is_code


def test_code_detects_language(tmp_path: Path):
    p = tmp_path / "mod.py"
    p.write_text("def f():\n    return 1\n", encoding="utf-8")
    result = default_registry().extract(p)
    assert result.status == Status.OK
    assert result.is_code
    assert result.language == "python"


def test_csv_produces_table(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    result = default_registry().extract(p)
    assert result.status == Status.OK
    assert result.tables == [[["a", "b"], ["1", "2"]]]


def test_unsupported_format_is_typed_not_raised(tmp_path: Path):
    p = tmp_path / "image.heic"
    p.write_bytes(b"\x00\x01")
    result = default_registry().extract(p)
    assert result.status == Status.UNSUPPORTED
    assert "unsupported" in result.message.lower()
