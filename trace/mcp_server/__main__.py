"""trace-mcp 엔트리포인트 (UOW-05, C1, NFR-05-RUN-1/2).

stdio 전송으로 MCP 서버를 기동한다. Claude Code 등 MCP 클라이언트가 stdio로 연결한다.
"""

from __future__ import annotations

from trace.mcp_server.server import build_server


def main() -> None:
    """stdio 전송으로 TRACE MCP 서버를 실행한다."""
    build_server().run("stdio")


if __name__ == "__main__":
    main()
