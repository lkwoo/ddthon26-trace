"""UOW-01 분류기 예제 테스트 (BR-CLASSIFY)."""

from __future__ import annotations

import pytest

from trace.engine.classifier import classify, is_test, looks_like_openapi
from trace.models.asset import AssetType

OPENAPI_YAML = "openapi: 3.0.1\ninfo:\n  title: X\npaths: {}\n"
SWAGGER_YAML = "swagger: '2.0'\ninfo: {title: X}\n"
PLAIN_YAML = "server:\n  port: 8080\n"
OPENAPI_JSON = '{"openapi": "3.0.1", "paths": {}}'


@pytest.mark.parametrize("rel,fname,expected", [
    ("src/Owner.java", "Owner.java", AssetType.SOURCE),
    ("app/main.py", "main.py", AssetType.SOURCE),
    ("db/schema.sql", "schema.sql", AssetType.SQL),
    ("docs/spec.pdf", "spec.pdf", AssetType.PDF),
    ("README.md", "README.md", AssetType.MARKDOWN),
    ("config/application.properties", "application.properties", AssetType.CONFIG),
    ("notes.txt", "notes.txt", AssetType.TEXT),
    ("data.unknownext", "data.unknownext", AssetType.TEXT),
])
def test_classify_by_extension(rel: str, fname: str, expected: AssetType) -> None:
    assert classify(rel, fname) == expected


def test_test_detection_takes_priority_over_source() -> None:
    # /test/ 경로의 소스는 TEST 로 분류 (BR-CLASSIFY-002)
    assert classify("src/test/FooTest.java", "FooTest.java") == AssetType.TEST
    assert classify("tests/test_scan.py", "test_scan.py") == AssetType.TEST
    assert is_test("a/tests/x.py", "x.py") is True
    assert is_test("src/main/Owner.java", "Owner.java") is False


@pytest.mark.parametrize("text,expected", [
    (OPENAPI_YAML, AssetType.OPENAPI),
    (SWAGGER_YAML, AssetType.OPENAPI),
    (OPENAPI_JSON, AssetType.OPENAPI),
    (PLAIN_YAML, AssetType.CONFIG),
])
def test_openapi_vs_config(text: str, expected: AssetType) -> None:
    assert classify("api/spec.yaml", "spec.yaml", text=text) == expected


def test_structured_without_text_falls_back_to_config() -> None:
    # 내용 없이 .yaml → openapi 판별 불가 → config (BR-CLASSIFY-003 폴백)
    assert classify("x.yaml", "x.yaml") == AssetType.CONFIG


def test_looks_like_openapi_handles_bad_yaml() -> None:
    assert looks_like_openapi("::: not valid : yaml : :") is False
