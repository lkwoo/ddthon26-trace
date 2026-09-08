"""C2 로컬 지식 엔진 — 코어 함수의 소유자 (오케스트레이션 진입점).

코어 함수(component-methods.md):
- scan_project           (UOW-01, 구현됨)
- analyze_project        (UOW-02, 파이프라인)
- list_features          (UOW-02)
- get_feature_knowledge  (UOW-02)
- get_conflicts          (UOW-03)
- analyze_task_impact    (UOW-04)

MCP 서버(C1)·CLI(C9)는 이 모듈의 함수만 호출한다(NFR-CORE-001/002).
"""

from __future__ import annotations

from trace.engine.scanner import collect_assets, scan_project

__all__ = ["scan_project", "collect_assets"]
