"""C8 프롬프트 로더 (UOW-0F) — 프롬프트는 코드와 분리 저장 (NFR-MAINT-002).

템플릿은 `trace/prompts/templates/<name>.md`에 두고, `get_prompt(name, **vars)`가 읽어
`{var}` 자리표시자를 채운다. 템플릿 내용은 각 AI 단위(UOW-02/03/04)가 채운다.
"""

from __future__ import annotations

import string
from pathlib import Path

_TEMPLATE_DIR = Path(__file__).parent / "templates"


class _SafeTemplate(string.Template):
    """`${var}`/`$var` 치환. 누락 변수는 예외 대신 원문 유지(안전)."""


def get_prompt(name: str, **variables: object) -> str:
    """이름으로 프롬프트 템플릿을 로드하고 변수를 렌더링한다.

    Raises:
        FileNotFoundError: 템플릿이 없을 때.
    """
    path = _TEMPLATE_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"프롬프트 템플릿을 찾을 수 없음: {name} ({path})")
    text = path.read_text(encoding="utf-8")
    if not variables:
        return text
    return _SafeTemplate(text).safe_substitute(
        {k: str(v) for k, v in variables.items()}
    )


def list_prompts() -> list[str]:
    """등록된 프롬프트 템플릿 이름 목록."""
    if not _TEMPLATE_DIR.is_dir():
        return []
    return sorted(p.stem for p in _TEMPLATE_DIR.glob("*.md"))


__all__ = ["get_prompt", "list_prompts"]
