"""UOW-01 스캐너/파서 테스트 — 분류·제외·경로검증·부분실패 + 데모 스캔."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, strategies as st

from trace.common import Result
from trace.engine import scan_project
from trace.engine.assets import classify, is_test_path

DEMO = Path(__file__).resolve().parents[1] / "demo"


# ---------------------------------------------------------------- 분류 규칙
def test_classify_by_extension():
    assert classify("src/Owner.java", "Owner.java", ".java") == "source"
    assert classify("db/schema.sql", "schema.sql", ".sql") == "sql"
    assert classify("spec.pdf", "spec.pdf", ".pdf") == "pdf"
    assert classify("readme.md", "readme.md", ".md") == "markdown"


def test_classify_openapi_vs_config_by_content():
    assert classify("api.yaml", "api.yaml", ".yaml", "openapi: 3.0.1") == "openapi"
    assert classify("cfg.yaml", "cfg.yaml", ".yaml", "server:\n  port: 8080") == "config"


def test_test_path_detection():
    assert is_test_path("src/test/java/FooTests.java", "FooTests.java")
    assert is_test_path("pkg/foo_test.go", "foo_test.go")
    assert is_test_path("t/test_bar.py", "test_bar.py")
    assert not is_test_path("src/main/Foo.java", "Foo.java")


@given(st.sampled_from([".java", ".py", ".sql", ".pdf", ".md", ".unknownext"]))
def test_classify_never_crashes(ext: str):
    t = classify(f"a{ext}", f"a{ext}", ext)
    assert isinstance(t, str) and t


# ------------------------------------------------------------- 경로 검증
def test_scan_invalid_path_returns_error_result(tmp_path):
    r = scan_project(str(tmp_path / "nope"))
    assert isinstance(r, Result)
    assert r.meta["ok"] is False
    assert "존재하지 않" in r.summary


def test_scan_file_not_dir_returns_error(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("hi")
    r = scan_project(str(f))
    assert r.meta["ok"] is False


# ------------------------------------------------------------- 제외 규칙
def test_exclusions_skip_git_and_node_modules(tmp_path):
    (tmp_path / "keep.py").write_text("x = 1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("secret")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text("y")
    r = scan_project(str(tmp_path))
    paths = [a["path"] for a in r.data["assets"]]
    assert "keep.py" in paths
    assert all(".git" not in p and "node_modules" not in p for p in paths)


# --------------------------------------------------------- 데모 데이터셋 스캔
def test_scan_demo_finds_all_asset_categories():
    r = scan_project(str(DEMO))
    assert r.meta["ok"] is True
    counts = r.data["counts_by_type"]
    # 교차소스 연결(FR-KNOWLEDGE-003): source/sql/openapi/test/pdf 모두 존재
    for t in ["source", "sql", "openapi", "test", "pdf"]:
        assert counts.get(t, 0) >= 1, f"missing asset type {t}: {counts}"


def test_scan_demo_pdf_parsed_ok():
    r = scan_project(str(DEMO))
    pdfs = [a for a in r.data["assets"] if a["type"] == "pdf"]
    assert pdfs and all(a["parse_status"] == "ok" for a in pdfs)
