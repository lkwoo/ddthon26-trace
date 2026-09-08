"""프로젝트 스캐너 (UOW-01, C2) — scan_project 코어 함수 + 자산 수집.

책임: 로컬 디렉터리 재귀 스캔, 제외 규칙 적용(FR-PROJECT-003), 자산 분류·파싱,
경로 검증(NFR-SEC-004), 부분 실패 허용(FR-ANALYSIS-003). 로컬 파일시스템 직접 접근은
엔진에 국한된다(NFR-LOCAL-001).
"""

from __future__ import annotations

from pathlib import Path

from trace.common import InvalidPathError, Result, get_logger
from trace.config import Config
from trace.engine.assets import Asset, classify
from trace.engine.parsers import parse_asset

_log = get_logger("trace.engine.scanner")

# 콘텐츠 스니핑(OpenAPI 판별)을 시도할 확장자
_SNIFF_EXTS = {".yaml", ".yml", ".json"}


def _validate_path(path: str) -> Path:
    """경로 존재·디렉터리 검증 (NFR-SEC-004). 실패 시 InvalidPathError."""
    p = Path(path).expanduser()
    if not p.exists():
        raise InvalidPathError(f"경로가 존재하지 않습니다: {path}")
    if not p.is_dir():
        raise InvalidPathError(f"디렉터리가 아닙니다: {path}")
    return p.resolve()


def _is_excluded(rel_parts: tuple[str, ...], exclusions: set[str]) -> bool:
    return any(part in exclusions for part in rel_parts)


def collect_assets(path: str, config: Config | None = None) -> tuple[list[Asset], list[str]]:
    """디렉터리를 스캔해 파싱된 Asset 목록과 warning 목록을 반환한다.

    경로 검증 실패는 InvalidPathError를 던진다(호출자가 Result.error로 변환).
    """
    config = config or Config()
    root = _validate_path(path)
    exclusions = set(config.exclusions)
    assets: list[Asset] = []
    warnings: list[str] = []

    for entry in sorted(root.rglob("*")):
        if not entry.is_file():
            continue
        rel = entry.relative_to(root).as_posix()
        rel_parts = entry.relative_to(root).parts
        if _is_excluded(rel_parts, exclusions):
            continue
        ext = entry.suffix.lower()

        sniff = ""
        if ext in _SNIFF_EXTS:
            try:
                with entry.open("r", encoding="utf-8", errors="replace") as fh:
                    sniff = fh.read(4096)
            except OSError:
                sniff = ""

        asset_type = classify(rel, entry.name, ext, sniff)
        if asset_type == "unknown":
            continue  # 바이너리·기타 무관 파일은 자산으로 취급하지 않음

        content, error = parse_asset(entry, asset_type)
        asset = Asset(
            path=rel,
            abspath=str(entry),
            type=asset_type,
            filename=entry.name,
            content=content,
            parse_status="ok" if not error else "error",
            error=error,
        )
        if error:
            msg = f"파싱 실패: {rel} ({error})"
            warnings.append(msg)
            _log.warning(msg)
        assets.append(asset)

    return assets, warnings


def scan_project(path: str, config: Config | None = None) -> Result:
    """대상 디렉터리를 스캔·분류·파싱한다 (FR-PROJECT-001/002).

    data: {project_name, assets:[{path,type,filename,parse_status}], counts_by_type}
    무효/접근불가 경로는 사용자 친화 오류 Result로 반환한다(NFR-SEC-004, NFR-REL-002).
    """
    try:
        root = _validate_path(path)
    except InvalidPathError as exc:
        return Result.error(str(exc))

    assets, warnings = collect_assets(path, config)
    counts: dict[str, int] = {}
    for a in assets:
        counts[a.type] = counts.get(a.type, 0) + 1

    ok = sum(1 for a in assets if a.parse_status == "ok")
    summary = (
        f"'{root.name}' 스캔 완료: 자산 {len(assets)}개 발견, {ok}개 파싱 성공"
        + (f", {len(warnings)}개 경고" if warnings else "")
    )
    result = Result.ok(
        summary,
        data={
            "project_name": root.name,
            "project_path": str(root),
            "assets": [a.summary_dict() for a in assets],
            "counts_by_type": counts,
        },
        meta={"assets_count": len(assets), "parsed_ok": ok},
    )
    result.warnings.extend(warnings)
    return result


__all__ = ["scan_project", "collect_assets"]
