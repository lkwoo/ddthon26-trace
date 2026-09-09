"""UOW-01 스캐너 속성 기반 테스트 (PBT 확장, PBT-01-A~D).

hypothesis 로 스캐너/파서의 핵심 불변식 4가지를 검증한다.
결정적 재현을 위해 derandomize=True 로 실행한다.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from trace.engine.classifier import classify
from trace.engine.scan import scan_project_assets
from trace.models.asset import AssetType, ParseStatus

# 파일명 구성용 전략
_names = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="._-"),
    min_size=1,
    max_size=20,
)
_exts = st.sampled_from(
    ["", ".java", ".py", ".sql", ".pdf", ".md", ".yaml", ".yml", ".json",
     ".properties", ".txt", ".xyz", ".TEST", ".Java"]
)

PBT = settings(derandomize=True, max_examples=60, deadline=None)


# --------------------------------------------------------------------------- #
# PBT-01-A: 분류 전결정성 — classify 는 항상 유효한 AssetType 하나 반환(예외/None 없음)
# --------------------------------------------------------------------------- #
@PBT
@given(stem=_names, ext=_exts, depth=st.integers(min_value=0, max_value=4))
def test_classify_is_total(stem: str, ext: str, depth: int) -> None:
    filename = f"{stem}{ext}"
    rel = "/".join(["d"] * depth + [filename]) if depth else filename
    result = classify(rel, filename)
    assert isinstance(result, AssetType)


# --------------------------------------------------------------------------- #
# PBT-01-B: 경로 안전성 — 결과 자산의 rel_path 는 항상 루트 내부(상대·비탈출)
# --------------------------------------------------------------------------- #
@PBT
@given(
    files=st.lists(
        st.tuples(
            st.lists(_names, min_size=0, max_size=3),  # 하위 디렉터리 경로
            _names,                                     # 파일 stem
            st.sampled_from([".py", ".txt", ".md", ".sql", ".yaml"]),
        ),
        min_size=0,
        max_size=8,
    ),
)
def test_scan_never_escapes_root(tmp_path_factory, files) -> None:  # type: ignore[no-untyped-def]
    root = tmp_path_factory.mktemp("root")
    outside = tmp_path_factory.mktemp("outside")
    (outside / "secret.txt").write_text("SECRET\n", encoding="utf-8")

    for dirs, stem, ext in files:
        target = root
        for d in dirs:
            target = target / d
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{stem}{ext}").write_text("data\n", encoding="utf-8")

    assets, _ = scan_project_assets(str(root))
    for a in assets:
        # 상대경로이며 상위 탈출(..)/절대경로가 아님
        assert not a.rel_path.startswith(("/", "\\"))
        assert ".." not in Path(a.rel_path).parts
        # 실제 파일이 루트 내부에 존재
        assert (root / a.rel_path).resolve().is_relative_to(root.resolve())
    # 루트 밖 파일은 결과에 없음
    assert all("secret.txt" != a.filename for a in assets)


# --------------------------------------------------------------------------- #
# PBT-01-C: 부분 실패 격리 — 일부 파일이 깨져도 scan 은 예외 없이 완료
# --------------------------------------------------------------------------- #
@PBT
@given(
    good=st.integers(min_value=0, max_value=5),
    bad=st.integers(min_value=0, max_value=5),
)
def test_partial_failure_is_isolated(tmp_path_factory, good: int, bad: int) -> None:  # type: ignore[no-untyped-def]
    root = tmp_path_factory.mktemp("mixed")
    for i in range(good):
        (root / f"good_{i}.txt").write_text("hello\n", encoding="utf-8")
    for i in range(bad):
        # 널바이트 포함 → 비-PDF 바이너리 → skipped(예외 아님). scan 은 완료해야 함.
        (root / f"bad_{i}.dat").write_bytes(b"\x00\x01\x02BINARY")

    assets, warnings = scan_project_assets(str(root))  # 예외가 나면 실패
    # good 파일은 모두 parsed
    parsed = [a for a in assets if a.parse_status == ParseStatus.PARSED]
    assert len(parsed) >= good
    # 전체 자산 수는 good+bad (bad 는 skipped 로 표기)
    assert len(assets) == good + bad


# --------------------------------------------------------------------------- #
# PBT-01-D: 결정성/멱등 — 동일 트리 2회 스캔 시 assets(순서 포함) 동일
# --------------------------------------------------------------------------- #
@PBT
@given(
    files=st.lists(
        st.tuples(_names, st.sampled_from([".py", ".txt", ".md", ".sql"])),
        min_size=0,
        max_size=8,
        unique_by=lambda t: t[0] + t[1],
    ),
)
def test_scan_is_idempotent(tmp_path_factory, files) -> None:  # type: ignore[no-untyped-def]
    root = tmp_path_factory.mktemp("idem")
    for stem, ext in files:
        (root / f"{stem}{ext}").write_text("x\n", encoding="utf-8")

    a1, _ = scan_project_assets(str(root))
    a2, _ = scan_project_assets(str(root))
    assert [a.rel_path for a in a1] == [a.rel_path for a in a2]
    assert [a.asset_type for a in a1] == [a.asset_type for a in a2]
