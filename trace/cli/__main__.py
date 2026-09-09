"""trace 폴백 CLI 엔트리포인트 (UOW-06, C9, FR-DEMO-002).

MCP 서버와 동일한 코어 함수(engine)를 호출한다. 서브커맨드:
  analyze                       프로젝트 스캔·지식화·충돌검출
  features                      Feature 요약 목록
  knowledge <id>                한 Feature 지식(구조화)
  conflicts [--feature <id>]    검출된 충돌
  impact <task> [--feature <id>] 작업 영향 분석(충돌 경고·Change Plan)

공통 옵션: --path <dir>(기본 TRACE_PROJECT_ROOT 또는 cwd), --json(구조화 출력).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from trace.common.errors import error_to_result
from trace.engine import (
    analyze_project,
    analyze_task_impact,
    get_conflicts,
    get_feature_knowledge,
    list_features,
)
from trace.mcp_server.serialize import serialize_result
from trace.models.result import Result


def _default_root() -> str:
    return os.environ.get("TRACE_PROJECT_ROOT") or os.getcwd()


def _print(result: Result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(serialize_result(result), ensure_ascii=False, indent=2))
        return
    # 사람이 읽는 출력: 요약(핵심 우선) + 충돌/영향 하이라이트
    print(result.summary)
    if result.conflicts:
        print("\n충돌:")
        for c in result.conflicts:
            print(f"  - [{c.type}] {c.claim}: {c.interpretation}")
    if result.impact is not None:
        imp = result.impact
        for label, items in (("Must Change", imp.must_change),
                             ("Likely Change", imp.likely_change),
                             ("Review", imp.review)):
            if items:
                print(f"\n{label}:")
                for it in items:
                    print(f"  - {it.path}: {it.reason}")
        if imp.change_plan:
            print("\nChange Plan:")
            for step in imp.change_plan:
                print(f"  {step}")
    if result.warnings:
        print("\n경고:")
        for w in result.warnings:
            print(f"  - [{w.code}] {w.message}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trace", description="TRACE 폴백 CLI — MCP와 동일한 코어 함수")
    p.add_argument("--path", default=None, help="프로젝트 루트(기본: TRACE_PROJECT_ROOT 또는 현재 디렉터리)")
    p.add_argument("--json", action="store_true", help="구조화(JSON) 출력")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("analyze", help="프로젝트 스캔·지식화·충돌검출")
    sub.add_parser("features", help="Feature 요약 목록")
    k = sub.add_parser("knowledge", help="한 Feature 지식")
    k.add_argument("feature_id")
    c = sub.add_parser("conflicts", help="검출된 충돌")
    c.add_argument("--feature", default=None, help="특정 Feature만")
    i = sub.add_parser("impact", help="작업 영향 분석")
    i.add_argument("task", help="자연어 변경 작업")
    i.add_argument("--feature", default=None, help="대상 Feature(선택)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.path or _default_root()

    try:
        if args.command == "analyze":
            result = analyze_project(root)
        elif args.command == "features":
            result = list_features(path=root)
        elif args.command == "knowledge":
            result = get_feature_knowledge(args.feature_id, path=root)
        elif args.command == "conflicts":
            result = get_conflicts(args.feature, path=root)
        elif args.command == "impact":
            result = analyze_task_impact(args.task, args.feature, path=root)
        else:  # pragma: no cover - argparse가 방어
            raise SystemExit(2)
    except Exception as exc:  # noqa: BLE001 — CLI 경계: 사람이 읽을 오류로 강등
        result = error_to_result(exc)

    _print(result, args.json)
    # 오류 Result면 비정상 종료 코드
    return 1 if result.meta.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
