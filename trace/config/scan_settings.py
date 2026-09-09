"""스캔 설정 (UOW-01, C7, NFR Design P7).

크기 상한 등 스캐너 동작 파라미터를 config 계층에 분리한다(NFR-01-MAINT-1, Q4=A).
기본값은 상수이며, 환경변수로 오버라이드할 수 있다(late override 지점).
"""

from __future__ import annotations

import os

from pydantic import BaseModel

_DEFAULT_MAX_FILE_BYTES = 5_000_000       # 파일당 5MB (Q2=B)
_DEFAULT_MAX_TOTAL_BYTES = 200_000_000    # 총량 200MB (Q2=B)


class ScanSettings(BaseModel):
    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_total_bytes: int = _DEFAULT_MAX_TOTAL_BYTES


def get_scan_settings() -> ScanSettings:
    """스캔 설정 반환. TRACE_MAX_FILE_BYTES / TRACE_MAX_TOTAL_BYTES 로 오버라이드 가능."""
    settings = ScanSettings()
    if raw := os.environ.get("TRACE_MAX_FILE_BYTES"):
        try:
            settings.max_file_bytes = int(raw)
        except ValueError:
            pass  # 잘못된 값은 무시하고 기본값 유지
    if raw := os.environ.get("TRACE_MAX_TOTAL_BYTES"):
        try:
            settings.max_total_bytes = int(raw)
        except ValueError:
            pass
    return settings


__all__ = ["ScanSettings", "get_scan_settings"]
