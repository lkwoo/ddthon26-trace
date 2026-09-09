"""프롬프트 로더 테스트 (C8, MNT-2)."""

from __future__ import annotations

import pytest

from trace.common.errors import ConfigError
from trace.prompts import loader


def test_missing_template_raises():
    with pytest.raises(ConfigError):
        loader.get_prompt("no-such-template")


def test_unsafe_name_rejected():
    with pytest.raises(ConfigError):
        loader.get_prompt("../secrets")


def test_render_and_unresolved_var(tmp_path, monkeypatch):
    # 임시 템플릿 디렉터리로 교체
    tdir = tmp_path / "templates"
    tdir.mkdir()
    (tdir / "greet.md").write_text("Hello ${name}", encoding="utf-8")
    monkeypatch.setattr(loader, "_TEMPLATE_DIR", tdir)

    assert loader.get_prompt("greet", name="TRACE") == "Hello TRACE"
    with pytest.raises(ConfigError):
        loader.get_prompt("greet")  # 미해결 변수
