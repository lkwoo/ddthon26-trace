"""C4 지식 저장소 — Feature 지식의 영속화 I/O (UOW-02).

FeatureKnowledge는 대상 프로젝트 하위 `.trace/knowledge/features/<id>.md` 에 **MD+YAML**
단일 진실원으로 저장한다(FR-KNOWLEDGE-002, Q5=A 캐시). 구조화 값(claims/conflicts/…)은 YAML
front matter에 두어 무손실 왕복(round-trip)을 보장하고, 사람이 읽는 서술(overview/business_rules)은
Markdown 본문으로 렌더한다(MCP 리소스로 그대로 노출, NFR-MCP-UX-002 정신).

저장소 루트는 `TRACE_HOME`(환경변수) 또는 현재 작업 디렉터리다. MCP 서버는 사용자 프로젝트
디렉터리에서 기동되므로 `list_features`/`get_feature_knowledge`가 경로 인자 없이도 같은 store를 읽는다.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from traceki.common import KnowledgeNotFoundError, get_logger
from traceki.models import FeatureKnowledge

_log = get_logger("trace.knowledge")

_FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_ID_SAFE = re.compile(r"[^a-z0-9._-]+")


def slugify(text: str) -> str:
    """Feature id로 안전한 슬러그 생성 (파일명·URI 안전)."""
    s = _ID_SAFE.sub("-", text.strip().lower()).strip("-._")
    return s or "feature"


def _render_markdown(fk: FeatureKnowledge) -> str:
    """FeatureKnowledge → MD+YAML 문서 문자열."""
    front = yaml.safe_dump(
        fk.to_dict(), allow_unicode=True, sort_keys=False, default_flow_style=False
    )
    lines = [f"---\n{front}---\n"]
    lines.append(f"# {fk.feature.title}\n")
    if fk.overview:
        lines.append(f"{fk.overview}\n")
    if fk.business_rules:
        lines.append("## 비즈니스 규칙\n")
        lines.extend(f"- {r}" for r in fk.business_rules)
        lines.append("")
    if fk.conflicts:
        lines.append("## ⚠️ 충돌\n")
        for c in fk.conflicts:
            vals = "; ".join(f"{v.value} ({v.source})" for v in c.values)
            lines.append(f"- **{c.claim}** — {c.type.value}: {vals}")
            if c.interpretation:
                lines.append(f"  - {c.interpretation}")
        lines.append("")
    if fk.dependencies:
        lines.append("## 의존\n")
        lines.extend(f"- {d}" for d in fk.dependencies)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _parse_front_matter(text: str) -> dict[str, Any]:
    m = _FRONT_MATTER.match(text)
    if not m:
        raise KnowledgeNotFoundError("지식 문서 형식이 올바르지 않습니다 (YAML front matter 없음).")
    return yaml.safe_load(m.group(1)) or {}


class KnowledgeStore:
    """`<base>/.trace/knowledge/features/<id>.md` 파일 저장소."""

    def __init__(self, base_dir: str | Path | None = None, dirname: str = ".trace"):
        base = Path(base_dir) if base_dir else Path(os.environ.get("TRACE_HOME", "")) or Path.cwd()
        self.base = Path(base)
        self.features_dir = self.base / dirname / "knowledge" / "features"

    def _path(self, feature_id: str) -> Path:
        return self.features_dir / f"{slugify(feature_id)}.md"

    def save_feature(self, fk: FeatureKnowledge) -> str:
        """FeatureKnowledge를 저장하고 파일 경로를 반환한다."""
        self.features_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(fk.feature.id)
        path.write_text(_render_markdown(fk), encoding="utf-8")
        _log.info("지식 저장: %s", path)
        return str(path)

    def load_feature(self, feature_id: str) -> FeatureKnowledge:
        path = self._path(feature_id)
        if not path.is_file():
            raise KnowledgeNotFoundError(f"Feature 지식을 찾을 수 없습니다: {feature_id}")
        data = _parse_front_matter(path.read_text(encoding="utf-8"))
        return FeatureKnowledge.from_dict(data)

    def list_feature_summaries(self) -> list[dict[str, Any]]:
        """저장된 Feature 요약 목록 (list_features용). id 정렬."""
        if not self.features_dir.is_dir():
            return []
        out: list[dict[str, Any]] = []
        for path in sorted(self.features_dir.glob("*.md")):
            try:
                fk = FeatureKnowledge.from_dict(_parse_front_matter(path.read_text(encoding="utf-8")))
            except (KnowledgeNotFoundError, yaml.YAMLError) as exc:
                _log.warning("지식 문서 읽기 실패 %s: %s", path.name, exc)
                continue
            out.append(
                {
                    "id": fk.feature.id,
                    "title": fk.feature.title,
                    "confidence": fk.confidence.value,
                    "conflicts": len(fk.conflicts),
                    "related_sources": list(fk.feature.related_sources),
                }
            )
        return out

    def read_resource(self, feature_id: str) -> str:
        """MCP 리소스 콘텐츠(Markdown 문서 전체)를 반환한다."""
        path = self._path(feature_id)
        if not path.is_file():
            raise KnowledgeNotFoundError(f"리소스를 찾을 수 없습니다: {feature_id}")
        return path.read_text(encoding="utf-8")

    def resource_path(self, feature_id: str) -> str:
        return str(self._path(feature_id))


# ------------------------------------------------------------- 모듈 기본 store
def default_store() -> KnowledgeStore:
    """환경(TRACE_HOME)·cwd 기준 기본 저장소."""
    return KnowledgeStore()


def save_feature(fk: FeatureKnowledge) -> str:
    return default_store().save_feature(fk)


def load_feature(feature_id: str) -> FeatureKnowledge:
    return default_store().load_feature(feature_id)


def list_feature_summaries() -> list[dict[str, Any]]:
    return default_store().list_feature_summaries()


def read_resource(feature_id: str) -> str:
    return default_store().read_resource(feature_id)


__all__ = [
    "KnowledgeStore",
    "slugify",
    "default_store",
    "save_feature",
    "load_feature",
    "list_feature_summaries",
    "read_resource",
]
