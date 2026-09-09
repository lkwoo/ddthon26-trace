"""스캔 진입점 (UOW-01, NFR Design P5/P9, BR-FAIL/DET).

- scan_project_assets(path): 내부 API. content 포함 list[Asset] + warnings 반환(오케스트레이션용).
- scan_project(path): 공개 코어 함수. Result(메타만, content 제외 — Q5=A) 반환.

analyze_project(전체 파이프라인)은 UOW-02+ 에서 scan_project_assets 를 소비해 완성한다.
"""

from __future__ import annotations

from pathlib import Path

from trace.common.errors import PathValidationError, error_to_result, sanitize_error
from trace.common.logging import get_logger
from trace.config.scan_settings import get_scan_settings
from trace.config.settings import get_exclusions
from trace.engine.classifier import classify
from trace.engine.parsers import parse_asset
from trace.engine.scanner import (
    ExclusionMatcher,
    is_binary,
    validate_root,
    walk_files,
)
from trace.models.asset import Asset, AssetType, ParseStatus
from trace.models.result import Result, Warning, build_result

_logger = get_logger("trace.engine.scan")


def scan_project_assets(path: str) -> tuple[list[Asset], list[Warning]]:
    """루트를 스캔해 자산(content 포함)과 경고를 반환한다.

    무효 루트는 PathValidationError 를 raise(상위 scan_project 가 오류 Result 로 변환).
    개별 파일 실패는 격리되어 warning 으로 수집되고 스캔은 계속된다(BR-FAIL).
    """
    root = validate_root(path)  # 무효 시 raise (P1)
    settings = get_scan_settings()
    matcher = ExclusionMatcher(get_exclusions())

    assets: list[Asset] = []
    warnings: list[Warning] = []
    total_read = 0

    for file_path in walk_files(root, matcher):
        rel = file_path.relative_to(root).as_posix()
        try:
            size = file_path.stat().st_size
            ext = file_path.suffix.lower()

            # 바이너리(비 PDF)는 건너뜀 (BR-EXCLUDE-002)
            if ext != ".pdf" and is_binary(file_path):
                assets.append(Asset(rel_path=rel, filename=file_path.name,
                                    asset_type=AssetType.TEXT,
                                    parse_status=ParseStatus.SKIPPED, size_bytes=size))
                continue

            # 총량 상한 (P4/BR-SIZE): 초과 시 이후 파일 skip
            if total_read + size > settings.max_total_bytes:
                assets.append(Asset(rel_path=rel, filename=file_path.name,
                                    asset_type=AssetType.TEXT,
                                    parse_status=ParseStatus.SKIPPED, size_bytes=size))
                warnings.append(Warning(code="total_size_cap",
                                        message="총량 상한 초과로 건너뜀", source=rel))
                continue

            result = parse_asset(file_path, size, settings, rel)
            total_read += size if result.content is None else len(result.content.encode("utf-8", "ignore"))
            atype = classify(rel, file_path.name, text=result.content)

            assets.append(Asset(
                rel_path=rel,
                filename=file_path.name,
                asset_type=atype,
                parse_status=result.status,
                size_bytes=size,
                content=result.content,
                truncated=result.truncated,
                error=result.error,
            ))
            warnings.extend(result.warnings)
        except Exception as exc:  # noqa: BLE001 — 파일 단위 실패 격리 (BR-FAIL-001)
            assets.append(Asset(rel_path=rel, filename=file_path.name,
                                asset_type=AssetType.TEXT,
                                parse_status=ParseStatus.FAILED,
                                error=sanitize_error(exc)))
            warnings.append(Warning(code="parse_failed", message="자산 처리 실패", source=rel))

    # 결정적 순서 (BR-DET-001)
    assets.sort(key=lambda a: a.rel_path)
    return assets, warnings


def _tally(assets: list[Asset]) -> dict:
    counts = {"total": len(assets), "parsed": 0, "partial": 0, "skipped": 0, "failed": 0}
    by_type: dict[str, int] = {}
    for a in assets:
        counts[a.parse_status.value] += 1
        by_type[a.asset_type.value] = by_type.get(a.asset_type.value, 0) + 1
    counts["by_type"] = by_type  # type: ignore[assignment]
    return counts


def scan_project(path: str) -> Result:
    """대상 디렉터리를 스캔·분류한다 (공개 코어 함수, Q5=A: data 에 메타만)."""
    try:
        assets, warnings = scan_project_assets(path)
    except PathValidationError as exc:
        _logger.info("scan_project path_invalid")
        return error_to_result(exc)

    counts = _tally(assets)
    root = Path(path).resolve()
    data = {
        "project_name": root.name,
        "root": root.name,  # 절대경로 비노출 (BR-DET-002/SEC)
        "assets": [a.to_meta() for a in assets],
        "counts": counts,
    }
    summary = (
        f"{counts['total']}개 자산 스캔 "
        f"(parsed {counts['parsed']} / partial {counts['partial']} / "
        f"skipped {counts['skipped']} / failed {counts['failed']})"
    )
    settings = get_scan_settings()
    return build_result(summary, data, warnings=warnings,
                        meta={"max_file_bytes": settings.max_file_bytes,
                              "max_total_bytes": settings.max_total_bytes})


__all__ = ["scan_project", "scan_project_assets"]
