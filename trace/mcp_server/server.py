"""MCP 서버 구성 (UOW-05, C1, NFR Design P1/P2/P4/P5).

build_server(): MCPServer에 5 도구·지식 리소스·구현전검토 프롬프트를 등록해 반환한다.
각 도구 핸들러는 얇다 — 입력→루트 주입→코어 함수→serialize_result. 코어 예외는
error_to_result로 흡수해 구조화 오류를 반환한다(서버 크래시 없음, NFR-05-REL-1).

`mcp` SDK는 이 모듈에서만 임포트된다(지연) — 코어·대다수 테스트는 mcp 불필요.
설치 환경: mcp 2.x, `from mcp.server.mcpserver import MCPServer`(구 FastMCP).
"""

from __future__ import annotations

import os
from typing import Any

from trace.common.errors import error_to_result
from trace.engine import (
    analyze_project,
    analyze_task_impact,
    get_conflicts,
    get_feature_knowledge,
    list_features,
)
from trace.knowledge.store import KnowledgeStore
from trace.mcp_server.serialize import serialize_result


def _root() -> str:
    """프로젝트 루트: TRACE_PROJECT_ROOT 환경변수 우선, 없으면 현재 작업 디렉터리 (NFR-05-RUN-3)."""
    return os.environ.get("TRACE_PROJECT_ROOT") or os.getcwd()


def build_server() -> Any:
    """5 도구·리소스·프롬프트가 등록된 MCPServer를 구성해 반환한다."""
    from mcp.server.mcpserver import MCPServer  # 지연 임포트

    server = MCPServer(name="trace", version="0.1.0",
                       instructions="TRACE — 프로젝트 지식·문서/구현 충돌·작업 영향을 근거와 함께 제공하는 로컬 MCP 서버")

    @server.tool()
    def trace_analyze_project() -> dict:
        """프로젝트를 스캔·지식화하고 문서/구현 충돌을 검출한다."""
        try:
            return serialize_result(analyze_project(_root()))
        except Exception as exc:  # noqa: BLE001
            return serialize_result(error_to_result(exc))

    @server.tool()
    def trace_list_features() -> dict:
        """식별된 Feature 요약 목록을 반환한다."""
        try:
            return serialize_result(list_features(path=_root()))
        except Exception as exc:  # noqa: BLE001
            return serialize_result(error_to_result(exc))

    @server.tool()
    def trace_get_feature_knowledge(feature_id: str) -> dict:
        """한 Feature의 지식(claims·confidence·conflicts·리소스 URI)을 반환한다."""
        try:
            return serialize_result(get_feature_knowledge(feature_id, path=_root()))
        except Exception as exc:  # noqa: BLE001
            return serialize_result(error_to_result(exc))

    @server.tool()
    def trace_get_conflicts(feature_id: str | None = None) -> dict:
        """검출된 문서/구현 충돌을 (Feature별 또는 전체) 반환한다."""
        try:
            return serialize_result(get_conflicts(feature_id, path=_root()))
        except Exception as exc:  # noqa: BLE001
            return serialize_result(error_to_result(exc))

    @server.tool()
    def trace_analyze_task_impact(task: str, feature_id: str | None = None) -> dict:
        """자연어 변경 작업의 영향(Must/Likely/Review)·관련 충돌·Change Plan을 근거와 함께 분석한다."""
        try:
            return serialize_result(analyze_task_impact(task, feature_id, path=_root()))
        except Exception as exc:  # noqa: BLE001
            return serialize_result(error_to_result(exc))

    @server.resource("trace://feature/{feature_id}")
    def feature_resource(feature_id: str) -> str:
        """Feature 지식 본문(Markdown)을 리소스로 노출한다 (FR-MCP-002)."""
        return KnowledgeStore(_root()).read_resource(f"trace://feature/{feature_id}")

    @server.prompt()
    def review_before_implementation(task: str) -> str:
        """구현 착수 전 충돌·영향을 검토하도록 유도하는 프롬프트 (FR-MCP-003, P1)."""
        return (
            f"구현을 시작하기 전에 TRACE로 아래 작업의 리스크를 검토하세요:\n\n"
            f"작업: {task}\n\n"
            f"1) `trace_get_conflicts`로 관련 기능의 미해소 문서/구현 충돌을 확인하세요.\n"
            f"2) `trace_analyze_task_impact`(task 전달)로 영향 파일(Must/Likely/Review)과 순서형 Change Plan을 받으세요.\n"
            f"3) 충돌이 있으면 먼저 해소한 뒤 구현에 착수하세요. 근거(Evidence)를 함께 확인하세요."
        )

    return server


__all__ = ["build_server"]
