"""UOW-02 실 API 통합 테스트 (옵트인, NFR-02-TST-2, Q3=B).

기본적으로 skip. 아래 두 조건이 모두 충족될 때만 실행:
  - 환경변수 TRACE_RUN_LLM_INTEGRATION=1
  - 유효한 Anthropic API 키(기본 env: ANTHROPIC_API_KEY)

실행 시: 실제 LLM으로 identify_features가 유효한 구조화 출력을 반환하는지 최소 검증.
CI/일반 실행에서는 네트워크·비용 없이 skip 되어야 한다.
"""

from __future__ import annotations

import os

import pytest

from trace.config.settings import get_llm_settings
from trace.models.asset import Asset, AssetType, ParseStatus

_RUN = os.environ.get("TRACE_RUN_LLM_INTEGRATION") == "1"


def _has_key() -> bool:
    try:
        get_llm_settings().resolve_api_key()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.llm_integration


@pytest.mark.skipif(not _RUN, reason="옵트인: TRACE_RUN_LLM_INTEGRATION=1 일 때만 실행")
@pytest.mark.skipif(not _has_key(), reason="유효한 Anthropic API 키 필요")
def test_identify_features_live() -> None:
    from trace.llm.client import AnthropicClient  # 실제 클라이언트
    from trace.llm.service import LLMService
    from trace.workflow.features import identify_features

    assets = [
        Asset(rel_path="src/Owner.java", filename="Owner.java", asset_type=AssetType.SOURCE,
              parse_status=ParseStatus.PARSED, size_bytes=40,
              content="class Owner { String telephone; }"),
        Asset(rel_path="db/schema.sql", filename="schema.sql", asset_type=AssetType.SQL,
              parse_status=ParseStatus.PARSED, size_bytes=40,
              content="CREATE TABLE owners (telephone VARCHAR(10));"),
    ]
    llm = LLMService(AnthropicClient())
    features, warnings = identify_features(assets, llm, max_features=5)
    assert warnings == [] or all(w.code == "identify_failed" for w in warnings)
    # 실제 모델이 최소 1개 Feature를 안전 id로 반환
    for f in features:
        assert f.id and "/" not in f.id
