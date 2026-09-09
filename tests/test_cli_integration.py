"""UOW-06 통합 테스트 — 폴백 CLI로 Hero 시나리오 E2E + 시크릿 위생.

replay 백엔드로 API 키 없이 전 흐름을 통과하는지 검증한다(NFR-REL-001 반복 가능 E2E).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from traceki.cli import main
from traceki.common import mask_secrets

DEMO = Path(__file__).resolve().parents[1] / "demo"
REPLAY = DEMO / "replay"


@pytest.fixture()
def replay_home(tmp_path, monkeypatch):
    monkeypatch.setenv("TRACE_LLM_BACKEND", "replay")
    monkeypatch.setenv("TRACE_REPLAY_DIR", str(REPLAY))
    monkeypatch.setenv("TRACE_HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    return tmp_path


def test_cli_full_hero_flow_exit_codes(replay_home, capsys):
    assert main(["analyze-project", str(DEMO), "--refresh"]) == 0
    assert main(["list-features"]) == 0
    assert main(["conflicts"]) == 0
    assert main(["analyze-task", "Add SMS verification to Owner registration"]) == 0
    out = capsys.readouterr().out
    assert "owner-registration" in out
    assert "value_mismatch" in out
    assert "Change Plan" in out


def test_cli_json_output(replay_home, capsys):
    main(["analyze-project", str(DEMO), "--refresh"])
    capsys.readouterr()
    rc = main(["conflicts", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().startswith("{")
    assert '"summary"' in out  # 봉투 키 순서: summary 우선


@pytest.mark.parametrize(
    "argv",
    [
        ["conflicts", "--json"],
        ["analyze-project", str(DEMO), "--json"],
        ["map", str(DEMO), "--json"],
    ],
)
def test_cli_json_flag_after_subcommand(replay_home, capsys, argv):
    """--json은 서브커맨드 뒤 위치에서 모든 명령에 동작해야 한다(문서·README와 일치)."""
    main(["analyze-project", str(DEMO), "--refresh"])
    capsys.readouterr()
    rc = main(argv)
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().startswith("{")  # 사람이 읽는 출력이 아니라 원시 JSON


def test_cli_unknown_feature_nonzero_exit(replay_home, capsys):
    rc = main(["feature", "no-such-feature"])
    assert rc == 2  # Result.meta.ok=False → 종료코드 2


def test_cli_analyze_task_without_analysis_guides_user(replay_home, capsys):
    # analyze-project 미실행 상태 → 안내 오류 (전역 예외 아님)
    rc = main(["analyze-task", "Do something"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "analyze_project" in out


# --------------------------------------------------------- 시크릿 위생
def test_secret_masking_in_logs():
    masked = mask_secrets("using key sk-ant-abc123XYZ and api_key=topsecret")
    assert "sk-ant-abc123XYZ" not in masked
    assert "topsecret" not in masked
    assert "sk-ant-***" in masked


def test_no_hardcoded_secret_in_repo_code():
    """소스에 sk-ant- 리터럴 키가 박혀 있지 않은지 (NFR-SEC-001)."""
    root = Path(__file__).resolve().parents[1] / "traceki"
    for py in root.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "sk-ant-" not in text or "sk-ant-***" in text, f"의심 키 리터럴: {py}"
