"""C2 로컬 지식 엔진 — 스캔·파싱·분류 (UOW-01).

이 패키지는 로컬 프로젝트를 안전하게 스캔하여 자산을 분류하고 텍스트를 추출한다.
구조적 의미 해석(Feature/Claim)은 상위 단위(UOW-02/03)의 몫이다.
"""

from trace.engine.analyze import analyze_project, analyze_task_impact, get_conflicts
from trace.engine.scan import scan_project, scan_project_assets

__all__ = [
    "scan_project", "scan_project_assets",
    "analyze_project", "get_conflicts", "analyze_task_impact",
]
