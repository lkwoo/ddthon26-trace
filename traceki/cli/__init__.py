"""C9 폴백 CLI — MCP 없이도 코어 함수를 직접 실행하는 얇은 어댑터 (UOW-06).

MCP 클라이언트(Claude Code)가 없거나 재현·시연이 필요할 때 같은 코어 함수를 터미널에서 호출한다
(Q5=A 폴백). 로직은 전혀 없고 인자 파싱·사람이 읽는 출력만 담당한다(NFR-CORE-002). `--json`으로
원시 Result(to_dict)를 그대로 출력할 수 있다.

진입점: `trace` → `main()`.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from traceki.common import Result, get_logger
from traceki.config import load_config

_log = get_logger("trace.cli")


def _print_result(result: Result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    print(result.summary)
    for w in result.warnings:
        print(f"  ⚠️  {w}")


def _cmd_analyze_project(args) -> Result:
    from traceki.engine import analyze_project

    config = load_config(args.path)
    result = analyze_project(args.path, config=config, refresh=args.refresh)
    if not args.json and result.meta.get("ok"):
        for f in result.data.get("features", []):
            flag = f" ⚠️ 충돌 {f['conflicts']}건" if f.get("conflicts") else ""
            print(f"  • {f['id']} — {f['title']} (신뢰도 {f.get('confidence','?')}){flag}")
    return result


def _cmd_list_features(args) -> Result:
    from traceki.engine import list_features

    result = list_features()
    if not args.json:
        for f in result.data.get("features", []):
            print(f"  • {f['id']} — {f['title']} (충돌 {f.get('conflicts',0)}건)")
    return result


def _cmd_feature(args) -> Result:
    from traceki.engine import get_feature_knowledge

    result = get_feature_knowledge(args.feature_id)
    if not args.json and result.meta.get("ok"):
        d = result.data
        if d.get("business_rules"):
            print("  비즈니스 규칙:")
            for r in d["business_rules"]:
                print(f"    - {r}")
        if d.get("conflicts"):
            print(f"  ⚠️ 충돌 {len(d['conflicts'])}건")
    return result


def _cmd_conflicts(args) -> Result:
    from traceki.engine import get_conflicts

    result = get_conflicts(args.feature)
    if not args.json:
        for c in result.conflicts:
            vals = "; ".join(f"{v['value']} ← {v['source']}" for v in c["values"])
            print(f"  • [{c['type']}] {c['claim']}: {vals}")
    return result


def _cmd_analyze_task(args) -> Result:
    from traceki.engine import analyze_task_impact

    config = load_config(".")
    result = analyze_task_impact(args.task, feature_id=args.feature, config=config)
    if not args.json and result.impact:
        imp = result.impact
        for label, key in [("반드시 변경", "must_change"), ("변경 가능", "likely_change"), ("검토", "review")]:
            items = imp.get(key, [])
            if items:
                print(f"  [{label}]")
                for it in items:
                    print(f"    - {it['path']}: {it.get('reason','')}")
        if imp.get("change_plan"):
            print("  [Change Plan]")
            for step in imp["change_plan"]:
                print(f"    {step}")
    return result


def _cmd_map(args) -> Result:
    from traceki.engine import generate_onboarding_map

    config = load_config(args.path)
    result = generate_onboarding_map(args.path, feature_id=args.feature, refresh=args.refresh, config=config)
    if not args.json and result.meta.get("ok"):
        d = result.data
        eps = d.get("entry_points", [])
        if eps:
            print("  [진입점]")
            for e in eps:
                print(f"    - {e['symbol']} ({e['file']}) — {e['kind']}")
        fmaps = d.get("feature_file_maps", [])
        if fmaps:
            print("  [Feature → 파일]")
            for m in fmaps:
                print(f"    - {m['title']}: {len(m['files'])}개 파일")
        graph = d.get("file_graph", {})
        print(f"  [관계] 파일 {len(graph.get('nodes', []))}개, 의존 {len(graph.get('dep_edges', []))}건, "
              f"호출 {len(graph.get('call_edges', []))}건")
        if d.get("overview_path"):
            print(f"  [저장] {d['overview_path']}")
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trace",
        description="TRACE — 흩어진 개발 자산을 Feature 중심 지식으로 재구성하고 충돌을 착수 전에 경고한다.",
    )
    # --json은 각 서브커맨드에 붙는 공용 옵션(`trace map ./demo --json`). 공용 부모 파서로
    # 모든 서브파서에 상속시켜 위치를 서브커맨드 뒤로 일관되게 둔다(argparse 서브파서 기본값
    # 우선순위 때문에 전역 옵션은 두지 않는다).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="원시 Result JSON 출력")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("analyze-project", parents=[common], help="프로젝트 스캔·분석(지식·충돌 생성)")
    sp.add_argument("path", nargs="?", default=".", help="분석 대상 경로 (기본: 현재 디렉터리)")
    sp.add_argument("--refresh", action="store_true", help="캐시 무시하고 재분석")
    sp.set_defaults(func=_cmd_analyze_project)

    sp = sub.add_parser("list-features", parents=[common], help="검출된 Feature 목록")
    sp.set_defaults(func=_cmd_list_features)

    sp = sub.add_parser("feature", parents=[common], help="단일 Feature 지식 상세")
    sp.add_argument("feature_id")
    sp.set_defaults(func=_cmd_feature)

    sp = sub.add_parser("conflicts", parents=[common], help="충돌 목록")
    sp.add_argument("--feature", default=None, help="특정 Feature로 한정")
    sp.set_defaults(func=_cmd_conflicts)

    sp = sub.add_parser("analyze-task", parents=[common], help="자연어 작업의 착수 전 영향 분석")
    sp.add_argument("task", help='예: "Add SMS verification to Owner registration"')
    sp.add_argument("--feature", default=None, help="특정 Feature로 한정")
    sp.set_defaults(func=_cmd_analyze_task)

    sp = sub.add_parser("map", parents=[common], help="신입 온보딩 맵 생성(진입점·의존 그래프·Feature→파일·Mermaid)")
    sp.add_argument("path", nargs="?", default=".", help="대상 경로 (기본: 현재 디렉터리)")
    sp.add_argument("--feature", default=None, help="특정 Feature로 한정")
    sp.add_argument("--refresh", action="store_true", help="캐시(overview.md) 무시하고 재생성")
    sp.set_defaults(func=_cmd_map)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 진입점. 코어 함수의 Result.meta.ok에 따라 종료코드를 정한다."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result: Result = args.func(args)
    except Exception as exc:  # noqa: BLE001 — 최후의 전역 핸들러(NFR-REL-002)
        _log.error("명령 실행 실패: %s", exc)
        print(f"오류: {exc}", file=sys.stderr)
        return 1
    _print_result(result, args.json)
    return 0 if result.meta.get("ok", True) else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
