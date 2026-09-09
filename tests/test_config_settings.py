"""설정·시크릿 취급 테스트 (BR-SEC, NFR-0F-SEC-1/DET-2)."""

from __future__ import annotations

import pytest

from trace.common.errors import ConfigError
from trace.config.settings import LLMSettings, get_exclusions, get_llm_settings, load_config


def test_defaults_are_deterministic():
    s = get_llm_settings()
    assert s.temperature == 0.0
    assert s.max_retries == 2


def test_llm_settings_holds_key_name_not_value():
    s = LLMSettings(api_key_env="MY_KEY_ENV")
    # 세팅 객체에 키 '값'이 담기지 않는다 — 이름만
    dumped = s.model_dump()
    assert dumped["api_key_env"] == "MY_KEY_ENV"
    assert "api_key" not in dumped


def test_resolve_api_key_missing_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = LLMSettings(api_key_env="ANTHROPIC_API_KEY")
    with pytest.raises(ConfigError) as exc:
        s.resolve_api_key()
    # 오류 메시지에 키 값이 없어야 함 (미설정이므로 자명하지만 계약 문서화)
    assert "ANTHROPIC_API_KEY" in str(exc.value)


def test_resolve_api_key_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    s = LLMSettings(api_key_env="ANTHROPIC_API_KEY")
    assert s.resolve_api_key() == "sk-test-123"


def test_get_exclusions_dedup():
    excl = get_exclusions()
    assert len(excl) == len(set(excl))
    assert any(".trace" in p for p in excl)


def test_load_config_missing_file_raises():
    with pytest.raises(ConfigError):
        load_config("does-not-exist.toml")
