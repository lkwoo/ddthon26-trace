"""UOW-01 스캐너 예제 테스트 — demo/ 스캔, 무효 경로, 제외 규칙 (BR-*)."""

from __future__ import annotations

from pathlib import Path

from trace.engine.scan import scan_project, scan_project_assets
from trace.models.asset import AssetType, ParseStatus

DEMO = Path(__file__).resolve().parents[1] / "demo"


def test_scan_demo_returns_diverse_assets() -> None:
    result = scan_project(str(DEMO))
    counts = result.data["counts"]
    assert counts["total"] >= 8
    assert counts["failed"] == 0
    # 6종 이상 자산 유형 커버 (파서 커버리지)
    by_type = counts["by_type"]
    for t in ("source", "openapi", "sql", "config", "test", "pdf", "markdown"):
        assert t in by_type, f"유형 {t} 누락"


def test_scan_demo_pdf_is_parsed() -> None:
    assets, _ = scan_project_assets(str(DEMO))
    pdfs = [a for a in assets if a.asset_type == AssetType.PDF]
    # 4개 도메인 스펙 PDF (owner/vet/visit/billing)
    assert len(pdfs) == 4
    assert all(p.parse_status == ParseStatus.PARSED for p in pdfs)
    owner_spec = next(p for p in pdfs if "owner-management-spec" in p.rel_path)
    assert owner_spec.content and "20 characters" in owner_spec.content  # PDF 텍스트 추출 확인


def test_scan_result_data_excludes_content() -> None:
    # Q5=A: Result.data.assets 에는 content 필드가 없어야 한다
    result = scan_project(str(DEMO))
    for meta in result.data["assets"]:
        assert "content" not in meta
        assert set(meta) == {"rel_path", "filename", "asset_type", "parse_status",
                             "size_bytes", "truncated"}


def test_scan_is_deterministic_and_sorted() -> None:
    a1, _ = scan_project_assets(str(DEMO))
    a2, _ = scan_project_assets(str(DEMO))
    paths1 = [a.rel_path for a in a1]
    paths2 = [a.rel_path for a in a2]
    assert paths1 == paths2
    assert paths1 == sorted(paths1)  # BR-DET-001


def test_invalid_path_returns_error_result() -> None:
    result = scan_project(str(DEMO / "does-not-exist"))
    assert result.meta.get("error_code") == "PATH_VALIDATION_ERROR"
    assert result.data == {}


def test_file_path_is_rejected_as_root() -> None:
    # 디렉터리가 아닌 파일을 루트로 주면 오류 (NFR-SEC-004)
    a_file = DEMO / "README.md"
    result = scan_project(str(a_file))
    assert result.meta.get("error_code") == "PATH_VALIDATION_ERROR"


def test_exclusions_prune_git_and_node_modules(tmp_path: Path) -> None:
    (tmp_path / "keep").mkdir()
    (tmp_path / "keep" / "a.py").write_text("print(1)\n", encoding="utf-8")
    for excluded in (".git", "node_modules", "__pycache__"):
        d = tmp_path / excluded
        d.mkdir()
        (d / "junk.py").write_text("x=1\n", encoding="utf-8")

    assets, _ = scan_project_assets(str(tmp_path))
    rels = {a.rel_path for a in assets}
    assert "keep/a.py" in rels
    assert not any(r.startswith((".git/", "node_modules/", "__pycache__/")) for r in rels)


def test_empty_project_is_not_an_error(tmp_path: Path) -> None:
    result = scan_project(str(tmp_path))
    assert "error_code" not in result.meta
    assert result.data["counts"]["total"] == 0
