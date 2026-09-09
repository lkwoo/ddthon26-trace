"""부분 실패 강등용 Warning 누적기 (UOW-0F, NFR Design P4).

BR-WARN-001: Warning은 {code, message, source?} 구조 (models.result.Warning).
NFR-0F-REL-2: 비치명 실패는 collector.add(...) 후 파이프라인 진행, 마지막에 build_result에 취합.
치명 실패(경로 이탈·키 부재)는 collector가 아니라 raise 한다.
"""

from __future__ import annotations

from trace.models.result import Warning

# 사전 정의 코드 집합 (BR-WARN-001) — 상위 단위가 필터/집계에 사용
CODE_PARSE_PARTIAL = "PARSE_PARTIAL"
CODE_LLM_LOW_CONFIDENCE = "LLM_LOW_CONFIDENCE"
CODE_LLM_RETRY_EXHAUSTED = "LLM_RETRY_EXHAUSTED"
CODE_PATH_SKIPPED = "PATH_SKIPPED"


class WarningCollector:
    """파이프라인 진행 중 비치명 경고를 누적한다 (append-only)."""

    def __init__(self) -> None:
        self._warnings: list[Warning] = []

    def add(self, code: str, message: str, source: str | None = None) -> None:
        self._warnings.append(Warning(code=code, message=message, source=source))

    def extend(self, warnings: list[Warning]) -> None:
        self._warnings.extend(warnings)

    def to_list(self) -> list[Warning]:
        """누적된 경고의 사본을 반환 (원본 불변 보호)."""
        return list(self._warnings)

    def __len__(self) -> int:
        return len(self._warnings)

    def __bool__(self) -> bool:
        return bool(self._warnings)
