"""프롬프트 템플릿 로더 (UOW-0F, C8).

get_prompt(name, **vars): prompts/templates/<name>.md 로드 후 vars 렌더.
템플릿 '내용'은 각 AI 단위(UOW-02/03/04)가 채운다 — 0F는 로더 계약만 동결.
미존재 템플릿 / 미해결 변수 → ConfigError (엄격, MNT-2).
"""

from __future__ import annotations

import string
from pathlib import Path

from trace.common.errors import ConfigError

_TEMPLATE_DIR = Path(__file__).parent / "templates"


class _StrictTemplate(string.Template):
    """${var} 치환. 미해결 변수는 예외로 드러낸다."""


def _template_path(name: str) -> Path:
    # 경로 이탈 방지 (name 은 파일명만 허용)
    if "/" in name or "\\" in name or ".." in name:
        raise ConfigError(f"허용되지 않는 프롬프트 이름: {name!r}")
    return _TEMPLATE_DIR / f"{name}.md"


def get_prompt(name: str, /, **vars: object) -> str:
    """템플릿 로드 + 변수 렌더 후 문자열 반환.

    `name`은 위치 전용 인자 — 템플릿 변수로 `name`을 써도 충돌하지 않는다.
    """
    path = _template_path(name)
    if not path.exists():
        raise ConfigError(f"프롬프트 템플릿을 찾을 수 없습니다: {name}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"프롬프트 템플릿 읽기 실패: {name} ({exc})") from exc
    try:
        return _StrictTemplate(raw).substitute(**vars)
    except KeyError as exc:
        raise ConfigError(
            f"프롬프트 '{name}' 렌더 중 미해결 변수: {exc}"
        ) from exc


def list_prompts() -> list[str]:
    """등록된 템플릿 이름 목록 (확장자 제외)."""
    if not _TEMPLATE_DIR.exists():
        return []
    return sorted(p.stem for p in _TEMPLATE_DIR.glob("*.md"))
