"""FeatureKnowledge ↔ MD+YAML Front Matter 직렬화 (UOW-0F, NFR Design P6/P8).

Q4=A: YAML Front Matter가 구조적 진실원, Markdown 본문은 사람이 읽는 파생 렌더.
NFR-0F-DET-1: sort_keys + 리스트 정렬 고정 → 같은 입력은 바이트 동일 출력.
NFR-0F-SEC-4: 역직렬화는 yaml.safe_load 만 사용.
BR-VAL-005: 필수 필드 누락/형식 오류 → StorageError (손상 파일 로드 거부).
"""

from __future__ import annotations

import yaml
from pydantic import ValidationError

from trace.common.errors import StorageError
from trace.models.domain import FeatureKnowledge

_FRONT_MATTER_DELIM = "---"


# --------------------------------------------------------------------------- #
# 직렬화
# --------------------------------------------------------------------------- #
def _sorted_dump(fk: FeatureKnowledge) -> dict:
    """결정적 직렬화를 위해 리스트를 안정 정렬한 dict를 만든다."""
    data = fk.model_dump(mode="json")
    # 리스트 정렬 키 고정 (BR-DET-002)
    data["claims"] = sorted(
        data.get("claims", []), key=lambda c: (c["subject"], c["predicate"], c["value"])
    )
    data["evidence"] = sorted(
        data.get("evidence", []), key=lambda e: (e["source"], e["location"])
    )
    data["confidence"] = sorted(
        data.get("confidence", []), key=lambda c: c["claim_key"]
    )
    data["conflicts"] = sorted(data.get("conflicts", []), key=lambda c: c["claim"])
    # body_markdown 은 본문으로 별도 렌더하므로 Front Matter에서 제외
    data.pop("body_markdown", None)
    return data


def render_body(fk: FeatureKnowledge) -> str:
    """사람이 읽는 Markdown 본문 렌더 (파생물)."""
    lines = [f"# {fk.feature.title}", "", fk.feature.description, ""]
    if fk.conflicts:
        lines.append("## ⚠ 충돌")
        for c in fk.conflicts:
            vals = ", ".join(f"{cv.value}({cv.source})" for cv in c.values)
            lines.append(f"- **{c.claim}**: {vals} — {c.interpretation}")
        lines.append("")
    if fk.claims:
        lines.append("## 주장 (Claims)")
        for cl in fk.claims:
            lines.append(f"- {cl.subject}.{cl.predicate} = {cl.value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def serialize(fk: FeatureKnowledge) -> str:
    """FeatureKnowledge → 'YAML Front Matter + Markdown 본문' 문자열."""
    front = _sorted_dump(fk)
    yaml_text = yaml.safe_dump(
        front, sort_keys=True, allow_unicode=True, default_flow_style=False
    )
    # body_markdown 이 있으면 그것을, 없으면 렌더 결과를 사용. 항상 strip 후
    # 단일 trailing newline으로 정규화 → round-trip 멱등 (NFR-0F-DET-1).
    body = (fk.body_markdown.strip() or render_body(fk).strip())
    return f"{_FRONT_MATTER_DELIM}\n{yaml_text}{_FRONT_MATTER_DELIM}\n\n{body}\n"


# --------------------------------------------------------------------------- #
# 역직렬화
# --------------------------------------------------------------------------- #
def _split_front_matter(text: str) -> tuple[str, str]:
    """'--- yaml --- body' 를 (yaml_text, body)로 분리."""
    stripped = text.lstrip()
    if not stripped.startswith(_FRONT_MATTER_DELIM):
        raise StorageError("지식 파일에 YAML Front Matter가 없습니다.")
    # 첫 '---' 이후, 다음 '---' 라인까지가 Front Matter
    rest = stripped[len(_FRONT_MATTER_DELIM):]
    end = rest.find(f"\n{_FRONT_MATTER_DELIM}")
    if end == -1:
        raise StorageError("YAML Front Matter 종료 구분자를 찾지 못했습니다.")
    yaml_text = rest[:end]
    body = rest[end + len(_FRONT_MATTER_DELIM) + 1:].lstrip("\n")
    return yaml_text, body


def deserialize(text: str) -> FeatureKnowledge:
    """지식 파일 문자열 → FeatureKnowledge (YAML Front Matter만 파싱, Q4=A)."""
    yaml_text, body = _split_front_matter(text)
    try:
        data = yaml.safe_load(yaml_text) or {}  # NFR-0F-SEC-4: safe_load
    except yaml.YAMLError as exc:
        raise StorageError(f"YAML 파싱 실패: {exc}") from exc
    if not isinstance(data, dict):
        raise StorageError("지식 파일 Front Matter가 매핑이 아닙니다.")
    data["body_markdown"] = body
    try:
        return FeatureKnowledge.model_validate(data)
    except ValidationError as exc:
        raise StorageError(f"지식 파일 검증 실패: {exc}") from exc
