"""Hero 시나리오 데모 하니스 (UOW-06, US-06.1, NFR-AI-004 결정적).

실제 코어 파이프라인(engine)을 구동해 Hero 흐름을 재현한다:
  analyze_project → list_features → get_conflicts → analyze_task_impact

두 가지 실행 모드:
  * (기본) FakeLLM  — **API 키 없이** 매번 동일한 결과. LLM만 스크립트된 FakeLLM으로 대체하고
                      (응답은 demo/의 실제 rel_path를 참조), 스캔·파싱·지식 저장·결정적 충돌 검출·
                      영향 매핑은 모두 진짜 코드가 수행한다.  실행:  python demo/run_demo.py
  * --live          — 실제 Claude(Anthropic)로 전체 파이프라인을 구동. 진짜 자동 Feature/충돌
                      검출을 시연하나, 결과는 비결정적이며 anthropic 설치 + ANTHROPIC_API_KEY 필요.
                      실행:  python demo/run_demo.py --live

데이터셋은 5개 도메인(owner/pet/vet/visit/billing)에 걸쳐 **9건의 의도적 충돌**을 담는다.
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

# Hero 태스크(영향 분석 대상)와 그 초점 Feature
HERO_TASK = "Add SMS verification to Owner registration"
HERO_FEATURE = "owner-registration"


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


def _paths(assets) -> dict[str, str]:
    """스크립트가 참조하는 실제 rel_path 모음 (드리프트 방지: 전부 스캔 자산에서 조회)."""
    return {
        "owner": _find(assets, "owner/Owner.java"),
        "pet": _find(assets, "pet/Pet.java"),
        "vet": _find(assets, "vet/Vet.java"),
        "visit": _find(assets, "visit/Visit.java"),
        "invoice": _find(assets, "billing/Invoice.java"),
        "openapi": _find(assets, "petclinic-rest.yaml"),
        "schema": _find(assets, "schema.sql"),
        "props": _find(assets, "application.properties"),
        "notes": _find(assets, "maintenance-notes.md"),
        "owner_spec": _find(assets, "owner-management-spec.pdf"),
        "vet_spec": _find(assets, "vet-directory-spec.pdf"),
        "visit_spec": _find(assets, "visit-scheduling-spec.pdf"),
        "billing_spec": _find(assets, "billing-spec.pdf"),
    }


def _ev(source, type_, location, value, relation):  # type: ignore[no-untyped-def]
    return {"source": source, "type": type_, "location": location,
            "extracted_value": value, "relation": relation}


def _build_scripts(assets) -> tuple[list[str], str]:
    """demo/의 실제 rel_path를 참조하는 스크립트 LLM 응답.

    analyze_project의 호출 순서(계약): identify → body×N → extract×N,
    feature id 오름차순. 6 Feature 이므로 1 + 6 + 6 = 13개 응답.
    """
    p = _paths(assets)

    # ── identify_features (6 Feature, related_sources 는 실제 rel_path) ──────────
    features = json.dumps({"features": [
        {"id": "billing-invoicing", "title": "Billing & Invoicing",
         "description": "청구서 금액·통화·세금 정책",
         "related_sources": [p["billing_spec"], p["schema"], p["invoice"]],
         "rationale": "청구 도메인"},
        {"id": "clinic-configuration", "title": "Clinic Configuration",
         "description": "운영 정책 설정(세금 적용 등)",
         "related_sources": [p["notes"], p["props"]],
         "rationale": "설정-문서 정합"},
        {"id": "owner-registration", "title": "Owner Registration",
         "description": "반려동물 주인 등록·연락처·이메일·주소 정책",
         "related_sources": [p["owner_spec"], p["openapi"], p["schema"], p["owner"]],
         "rationale": "핵심 등록 흐름"},
        {"id": "pet-management", "title": "Pet Management",
         "description": "반려동물 등록·생일 검증",
         "related_sources": [p["pet"], p["notes"], p["openapi"]],
         "rationale": "펫 도메인"},
        {"id": "vet-directory", "title": "Veterinarian Directory",
         "description": "수의사·전문분야 관리",
         "related_sources": [p["vet_spec"], p["vet"], p["schema"]],
         "rationale": "수의사 디렉터리"},
        {"id": "visit-scheduling", "title": "Visit Scheduling",
         "description": "진료 방문 예약·설명·일자 검증",
         "related_sources": [p["visit_spec"], p["openapi"], p["visit"], p["schema"]],
         "rationale": "방문 예약"},
    ]})

    body = json.dumps({"markdown": "# 지식 개요\n\n(데모 본문)"})

    # ── extract_claims (feature id 오름차순으로 소비됨) ──────────────────────────
    # 1) billing-invoicing → C-7 value_mismatch
    extract_billing = json.dumps({"claims": [
        {"subject": "invoice.amount", "predicate": "precision", "evidence": [
            _ev(p["billing_spec"], "pdf", "REQ-1", "DECIMAL(10,2)", "supports"),
            _ev(p["schema"], "sql", "invoices.amount", "DECIMAL(8,2)", "supports"),
            _ev(p["invoice"], "source", "@Column(precision=8)", "DECIMAL(8,2)", "supports"),
        ]},
    ]})
    # 2) clinic-configuration → C-9 stale_knowledge (behavioral 'enforced')
    extract_clinic = json.dumps({"claims": [
        {"subject": "billing.tax", "predicate": "enforcement_default", "evidence": [
            _ev(p["notes"], "markdown", "BILLING-RULE-1", "enforced", "supports"),
            _ev(p["props"], "config", "billing.tax.enforcement", "disabled", "contradicts"),
        ]},
    ]})
    # 3) owner-registration → C-1 value_mismatch, C-3 policy, C-8 policy
    extract_owner = json.dumps({"claims": [
        {"subject": "owner.telephone", "predicate": "max_length", "evidence": [
            _ev(p["owner_spec"], "pdf", "REQ-1", "20", "supports"),
            _ev(p["openapi"], "openapi", "components.Owner.telephone", "10", "supports"),
            _ev(p["owner"], "source", "@Size(max=10)", "10", "supports"),
            _ev(p["schema"], "sql", "owners.telephone", "10", "supports"),
        ]},
        {"subject": "owner.email", "predicate": "required", "evidence": [
            _ev(p["owner_spec"], "pdf", "REQ-2", "required", "supports"),
            _ev(p["openapi"], "openapi", "components.Owner", "absent", "contradicts"),
            _ev(p["owner"], "source", "fields", "absent", "contradicts"),
            _ev(p["schema"], "sql", "owners", "absent", "contradicts"),
        ]},
        {"subject": "owner.address", "predicate": "required", "evidence": [
            _ev(p["owner_spec"], "pdf", "REQ-3", "required", "supports"),
            _ev(p["owner"], "source", "@Size(max=255) nullable", "absent", "contradicts"),
        ]},
    ]})
    # 4) pet-management → C-2 stale_knowledge
    extract_pet = json.dumps({"claims": [
        {"subject": "pet.birthDate", "predicate": "future_date_validation", "evidence": [
            _ev(p["notes"], "markdown", "PET-RULE-1", "rejected", "supports"),
            _ev(p["pet"], "source", "setBirthDate", "accepted", "contradicts"),
        ]},
    ]})
    # 5) vet-directory → C-5 policy_conflict
    extract_vet = json.dumps({"claims": [
        {"subject": "vet.specialties", "predicate": "min_one_required", "evidence": [
            _ev(p["vet_spec"], "pdf", "REQ-1", "required", "supports"),
            _ev(p["vet"], "source", "specialties(no @Size)", "absent", "contradicts"),
        ]},
    ]})
    # 6) visit-scheduling → C-4 value_mismatch, C-6 stale_knowledge
    extract_visit = json.dumps({"claims": [
        {"subject": "visit.description", "predicate": "max_length", "evidence": [
            _ev(p["visit_spec"], "pdf", "REQ-1", "255", "supports"),
            _ev(p["openapi"], "openapi", "components.Visit.description", "8192", "supports"),
            _ev(p["visit"], "source", "@Size(max=8192)", "8192", "supports"),
            _ev(p["schema"], "sql", "visits.description", "8192", "supports"),
        ]},
        {"subject": "visit.date", "predicate": "past_date_validation", "evidence": [
            _ev(p["notes"], "markdown", "VISIT-RULE-1", "rejected", "supports"),
            _ev(p["visit"], "source", "setDate", "accepted", "contradicts"),
        ]},
    ]})

    scripts = (
        [features]
        + [body] * 6
        + [extract_billing, extract_clinic, extract_owner,
           extract_pet, extract_vet, extract_visit]
    )
    return scripts, HERO_FEATURE


def _impact_script(assets) -> list[str]:
    p = _paths(assets)
    return [json.dumps({
        "candidates": [
            {"path": p["owner"], "category": "must_change",
             "reason": "전화번호 검증·SMS 인증 연동 지점",
             "evidence": [{"source": p["owner"], "location": "@Size", "relation": "supports"}]},
            {"path": p["openapi"], "category": "likely_change",
             "reason": "telephone 스키마·엔드포인트 갱신 가능",
             "evidence": [{"source": p["openapi"], "location": "components.Owner.telephone", "relation": "mentions"}]},
            {"path": p["schema"], "category": "review",
             "reason": "telephone 컬럼 길이 확인 필요",
             "evidence": [{"source": p["schema"], "location": "owners.telephone", "relation": "mentions"}]},
        ],
        "change_plan": [
            "1. telephone 길이 충돌(문서 20 vs 구현 10) 먼저 해소",
            "2. OpenAPI telephone 스키마·검증 규칙 정의",
            "3. Owner 검증 로직에 SMS 인증 흐름 추가",
            "4. 통합/컨트롤러 테스트 갱신",
            "5. 문서(spec) 동기화",
        ],
    })]


def _live_llm() -> LLMService:
    """실제 Claude(Anthropic) 기반 LLMService. anthropic 설치 + ANTHROPIC_API_KEY 필요."""
    from trace.llm.client import AnthropicClient
    return LLMService(AnthropicClient())


def _hr(title: str) -> None:
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    live = "--live" in argv

    # 리포를 오염시키지 않도록 demo/를 임시 디렉터리에 복사해 실행(.trace 생성물 격리)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "demo"
        shutil.copytree(_DEMO_DIR, root, ignore=shutil.ignore_patterns(
            "run_demo.py", "tools", "__pycache__", ".trace"))
        root_str = str(root)

        assets, _ = scan_project_assets(root_str)

        if live:
            _hr("실행 모드: --live (실제 Claude 자동 검출, 비결정적)")
            analysis_llm = _live_llm()
            impact_llm = _live_llm()
        else:
            _hr("실행 모드: FakeLLM (API 키 없이 결정적 재현)")
            scripts, _ = _build_scripts(assets)
            analysis_llm = LLMService(_ScriptedLLM(scripts))
            impact_llm = LLMService(_ScriptedLLM(_impact_script(assets)))

        _hr("① analyze_project — 스캔·지식화·결정적 충돌 검출")
        res = analyze_project(root_str, llm=analysis_llm)
        print(res.summary)
        print(f"자산 {res.data['assets_count']}개 / Feature {len(res.data['features'])}개 "
              f"/ 충돌 {res.data['conflicts_count']}건")

        _hr("② list_features — Feature 요약 (캐시/저장 지식, LLM 미호출)")
        for f in list_features(path=root_str).data["features"]:
            print(f"  - {f['id']}: {f['title']} (충돌 {f['conflicts_count']}건)")

        _hr("③ get_conflicts — 문서/구현 충돌 (근거 포함)")
        for c in get_conflicts(path=root_str).conflicts:
            vals = ", ".join(f"{v['value']}@{v['source']}" for v in c.values)
            print(f"  - [{c.type}] {c.claim}\n      {c.interpretation}\n      값: {vals}")

        _hr(f"④ analyze_task_impact — '{HERO_TASK}'")
        ir = analyze_task_impact(HERO_TASK, HERO_FEATURE, path=root_str, llm=impact_llm)
        print(ir.summary)
        if ir.conflicts:
            print("\n⚠ 구현 착수 전 확인해야 할 기존 충돌:")
            for c in ir.conflicts:
                print(f"  - [{c.type}] {c.claim}: {c.interpretation}")
        imp = ir.impact
        if imp is not None:
            for label, items in (("Must Change", imp.must_change),
                                 ("Likely Change", imp.likely_change),
                                 ("Review", imp.review)):
                if items:
                    print(f"\n{label}:")
                    for it in items:
                        print(f"  - {it.path}: {it.reason}")
            if imp.change_plan:
                print("\nChange Plan (충돌 해소 우선):")
                for step in imp.change_plan:
                    print(f"  {step}")

        _hr("완료 — Hero 흐름 E2E 통과"
            + (" (실제 Claude)" if live else " (API 키 없이 결정적 재현)"))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
