"""LLMService 구조화·재시도 테스트 (P1/P2, NFR-0F-REL-3/TST-1)."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from trace.common.errors import LLMValidationError
from trace.config.settings import LLMSettings
from trace.llm.service import LLMService
from tests.conftest import FakeLLMClient


class _Answer(BaseModel):
    name: str
    count: int


def _settings(max_retries: int = 2) -> LLMSettings:
    return LLMSettings(max_retries=max_retries)


def test_structured_success_first_try():
    client = FakeLLMClient(['{"name": "trace", "count": 3}'])
    svc = LLMService(client, _settings())
    out = svc.complete_structured("prompt", _Answer)
    assert out.name == "trace" and out.count == 3
    assert len(client.calls) == 1


def test_structured_recovers_after_correction():
    # 1차: 스키마 위반(count 누락) → 2차: 교정된 유효 JSON
    client = FakeLLMClient(['{"name": "trace"}', '{"name": "trace", "count": 5}'])
    svc = LLMService(client, _settings())
    out = svc.complete_structured("prompt", _Answer)
    assert out.count == 5
    assert len(client.calls) == 2
    # 2차 프롬프트에 제약 교정 힌트가 포함
    assert "스키마" in client.calls[1]


def test_structured_exhausts_retries():
    client = FakeLLMClient(["not json", "still bad", "nope"])
    svc = LLMService(client, _settings(max_retries=2))
    with pytest.raises(LLMValidationError):
        svc.complete_structured("prompt", _Answer)
    assert len(client.calls) == 3  # 최초 1 + 재시도 2


def test_strips_code_fence():
    client = FakeLLMClient(['```json\n{"name": "x", "count": 1}\n```'])
    svc = LLMService(client, _settings())
    out = svc.complete_structured("prompt", _Answer)
    assert out.name == "x"
