"""공통 오류 타입 계층 (UOW-0F, NFR Design P3).

BR-ERR-001: 모든 도메인/서비스 오류는 TraceError 하위 타입으로 raise.
BR-ERR-002: 어댑터(C1 MCP / C9 CLI)가 이 예외를 사용자용 Result로 변환 —
            stack trace·내부 경로 원문은 노출하지 않는다.
"""

from __future__ import annotations


class TraceError(Exception):
    """TRACE 도메인/서비스 오류의 베이스 타입."""

    #: 기계 판별용 코드 (Warning.code 및 로그와 정합)
    code: str = "TRACE_ERROR"


class ConfigError(TraceError):
    """설정·환경변수·템플릿 로드 실패 (예: API 키 미설정, 템플릿 미존재)."""

    code = "CONFIG_ERROR"


class PathValidationError(TraceError):
    """스캔/저장 경로가 허용 루트를 벗어나거나 접근 불가 (NFR-SEC-004)."""

    code = "PATH_VALIDATION_ERROR"


class ParseError(TraceError):
    """자산 파싱 실패 — 대개 부분 실패로 warning 강등 가능 (FR-ANALYSIS-003)."""

    code = "PARSE_ERROR"


class LLMValidationError(TraceError):
    """LLM 구조화 출력이 재시도(제약 교정)를 소진하고도 스키마 검증 실패 (P2)."""

    code = "LLM_VALIDATION_ERROR"


class StorageError(TraceError):
    """.trace 지식 저장소 I/O 또는 역직렬화 실패 (손상 파일 로드 거부 포함)."""

    code = "STORAGE_ERROR"


def sanitize_error(exc: BaseException) -> str:
    """예외를 사용자/로그용 안전 요약으로 변환 (UOW-01 P5, BR-SEC-001).

    파일 내용·시크릿·전체 절대경로·스택 트레이스를 노출하지 않고,
    예외 타입명과 (있으면) 짧은 메시지 첫 줄만 남긴다.
    """
    name = type(exc).__name__
    message = str(exc).splitlines()[0].strip() if str(exc) else ""
    # 절대경로로 보이는 토큰 제거 (드라이브 문자/슬래시 시작)
    safe_tokens = [
        tok
        for tok in message.split()
        if not (tok.startswith(("/", "\\")) or (len(tok) > 1 and tok[1] == ":"))
    ]
    safe_message = " ".join(safe_tokens)
    return f"{name}: {safe_message}" if safe_message else name


def error_to_result(error: TraceError) -> "Result":
    """TraceError를 사용자용 Result로 변환 (어댑터 경계 전용, P3).

    코어는 예외를 raise만 하고, C1/C9 어댑터가 이 헬퍼로 사용자 표현을 만든다.
    내부 스택/경로 원문은 담지 않고 code+안전한 메시지만 전달한다.
    """
    # 지연 임포트로 순환 의존 회피 (result → 이 모듈 참조 없음, 방향 유지)
    from trace.models.result import Result, Warning

    return Result(
        summary=f"요청을 완료하지 못했습니다: {error}",
        data={},
        warnings=[Warning(code=error.code, message=str(error))],
        meta={"error": True, "error_code": error.code},
    )
