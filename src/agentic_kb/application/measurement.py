"""Lightweight latency measurement hook (US-N1 AC-2).

Wraps read/sync code paths to record elapsed time without affecting results.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager

logger = logging.getLogger("agentic_kb.measure")


@contextmanager
def measure(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.debug("%s took %.2f ms", name, elapsed_ms)
