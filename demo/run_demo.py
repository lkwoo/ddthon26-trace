"""Hero 시나리오 데모 하니스 (UOW-06, US-06.1, NFR-AI-004 결정적).

**API 키 없이** 실제 코어 파이프라인(engine)을 구동해 Hero 흐름을 재현한다:
  analyze_project → list_features → get_conflicts → analyze_task_impact

LLM만 스크립트된 FakeLLM으로 대체하고(응답은 demo/의 실제 rel_path를 참조), 스캔·파싱·지식 저장·
결정적 충돌 검출·영향 매핑은 모두 진짜 코드가 수행한다. 결과는 매 실행 동일(고정 데이터셋).

실행:  python demo/run_demo.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# demo/ 상위(리포 루트)를 import 경로에 추가 (스크립트 직접 실행 대비)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows 콘솔(cp949 등)에서도 한글·기호 출력이 깨지지 않도록 UTF-8 강제
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
except Exception:  # pragma: no cover - 구형 스트림 방어
    pass

from trace.engine.analyze import (  # noqa: E402
    analyze_project,
    analyze_task_impact,
    get_conflicts,
    list_features,
)
from trace.engine.scan import scan_project_assets  # noqa: E402
from trace.llm.service import LLMService  # noqa: E402

_DEMO_DIR = Path(__file__).resolve().parent


class _ScriptedLLM:
    """미리 정한 응답을 순서대로 반환하는 LLMClient (FakeLLM, 네트워크 없음)."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls = 0

    def complete(self, prompt: str, *, settings) -> str:  # type: ignore[no-untyped-def]
        self.calls += 1
        if not self._responses:
            raise AssertionError("스크립트 응답이 소진되었습니다")
        return self._responses.pop(0)


def _find(assets, needle: str) -> str:
    """rel_path에 needle을 포함하는 첫 자산의 rel_path 반환 (실제 스캔 경로 사용)."""
    for a in assets:
        if needle in a.rel_path:
            return a.rel_path
    raise LookupError(needle)


def _build_scripts(assets) -> tuple[list[str], str]:
    """demo/의 실제 rel_path를 참조하는 스크립트 LLM 응답(식별→지식본문×2→추출×2)."""
    owner = _find(assets, "owner/Owner.java")
    openapi = _find(assets, "petclinic-rest.yaml")
    schema = _find(assets, "schema.sql")
    spec = _find(assets, "owner-management-spec.pdf")
    notes = _find(assets, "maintenance-notes.md")
    pet = _find(assets, "pet/Pet.java")

    features = json.dumps({"features": [
        {"id": "owner-registration", "title": "Owner Registration",
         "description": "반려동물 주인 등록·연락처·이메일 정책",
         "related_sources": [owner, openapi, schema, spec], "rationale": "핵심 등록 흐름"},
        {"id": "pet-management", "title": "Pet Management",
         "description": "반려동물 등록·생일 검증",
         "related_sources": [pet, notes, openapi], "rationale": "펫 도메인"},
    ]})
    body = json.dumps({"markdown": "# 지식 개요\n\n(데모 본문)"})

    extract_owner = json.dumps({"claims": [
        {"subject": "owner.telephone", "predicate": "max_length", "evidence": [
            {"source": spec, "type": "pdf", "location": "p.2", "extracted_value": "20", "relation": "supports"},
            {"source": openapi, "type": "openapi", "location": "components.Owner.telephone", "extracted_value": "10", "relation": "supports"},
            {"source": owner, "type": "source", "location": "@Size", "extracted_value": "10", "relation": "supports"},
            {"source": schema, "type": "sql", "location": "owners.telephone", "extracted_value": "10", "relation": "supports"},
        ]},
        {"subject": "owner.email", "predicate": "required", "evidence": [
            {"source": spec, "type": "pdf", "location": "p.3", "extracted_value": "required", "relation": "supports"},
            {"source": openapi, "type": "openapi", "location": "components.Owner", "extracted_value": "absent", "relation": "contradicts"},
            {"source": owner, "type": "source", "location": "fields", "extracted_value": "absent", "relation": "contradicts"},
        ]},
    ]})
    extract_pet = json.dumps({"claims": [
        {"subject": "pet.birthdate", "predicate": "future_date_validation", "evidence": [
            {"source": notes, "type": "markdown", "location": "설계 노트", "extracted_value": "rejected", "relation": "supports"},
            {"source": pet, "type": "source", "location": "setBirthDate", "extracted_value": "accepted", "relation": "contradicts"},
        ]},
    ]})
    # 순서: identify → body(owner) → body(pet) → extract(owner) → extract(pet)
    return [features, body, body, extract_owner, extract_pet], "owner-registration"


def _impact_script(assets) -> list[str]:
    owner = _find(assets, "owner/Owner.java")
    openapi = _find(assets, "petclinic-rest.yaml")
    schema = _find(assets, "schema.sql")
    return [json.dumps({
        "candidates": [
            {"path": owner, "category": "must_change", "reason": "전화번호 검증·SMS 인증 연동 지점",
             "evidence": [{"source": owner, "location": "@Size", "relation": "supports"}]},
            {"path": openapi, "category": "likely_change", "reason": "telephone 스키마·엔드포인트 갱신 가능",
             "evidence": [{"source": openapi, "location": "components.Owner.telephone", "relation": "mentions"}]},
            {"path": schema, "category": "review", "reason": "telephone 컬럼 길이 확인 필요",
             "evidence": [{"source": schema, "location": "owners.telephone", "relation": "mentions"}]},
        ],
        "change_plan": [
            "1. telephone 길이 충돌(문서 20 vs 구현 10) 먼저 해소",
            "2. OpenAPI telephone 스키마·검증 규칙 정의",
            "3. Owner 검증 로직에 SMS 인증 흐름 추가",
            "4. 통합/컨트롤러 테스트 갱신",
            "5. 문서(spec) 동기화",
        ],
    })]


def _hr(title: str) -> None:
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def main() -> int:
    # 리포를 오염시키지 않도록 demo/를 임시 디렉터리에 복사해 실행(.trace 생성물 격리)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "demo"
        shutil.copytree(_DEMO_DIR, root, ignore=shutil.ignore_patterns(
            "run_demo.py", "__pycache__", ".trace"))
        root_str = str(root)

        assets, _ = scan_project_assets(root_str)
        scripts, hero_fid = _build_scripts(assets)
        analysis_llm = LLMService(_ScriptedLLM(scripts))

        _hr("① analyze_project — 스캔·지식화·결정적 충돌 검출")
        res = analyze_project(root_str, llm=analysis_llm)
        print(res.summary)
        print(f"자산 {res.data['assets_count']}개 / Feature {len(res.data['features'])}개 / 충돌 {res.data['conflicts_count']}건")

        _hr("② list_features — Feature 요약 (캐시/저장 지식, LLM 미호출)")
        for f in list_features(path=root_str).data["features"]:
            print(f"  - {f['id']}: {f['title']} (충돌 {f['conflicts_count']}건)")

        _hr("③ get_conflicts — 문서/구현 충돌 (근거 포함)")
        for c in get_conflicts(path=root_str).conflicts:
            vals = ", ".join(f"{v['value']}@{v['source']}" for v in c.values)
            print(f"  - [{c.type}] {c.claim}\n      {c.interpretation}\n      값: {vals}")

        _hr("④ analyze_task_impact — 'Add SMS verification to Owner registration'")
        impact_llm = LLMService(_ScriptedLLM(_impact_script(assets)))
        ir = analyze_task_impact("Add SMS verification to Owner registration",
                                 hero_fid, path=root_str, llm=impact_llm)
        print(ir.summary)
        if ir.conflicts:
            print("\n⚠ 구현 착수 전 확인해야 할 기존 충돌:")
            for c in ir.conflicts:
                print(f"  - [{c.type}] {c.claim}: {c.interpretation}")
        imp = ir.impact
        for label, items in (("Must Change", imp.must_change), ("Likely Change", imp.likely_change), ("Review", imp.review)):
            if items:
                print(f"\n{label}:")
                for it in items:
                    print(f"  - {it.path}: {it.reason}")
        print("\nChange Plan (충돌 해소 우선):")
        for step in imp.change_plan:
            print(f"  {step}")

        _hr("완료 — Hero 흐름 E2E 통과 (API 키 없이 결정적 재현)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
