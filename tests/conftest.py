"""테스트 환경 격리.

`load_config`는 앱 동작상 `cwd/.env`를 `os.environ`에 병합한다(프로세스 전역). 저장소 루트에
실제 `.env`(live/bedrock 자격증명 등)가 있으면 한 테스트의 병합이 이후 테스트로 새어들어
결과를 오염시킨다. 아래 autouse 픽스처로 각 테스트를 TRACE/LLM 관련 환경변수로부터 격리하고,
테스트가 끝나면 원래 환경을 복원한다.
"""

from __future__ import annotations

import os

import pytest

# 테스트 결정성에 영향을 주는 환경변수 (앰비언트 .env/셸 값 차단)
_ISOLATED_VARS = (
    "TRACE_LLM_BACKEND",
    "TRACE_LLM_MODEL",
    "TRACE_BEDROCK_MODEL",
    "TRACE_REPLAY_DIR",
    "TRACE_HOME",
    "TRACE_LOG_LEVEL",
    "ANTHROPIC_API_KEY",
    "AWS_BEARER_TOKEN_BEDROCK",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
)


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path_factory):
    """각 테스트를 저장소 `.env`/셸 값으로부터 격리한다.

    - 관련 환경변수를 제거하고,
    - cwd를 깨끗한 임시 디렉터리로 옮겨 `load_config`가 저장소 루트의 `.env`를
      읽지 못하게 한다(load_config는 cwd/.env를 병합하므로).
    monkeypatch가 테스트 종료 시 환경변수와 cwd를 모두 복원한다.
    """
    for var in _ISOLATED_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(tmp_path_factory.mktemp("cwd_isolated"))
    yield
