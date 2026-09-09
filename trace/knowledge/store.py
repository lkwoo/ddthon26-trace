"""지식 저장소 (UOW-02, C4, NFR Design P4, BR-STORE).

<project_root>/.trace/knowledge/features/<id>.md 로 FeatureKnowledge를 MD+YAML 저장/로드.
serialize/deserialize(UOW-0F) 사용. 저장 경로는 항상 루트 하위(트래버설 금지).
"""

from __future__ import annotations

from pathlib import Path

from trace.common.errors import StorageError
from trace.common.logging import get_logger
from trace.knowledge.ids import safe_feature_id
from trace.models.domain import FeatureKnowledge
from trace.models.result import FeatureSummary
from trace.models.serialize import deserialize, serialize

_log = get_logger("trace.knowledge.store")

_RESOURCE_PREFIX = "trace://feature/"


class KnowledgeStore:
    def __init__(self, project_root: str | Path, knowledge_dir: str = ".trace/knowledge") -> None:
        self._root = Path(project_root)
        self._knowledge_dir = knowledge_dir

    def features_dir(self) -> Path:
        return self._root / self._knowledge_dir / "features"

    def _feature_path(self, feature_id: str) -> Path:
        safe = safe_feature_id(feature_id)  # 방어: 경로 이탈 차단
        return self.features_dir() / f"{safe}.md"

    def save_feature(self, fk: FeatureKnowledge) -> str:
        """FeatureKnowledge 저장. 저장 경로(문자열) 반환."""
        path = self._feature_path(fk.feature.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialize(fk), encoding="utf-8")
        _log.info(f"event=feature_saved id={fk.feature.id}")
        return str(path)

    def load_feature(self, feature_id: str) -> FeatureKnowledge:
        path = self._feature_path(feature_id)
        if not path.exists():
            raise StorageError(f"지식 파일을 찾을 수 없습니다: {feature_id}")
        try:
            return deserialize(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise StorageError(f"지식 파일 읽기 실패: {feature_id}") from exc

    def list_feature_summaries(self) -> list[FeatureSummary]:
        """features/*.md 를 로드해 요약 목록 생성 (손상 파일은 skip, 결정적 정렬)."""
        fdir = self.features_dir()
        if not fdir.exists():
            return []
        summaries: list[FeatureSummary] = []
        for path in sorted(fdir.glob("*.md")):
            try:
                fk = deserialize(path.read_text(encoding="utf-8"))
            except (StorageError, OSError) as exc:
                _log.warning(f"event=feature_load_skip file={path.name} error_type={type(exc).__name__}")
                continue
            summaries.append(FeatureSummary(
                id=fk.feature.id,
                title=fk.feature.title,
                confidence=_dominant_confidence(fk),
                conflicts_count=len(fk.conflicts),
                related_sources=list(fk.feature.related_sources),
            ))
        summaries.sort(key=lambda s: s.id)
        return summaries

    def read_resource(self, uri: str) -> str:
        """trace://feature/<id> → body_markdown."""
        if not uri.startswith(_RESOURCE_PREFIX):
            raise StorageError(f"지원하지 않는 리소스 URI: {uri}")
        feature_id = uri[len(_RESOURCE_PREFIX):]
        return self.load_feature(feature_id).body_markdown


def _dominant_confidence(fk: FeatureKnowledge) -> str | None:
    """요약용 대표 신뢰도(가장 낮은 수준 우선 — 주의 환기)."""
    if not fk.confidence:
        return None
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    levels = [c.assessment.level.value for c in fk.confidence]
    return min(levels, key=lambda lv: order.get(lv, 3))


__all__ = ["KnowledgeStore"]
