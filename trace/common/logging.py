"""구조화 로깅 + 단계 타이밍 컨텍스트 매니저 (UOW-0F, NFR Design P5).

NFR-0F-OBS-1: 단계·카운트·소요시간을 구조화(키=값) 1줄 로그로.
NFR-0F-SEC-3: 값 필드·문서 원문은 로깅하지 않는다 (경로·카운트·요약만).
레벨은 TRACE_LOG_LEVEL 환경변수로 조정 (기본 INFO).
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from typing import Iterator

_CONFIGURED = False


def get_logger(name: str = "trace") -> logging.Logger:
    """TRACE 로거 반환. 최초 호출 시 핸들러·레벨을 1회 설정한다."""
    global _CONFIGURED
    if not _CONFIGURED:
        level_name = os.environ.get("TRACE_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        root = logging.getLogger("trace")
        root.setLevel(level)
        # 중복 핸들러 방지
        if not root.handlers:
            root.addHandler(handler)
        _CONFIGURED = True
    return logging.getLogger(name)


def _kv(fields: dict[str, object]) -> str:
    """dict를 안정적 순서의 key=value 문자열로 (결정성)."""
    return " ".join(f"{k}={v}" for k, v in sorted(fields.items()))


class _Stage:
    """log_stage 컨텍스트 내부 상태 — 카운트를 모아 종료 시 1줄로 남긴다."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._counts: dict[str, object] = {}

    def count(self, key: str, value: object) -> None:
        """단계 지표 기록 (예: st.count("assets", 42)). 값 원문·시크릿 금지."""
        self._counts[key] = value


@contextmanager
def log_stage(name: str, logger: logging.Logger | None = None) -> Iterator[_Stage]:
    """단계 실행을 감싸 시작/종료·소요시간·카운트를 구조화 로깅한다.

    사용:
        with log_stage("scan") as st:
            ...
            st.count("assets", n)
    """
    log = logger or get_logger()
    stage = _Stage(name)
    start = time.perf_counter()
    log.info(_kv({"event": "stage_start", "stage": name}))
    try:
        yield stage
    except Exception as exc:  # noqa: BLE001 — 종료 로그 후 재-raise
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        log.error(
            _kv(
                {
                    "event": "stage_error",
                    "stage": name,
                    "elapsed_ms": elapsed_ms,
                    "error_type": type(exc).__name__,
                }
            )
        )
        raise
    else:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        log.info(
            _kv(
                {
                    "event": "stage_end",
                    "stage": name,
                    "elapsed_ms": elapsed_ms,
                    **stage._counts,
                }
            )
        )
