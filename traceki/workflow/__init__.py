"""C3 AI 워크플로우 — 구조화 출력 LLM step (UOW-02 부분).

UOW-02 담당 step:
- `identify_features`      : 자산에서 Feature 자동 검출 (FR-KNOWLEDGE-001)
- `generate_feature_knowledge`: Feature별 서술 지식 생성 (FR-KNOWLEDGE-002)

UOW-03이 `extract_claims`/`group_evidence`/`assign_confidence`를 이 모듈에 추가한다.

각 step은 `LLMService.structured(step_key, prompt)`로 파싱된 JSON을 받는다. replay 백엔드는
`step_key`로 사전 응답을 재생하고, live 백엔드는 `prompts.get_prompt(...)`로 렌더한 프롬프트를 쓴다.
근거 그라운딩(NFR-AI-002)을 위해 프롬프트에 자산 발췌를 주입한다.
"""

from __future__ import annotations

from typing import Any

from traceki.common import get_logger
from traceki.engine.assets import Asset
from traceki.knowledge import slugify
from traceki.llm import LLMService
from traceki.models import Claim, Evidence, EvidenceRelation, Feature, FeatureKnowledge
from traceki.prompts import get_prompt

_log = get_logger("trace.workflow")

# 프롬프트에 넣을 자산당 최대 발췌 길이 (토큰·비용 방어)
_EXCERPT_CHARS = 2000


def render_assets(assets: list[Asset], limit: int = _EXCERPT_CHARS) -> str:
    """자산 목록을 프롬프트용 텍스트 블록으로 렌더 (경로·유형·발췌)."""
    blocks: list[str] = []
    for a in assets:
        excerpt = (a.content or "")[:limit]
        blocks.append(f"### {a.path} ({a.type})\n{excerpt}")
    return "\n\n".join(blocks)


def identify_features(assets: list[Asset], llm: LLMService) -> list[Feature]:
    """자산 집합에서 Feature 후보를 자동 검출한다 (FR-KNOWLEDGE-001).

    replay step_key: ``identify_features``.
    """
    prompt = get_prompt("identify_features", assets=render_assets(assets))
    raw = llm.structured("identify_features", prompt)
    features = _coerce_features(raw)
    _log.info("Feature 검출: %d개", len(features))
    return features


def generate_feature_knowledge(
    feature: Feature,
    assets: list[Asset],
    llm: LLMService,
    claims: list | None = None,
    conflicts: list | None = None,
) -> FeatureKnowledge:
    """Feature의 서술 지식(overview·business_rules·dependencies)을 생성한다.

    claims/conflicts는 UOW-03 파이프라인이 채워 넘긴다(UOW-02 단독 실행 시 빈 목록).
    replay step_key: ``generate_knowledge.<feature_id>``.
    """
    related = [a for a in assets if a.path in set(feature.related_sources)] or assets
    prompt = get_prompt(
        "generate_knowledge",
        feature_title=feature.title,
        feature_description=feature.description,
        assets=render_assets(related),
    )
    raw = llm.structured(f"generate_knowledge.{feature.id}", prompt)
    data = raw if isinstance(raw, dict) else {}
    from traceki.models import Confidence

    return FeatureKnowledge(
        feature=feature,
        overview=str(data.get("overview", "")),
        business_rules=[str(r) for r in data.get("business_rules", [])],
        claims=list(claims or []),
        conflicts=list(conflicts or []),
        dependencies=[str(d) for d in data.get("dependencies", [])],
        confidence=Confidence.MEDIUM,
    )


def extract_claims(feature: Feature, assets: list[Asset], llm: LLMService) -> list[Claim]:
    """Feature에서 정규화 원자 Claim(subject·predicate·value) + Evidence를 추출한다.

    이것이 TRACE의 구조적 차별점의 입력이다(FR-CLAIM-001): 자유 텍스트가 아니라
    (subject, predicate, value) 삼중항으로 정규화하므로, 같은 (subject.predicate)에 서로 다른
    value가 붙으면 결정적 코드로 value_mismatch를 검출할 수 있다(UOW-03 detect_conflicts).

    replay step_key: ``extract_claims.<feature_id>``.
    """
    related = [a for a in assets if a.path in set(feature.related_sources)] or assets
    prompt = get_prompt(
        "extract_claims",
        feature_title=feature.title,
        assets=render_assets(related),
    )
    raw = llm.structured(f"extract_claims.{feature.id}", prompt)
    claims = _coerce_claims(raw)
    _log.info("Claim 추출: %s → %d개", feature.id, len(claims))
    return claims


def analyze_task(task: str, task_id: str, context: str, llm: LLMService) -> dict:
    """자연어 작업을 지식 컨텍스트에 그라운딩해 영향 범위를 분석한다 (FR-IMPACT-002).

    지식(Claim·충돌·소스)에 근거해 변경 파일을 Must/Likely/Review로 분류하고 순서형 계획을 낸다.
    소스를 자동 수정하지 않는다(FR-IMPACT-003 — 제안만).

    replay step_key: ``analyze_task.<task_id>``. 반환 dict은 impact 컴포넌트가 정규화한다.
    """
    prompt = get_prompt("analyze_task", task=task, context=context)
    raw = llm.structured(f"analyze_task.{task_id}", prompt)
    return raw if isinstance(raw, dict) else {}


def group_evidence(claims: list[Claim]) -> list[Claim]:
    """동일 (key, value) Claim을 병합하고 Evidence를 중복 제거한다 (FR-EVIDENCE-001).

    LLM이 같은 주장을 여러 번 내도 근거만 합쳐 하나의 Claim으로 정규화한다. 서로 다른 value는
    별개 Claim으로 유지되어 충돌 검출의 입력이 된다.
    """
    merged: dict[tuple[str, str], Claim] = {}
    for c in claims:
        gkey = (c.key, c.value.strip())
        if gkey not in merged:
            merged[gkey] = Claim(c.subject, c.predicate, c.value, evidence=[], confidence=c.confidence)
        target = merged[gkey]
        seen = {(e.source, e.location, e.extracted_value) for e in target.evidence}
        for e in c.evidence:
            sig = (e.source, e.location, e.extracted_value)
            if sig not in seen:
                target.evidence.append(e)
                seen.add(sig)
    return list(merged.values())


# ------------------------------------------------------------------ 강제 변환
def _coerce_claims(raw: Any) -> list[Claim]:
    """LLM 원시 출력을 Claim 목록으로 관대하게 변환한다."""
    items = raw.get("claims") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    out: list[Claim] = []
    for item in items:
        if not isinstance(item, dict) or not item.get("subject") or not item.get("predicate"):
            continue
        evs: list[Evidence] = []
        for e in item.get("evidence", []):
            if not isinstance(e, dict) or not e.get("source"):
                continue
            try:
                rel = EvidenceRelation(str(e.get("relation", "supporting")))
            except ValueError:
                rel = EvidenceRelation.SUPPORTING
            evs.append(
                Evidence(
                    source=str(e["source"]),
                    type=str(e.get("type", "")),
                    location=str(e.get("location", "")),
                    extracted_value=str(e.get("extracted_value", "")),
                    relation=rel,
                )
            )
        out.append(
            Claim(
                subject=str(item["subject"]).strip(),
                predicate=str(item["predicate"]).strip(),
                value=str(item.get("value", "")).strip(),
                evidence=evs,
            )
        )
    return out


def _coerce_features(raw: Any) -> list[Feature]:
    """LLM 원시 출력을 Feature 목록으로 관대하게 변환한다."""
    items = raw.get("features") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    out: list[Feature] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not (item.get("title") or item.get("id")):
            continue
        title = str(item.get("title") or item.get("id"))
        fid = slugify(str(item.get("id") or title))
        out.append(
            Feature(
                id=fid,
                title=title,
                description=str(item.get("description", "")),
                related_sources=[str(s) for s in item.get("related_sources", [])],
            )
        )
    return out


__all__ = [
    "identify_features",
    "generate_feature_knowledge",
    "extract_claims",
    "group_evidence",
    "analyze_task",
    "render_assets",
]
