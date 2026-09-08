"""C7 설정 — 제외 규칙, 지원 확장자, LLM 설정 (UOW-0F).

시크릿(API 키)은 코드/로그에 하드코딩하지 않고 환경변수에서만 읽는다 (NFR-SEC-001).
`.env` 파일이 있으면 (외부 의존 없이) 가볍게 로드한다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# 제외 규칙 (FR-PROJECT-003) — 설정/중앙 상수로 구성 가능
DEFAULT_EXCLUSIONS: list[str] = [
    ".git", ".hg", ".svn",
    "node_modules", "bower_components",
    "build", "dist", "target", "out", "bin", "obj",
    ".idea", ".vscode", ".vs",
    "__pycache__", ".pytest_cache", ".hypothesis",
    ".venv", "venv", "env",
    ".trace",  # TRACE 자신의 산출물은 재귀 분석하지 않는다
]

# 지원 자산 유형 → 확장자 (FR-PROJECT-002). PDF는 P0.
ASSET_EXTENSIONS: dict[str, list[str]] = {
    "source": [".py", ".java", ".js", ".ts", ".go", ".rb", ".kt", ".cs", ".php"],
    "markdown": [".md", ".markdown"],
    "text": [".txt", ".rst"],
    "pdf": [".pdf"],
    "openapi": [".yaml", ".yml", ".json"],  # 내용으로 OpenAPI 여부 추가 판별
    "sql": [".sql"],
    "config": [".toml", ".ini", ".cfg", ".properties", ".env"],
    "test": [],  # 경로 규칙(tests/, *_test.*, test_*)으로 별도 판별
}


@dataclass
class LLMSettings:
    """LLM 접근 설정. 결정성 파라미터 포함 (NFR-AI-004).

    참고: Claude Sonnet 5는 temperature 등 샘플링 파라미터를 허용하지 않으므로(400),
    결정성은 구조화 출력 + replay 캐시로 확보한다. temperature 필드는 두지 않는다.
    """

    backend: str = "replay"                # "live" | "replay"
    model: str = "claude-sonnet-5"
    api_key: str | None = None
    replay_dir: str | None = None          # replay 사전 응답 디렉터리 (없으면 데모 픽스처)
    max_tokens: int = 4096


@dataclass
class Config:
    """TRACE 실행 설정."""

    exclusions: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUSIONS))
    asset_extensions: dict[str, list[str]] = field(default_factory=lambda: dict(ASSET_EXTENSIONS))
    llm: LLMSettings = field(default_factory=LLMSettings)
    knowledge_dirname: str = ".trace"      # 대상 프로젝트 기준 산출물 위치 (Q5=A)


def _load_dotenv(path: Path) -> None:
    """의존성 없이 `.env`를 os.environ에 병합 (이미 설정된 키는 덮어쓰지 않음)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(path: str | None = None) -> Config:
    """설정 로드. `path`가 주어지면 그 디렉터리의 `.env`를 먼저 병합한다."""
    if path:
        _load_dotenv(Path(path) / ".env")
    _load_dotenv(Path.cwd() / ".env")
    return Config(llm=get_llm_settings())


def get_exclusions(config: Config | None = None) -> list[str]:
    return list((config or Config()).exclusions)


def get_llm_settings() -> LLMSettings:
    """환경변수에서 LLM 설정을 읽는다. API 키는 여기서만 접근 (NFR-SEC-001)."""
    return LLMSettings(
        backend=os.environ.get("TRACE_LLM_BACKEND", "replay").lower(),
        model=os.environ.get("TRACE_LLM_MODEL", "claude-sonnet-5"),
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        replay_dir=os.environ.get("TRACE_REPLAY_DIR"),
    )


__all__ = [
    "DEFAULT_EXCLUSIONS",
    "ASSET_EXTENSIONS",
    "LLMSettings",
    "Config",
    "load_config",
    "get_exclusions",
    "get_llm_settings",
]
