"""공통 계약 — Result envelope, 오류 타입, 로깅 (UOW-0F).

모든 코어 함수는 `Result`를 반환한다. 핵심 우선 순서(NFR-MCP-UX-002):
summary → data → conflicts → impact → evidence → warnings → meta.
사람이 읽는 summary와 기계 판독 data를 함께 담아 에이전트가 그대로 설명할 수 있게 한다.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

# ----------------------------------------------------------------------------
# 오류 타입 (§17, NFR-REL-002: 사람이 읽는 오류 + 진단)
# ----------------------------------------------------------------------------


class TraceError(Exception):
    """TRACE 도메인 오류의 기반. 사용자 친화 메시지를 담는다."""


class InvalidPathError(TraceError):
    """분석 대상 경로가 없거나 디렉터리가 아님 (NFR-SEC-004 경로 검증)."""


class ConfigError(TraceError):
    """설정/환경 구성 오류 (예: live 모드인데 API 키 없음)."""


class LLMError(TraceError):
    """LLM 호출/구조화 출력 검증 실패 (§17.4)."""


class KnowledgeNotFoundError(TraceError):
    """요청한 Feature 지식을 찾을 수 없음."""


# ----------------------------------------------------------------------------
# Result envelope (공통 봉투, Q4=A)
# ----------------------------------------------------------------------------


@dataclass
class Result:
    """코어 함수 공통 반환 봉투. `to_dict`가 MCP JSON 직렬화의 정본 형식."""

    summary: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    impact: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def add_warning(self, message: str) -> "Result":
        """부분 실패/저신뢰 경고 추가 (FR-ANALYSIS-003). 체이닝 가능."""
        self.warnings.append(message)
        return self

    def to_dict(self) -> dict[str, Any]:
        """핵심 우선 순서로 직렬화 (NFR-MCP-UX-002)."""
        return {
            "summary": self.summary,
            "data": self.data,
            "conflicts": self.conflicts,
            "impact": self.impact,
            "evidence": self.evidence,
            "warnings": self.warnings,
            "meta": self.meta,
        }

    @classmethod
    def error(cls, message: str, **meta: Any) -> "Result":
        """사용자 친화 오류 Result. 예외를 봉투로 감싸 어댑터가 그대로 노출."""
        return cls(summary=message, meta={"ok": False, **meta}, warnings=[message])

    @classmethod
    def ok(cls, summary: str, **kwargs: Any) -> "Result":
        r = cls(summary=summary, **kwargs)
        r.meta.setdefault("ok", True)
        return r


# ----------------------------------------------------------------------------
# 로깅 (NFR-LOG-001: 시크릿 비노출)
# ----------------------------------------------------------------------------

_SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9\-_]+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*\S+"),
]


def mask_secrets(text: str) -> str:
    """로그/결과에 시크릿이 새지 않도록 마스킹 (NFR-SEC-005, NFR-LOG-001)."""
    out = text
    out = _SECRET_PATTERNS[0].sub("sk-ant-***", out)
    out = _SECRET_PATTERNS[1].sub(lambda m: f"{m.group(1)}=***", out)
    return out


class _SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        if isinstance(record.msg, str):
            record.msg = mask_secrets(record.msg)
        return True


_CONFIGURED = False


def get_logger(name: str = "trace") -> logging.Logger:
    """시크릿 마스킹 필터가 붙은 로거를 반환한다. 반복 호출 안전."""
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        level = os.environ.get("TRACE_LOG_LEVEL", "INFO").upper()
        handler = logging.StreamHandler()  # stderr — stdio MCP 전송(stdout)을 오염시키지 않음
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handler.addFilter(_SecretMaskingFilter())
        root = logging.getLogger("trace")
        root.setLevel(getattr(logging, level, logging.INFO))
        root.addHandler(handler)
        root.propagate = False
        _CONFIGURED = True
    return logger


__all__ = [
    "TraceError",
    "InvalidPathError",
    "ConfigError",
    "LLMError",
    "KnowledgeNotFoundError",
    "Result",
    "mask_secrets",
    "get_logger",
]
