"""C1 MCP 어댑터 — TRACE 코어 함수를 MCP 도구/리소스로 노출 (UOW-05).

설계 원칙(NFR-CORE-001/002): 어댑터는 **얇다**. 5개 MCP 도구는 엔진의 코어 함수와 1:1로 매핑되고,
비즈니스 로직은 전혀 갖지 않는다. 모든 도구는 공통 Result를 `to_dict()`(핵심 우선 순서,
NFR-MCP-UX-002)로 직렬화해 반환하므로, 에이전트(Claude Code)가 summary를 그대로 설명하고
conflicts/impact를 상위에서 읽을 수 있다.

전송은 stdio다. 로깅은 stderr로만 나가 stdout(MCP 프레이밍)을 오염시키지 않는다(common.get_logger).
`mcp` 패키지는 서버 기동 시에만 필요하므로 지연 임포트한다(코어·테스트는 오프라인).

진입점: `trace-mcp` → `main()`.
"""

from __future__ import annotations

from typing import Any

from traceki.common import get_logger
from traceki.config import load_config
from traceki.conflict import get_conflicts as _get_conflicts
from traceki.engine import analyze_project as _analyze_project
from traceki.engine import get_feature_knowledge as _get_feature_knowledge
from traceki.engine import list_features as _list_features
from traceki.impact import analyze_task_impact as _analyze_task_impact
from traceki.knowledge import default_store

_log = get_logger("trace.mcp")

INSTRUCTIONS = (
    "TRACE reconstructs scattered dev assets into feature-centric, evidence-based knowledge and "
    "flags value_mismatch conflicts BEFORE you write code. Typical flow: call analyze_project(path) "
    "once, then list_features / get_feature_knowledge / get_conflicts, and analyze_task_impact(task) "
    "before starting a change. Every result has a human 'summary' plus structured 'data'/'conflicts'/'impact'."
)


def build_server() -> Any:
    """MCPServer 인스턴스를 구성한다. 코어 함수 5개 = 도구 5개, 지식은 리소스로 노출."""
    from mcp.server.mcpserver import MCPServer  # 지연 임포트 (mcp 2.x)

    from traceki import __version__

    mcp = MCPServer(name="trace", version=__version__, instructions=INSTRUCTIONS)
    config = load_config(".")  # 서버 cwd의 .env·환경에서 LLM 백엔드/키 결정

    # ---------------------------------------------------------------- 도구 (코어 1:1)
    @mcp.tool(description="프로젝트를 스캔·분석해 Feature 중심 지식과 충돌을 생성한다(1회 실행). data: features, conflicts_count, assets_count.")
    def analyze_project(path: str = ".", refresh: bool = False) -> dict:
        return _analyze_project(path, config=config, refresh=refresh).to_dict()

    @mcp.tool(description="검출된 Feature 요약 목록을 반환한다.")
    def list_features() -> dict:
        return _list_features().to_dict()

    @mcp.tool(description="단일 Feature의 지식(overview·business_rules·claims·conflicts·dependencies)을 반환한다.")
    def get_feature_knowledge(feature_id: str) -> dict:
        return _get_feature_knowledge(feature_id).to_dict()

    @mcp.tool(description="value_mismatch 등 충돌 목록을 반환한다. feature_id 생략 시 전체 프로젝트.")
    def get_conflicts(feature_id: str | None = None) -> dict:
        return _get_conflicts(feature_id).to_dict()

    @mcp.tool(description="자연어 작업의 영향 범위를 착수 전 분석한다: Must/Likely/Review + 충돌 경고 + 순서형 Change Plan.")
    def analyze_task_impact(task: str, feature_id: str | None = None) -> dict:
        return _analyze_task_impact(task, feature_id=feature_id, config=config).to_dict()

    # ---------------------------------------------------------------- 리소스 (지식 노출)
    @mcp.resource("trace://features", description="분석된 Feature id·제목·충돌 수 목록.", mime_type="text/markdown")
    def features_index() -> str:
        summaries = default_store().list_feature_summaries()
        if not summaries:
            return "# TRACE\n\n아직 분석된 Feature가 없습니다. `analyze_project`를 먼저 실행하세요.\n"
        lines = ["# TRACE Features\n"]
        for s in summaries:
            flag = f" ⚠️ 충돌 {s['conflicts']}건" if s["conflicts"] else ""
            lines.append(f"- `trace://feature/{s['id']}` — {s['title']} (신뢰도 {s['confidence']}){flag}")
        return "\n".join(lines) + "\n"

    @mcp.resource(
        "trace://feature/{feature_id}",
        description="단일 Feature 지식 문서(MD+YAML).",
        mime_type="text/markdown",
    )
    def feature_resource(feature_id: str) -> str:
        try:
            return default_store().read_resource(feature_id)
        except Exception as exc:  # noqa: BLE001
            return f"# 지식 없음\n\n{exc}\n"

    _log.info("TRACE MCP 서버 구성 완료: 도구 5, 리소스 2 (backend=%s)", config.llm.backend)
    return mcp


def main() -> None:
    """`trace-mcp` 진입점 — stdio로 MCP 서버를 기동한다."""
    try:
        server = build_server()
    except ImportError as exc:  # mcp 미설치
        _log.error("MCP 서버를 시작할 수 없습니다: %s. `pip install -e .` 로 mcp를 설치하세요.", exc)
        raise SystemExit(1) from exc
    _log.info("TRACE MCP 서버 시작 (stdio)")
    server.run(transport="stdio")


__all__ = ["build_server", "main"]
