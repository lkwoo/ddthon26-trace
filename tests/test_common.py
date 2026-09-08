"""UOW-0F 공통 계약 테스트 — Result envelope, 시크릿 마스킹."""

from __future__ import annotations

from hypothesis import given, strategies as st

from trace.common import Result, mask_secrets


def test_result_to_dict_key_order():
    """핵심 우선 순서(NFR-MCP-UX-002): summary→data→conflicts→impact→evidence→warnings→meta."""
    r = Result.ok("done")
    assert list(r.to_dict().keys()) == [
        "summary", "data", "conflicts", "impact", "evidence", "warnings", "meta",
    ]


def test_result_ok_and_error_flags():
    assert Result.ok("s").meta["ok"] is True
    err = Result.error("bad path")
    assert err.meta["ok"] is False
    assert "bad path" in err.warnings


def test_add_warning_chains():
    r = Result().add_warning("w1").add_warning("w2")
    assert r.warnings == ["w1", "w2"]


def test_mask_secrets_hides_api_key():
    assert "sk-ant-" in mask_secrets("key sk-ant-ABC123xyz")
    assert "ABC123xyz" not in mask_secrets("key sk-ant-ABC123xyz")


def test_mask_secrets_hides_keyvalue():
    masked = mask_secrets("api_key=supersecret token: abc")
    assert "supersecret" not in masked
    assert "abc" not in masked


@given(st.text())
def test_mask_secrets_never_crashes(s: str):
    assert isinstance(mask_secrets(s), str)
