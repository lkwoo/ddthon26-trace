"""데브(Understand) 페르소나 시나리오 캡처 하니스 (결정적, API 키 불필요).

run_demo.py 의 FakeLLM 스크립트를 재사용해 데브 여정을 순차 재현한다:
  analyze_project → list_features → get_feature_knowledge("owner-registration")
                  → read_resource("trace://feature/owner-registration")

run_demo.py 와 달리 임시 디렉터리에 지식을 **영속**시켜, 스캔·지식화 이후의
조회 도구(list/knowledge/resource)가 저장된 지식을 그대로 읽는 실제 흐름을 보여준다.
출력은 데브가 Claude Code 안에서 각 MCP tool 결과로 받는 화면과 동일하다.

실행:  python demo/scenario/dev/capture_dev_scenario.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# 리포 루트를 import 경로에 추가 (demo.run_demo 재사용)
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
except Exception:  # pragma: no cover
    pass

from demo.run_demo import _ScriptedLLM, _build_scripts  # noqa: E402
from trace.engine.analyze import (  # noqa: E402
    analyze_project,
    get_feature_knowledge,
    list_features,
)
from trace.engine.scan import scan_project_assets  # noqa: E402
from trace.knowledge.store import KnowledgeStore  # noqa: E402
from trace.llm.service import LLMService  # noqa: E402

_DEMO_DIR = _REPO_ROOT / "demo"
DEV_FEATURE = "owner-registration"


def _hr(title: str) -> None:
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def main() -> int:
    # demo/ 를 임시 디렉터리에 복사해 실행(.trace 생성물을 리포 밖으로 격리·영속)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "demo"
        shutil.copytree(_DEMO_DIR, root, ignore=shutil.ignore_patterns(
            "run_demo.py", "scenario", "tools", "__pycache__", ".trace"))
        root_str = str(root)

        assets, _ = scan_project_assets(root_str)
        scripts, _ = _build_scripts(assets)
        analysis_llm = LLMService(_ScriptedLLM(scripts))

        # ── STEP 1 ────────────────────────────────────────────────────────
        _hr('STEP 1 · trace_analyze_project — "이 프로젝트를 분석해줘"')
        res = analyze_project(root_str, llm=analysis_llm)
        print(res.summary)
        print(f"자산 {res.data['assets_count']}개 / "
              f"Feature {len(res.data['features'])}개 / "
              f"충돌 {res.data['conflicts_count']}건")

        # ── STEP 2 ────────────────────────────────────────────────────────
        _hr('STEP 2 · trace_list_features — "어떤 기능들이 있어?"')
        for f in list_features(path=root_str).data["features"]:
            print(f"  - {f['id']}: {f['title']} (충돌 {f['conflicts_count']}건)")

        # ── STEP 3 ────────────────────────────────────────────────────────
        _hr('STEP 3 · trace_get_feature_knowledge("owner-registration")'
            ' — "Owner 등록 기능을 근거와 함께 설명해줘"')
        k = get_feature_knowledge(DEV_FEATURE, path=root_str)
        feat = k.data["feature"]
        print(f"Feature: {feat['title']} ({feat['id']})")
        print(f"설명: {feat['description']}")
        print(f"관련 자산 {len(feat['related_sources'])}개:")
        for s in feat["related_sources"]:
            print(f"  - {s}")

        print(f"\nClaims {len(k.data['claims'])}건 (subject · predicate = value):")
        for c in k.data["claims"]:
            print(f"  - {c['subject']}.{c['predicate']} = {c['value']}")

        print(f"\nConfidence {len(k.data['confidence'])}건:")
        for cc in k.data["confidence"]:
            a = cc["assessment"]
            print(f"  - {cc['claim_key']}: {a['level']} — {a['reason']}")

        print(f"\n이 Feature의 충돌 {len(k.conflicts)}건:")
        for c in k.conflicts:
            vals = ", ".join(f"{v['value']}@{v['source']}" for v in c.values)
            print(f"  - [{c.type}] {c.claim}")
            print(f"      {c.interpretation}")
            print(f"      값: {vals}")

        print(f"\n지식 본문 리소스: {k.data['resource_uri']}")

        # ── STEP 4 ────────────────────────────────────────────────────────
        _hr('STEP 4 · resource read — "trace://feature/owner-registration" 본문')
        body = KnowledgeStore(root_str).read_resource(k.data["resource_uri"])
        print(body)

        _hr("데브 여정 완료 — 낯선 코드베이스를 Feature 단위 + 근거로 이해")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
