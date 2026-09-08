"""C2 로컬 지식 엔진 — 코어 함수의 소유자 (오케스트레이션 진입점).

코어 함수(component-methods.md):
- scan_project           (UOW-01, 구현됨)
- analyze_project        (UOW-02, 파이프라인, 구현됨)
- list_features          (UOW-02, 구현됨)
- get_feature_knowledge  (UOW-02, 구현됨)
- get_conflicts          (UOW-03, 구현됨)
- analyze_task_impact    (UOW-04)

MCP 서버(C1)·CLI(C9)는 이 모듈의 함수만 호출한다(NFR-CORE-001/002).
"""

from __future__ import annotations

from typing import Any

from trace.engine.pipeline import (
    analyze_project,
    get_feature_knowledge,
    list_features,
    register_enrich_hook,
)
from trace.engine.scanner import collect_assets, scan_project

__all__ = [
    "scan_project",
    "collect_assets",
    "analyze_project",
    "list_features",
    "get_feature_knowledge",
    "get_conflicts",
    "register_enrich_hook",
]


def __getattr__(name: str) -> Any:
    """get_conflicts는 UOW-03(trace.conflict)에 있으므로 지연 재노출한다(순환 임포트 방지)."""
    if name == "get_conflicts":
        from trace.conflict import get_conflicts

        return get_conflicts
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
