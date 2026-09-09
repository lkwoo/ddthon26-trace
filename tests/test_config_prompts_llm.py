"""UOW-0F 테스트 — config(.env/제외규칙), 프롬프트 로더, LLMService replay/파싱."""

from __future__ import annotations

import json

import pytest

import traceki.prompts as prompts_mod
from traceki.common import ConfigError, LLMError
from traceki.config import DEFAULT_EXCLUSIONS, get_llm_settings, load_config
from traceki.llm import LLMService, _extract_json
from traceki.prompts import get_prompt


# ------------------------------------------------------------------- config
def test_default_exclusions_cover_common_dirs():
    for d in [".git", "node_modules", "target", "__pycache__", ".trace"]:
        assert d in DEFAULT_EXCLUSIONS


def test_load_dotenv_merges_without_override(tmp_path, monkeypatch):
    monkeypatch.delenv("TRACE_LLM_MODEL", raising=False)
    (tmp_path / ".env").write_text("TRACE_LLM_MODEL=claude-test\nANTHROPIC_API_KEY=sk-ant-xyz\n")
    load_config(str(tmp_path))
    s = get_llm_settings()
    assert s.model == "claude-test"
    assert s.api_key == "sk-ant-xyz"


def test_llm_settings_default_backend_is_replay(monkeypatch):
    monkeypatch.delenv("TRACE_LLM_BACKEND", raising=False)
    assert get_llm_settings().backend == "replay"


def test_bedrock_backend_reads_bearer_token_and_model(monkeypatch):
    # Bedrock은 sk-ant 다이렉트 키가 아니라 bearer 토큰(ABSK…)과 Bedrock 모델 ID를 쓴다.
    monkeypatch.setenv("TRACE_LLM_BACKEND", "bedrock")
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "ABSK-test-token")
    monkeypatch.setenv("TRACE_BEDROCK_MODEL", "apac.anthropic.claude-sonnet-4-5-20250929-v1:0")
    monkeypatch.setenv("AWS_REGION", "ap-northeast-2")
    s = get_llm_settings()
    assert s.backend == "bedrock"
    assert s.api_key == "ABSK-test-token"
    assert s.model == "apac.anthropic.claude-sonnet-4-5-20250929-v1:0"
    assert s.aws_region == "ap-northeast-2"


# ------------------------------------------------------------------ prompts
def test_get_prompt_renders_variables(tmp_path, monkeypatch):
    tdir = tmp_path / "templates"
    tdir.mkdir()
    (tdir / "greet.md").write_text("Analyze ${feature} in ${count} files.")
    monkeypatch.setattr(prompts_mod, "_TEMPLATE_DIR", tdir)
    out = get_prompt("greet", feature="Owner", count=3)
    assert out == "Analyze Owner in 3 files."


def test_get_prompt_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(prompts_mod, "_TEMPLATE_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        get_prompt("nope")


# ---------------------------------------------------------------------- llm
def test_extract_json_plain():
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_from_code_fence():
    assert _extract_json("```json\n[1, 2, 3]\n```") == [1, 2, 3]


def test_extract_json_with_surrounding_prose():
    assert _extract_json('Sure! Here: {"x": 5} done') == {"x": 5}


def test_replay_backend_reads_fixture(tmp_path):
    (tmp_path / "identify_features.json").write_text(json.dumps([{"id": "f1"}]))
    svc = LLMService(get_llm_settings(), replay_dir=tmp_path)
    assert svc.structured("identify_features") == [{"id": "f1"}]


def test_replay_backend_missing_fixture_raises(tmp_path):
    svc = LLMService(get_llm_settings(), replay_dir=tmp_path)
    with pytest.raises(LLMError):
        svc.structured("does_not_exist")


def test_live_backend_without_key_raises(monkeypatch):
    monkeypatch.setenv("TRACE_LLM_BACKEND", "live")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    svc = LLMService(get_llm_settings())
    with pytest.raises(ConfigError):
        svc.structured("any", "prompt")
