"""설정·LLM 세팅·제외 규칙 (UOW-0F, C7, NFR Design P7).

BR-SEC-001/002: LLMSettings는 API 키 '값'이 아니라 '환경변수 이름'만 보관.
                실제 값은 소비 직전 os.environ 에서 조회한다 (late lookup).
BR-DET-001: 결정성 파라미터(temperature=0, seed)는 여기서 중앙 관리.
설정 로딩 순서: 내장 기본값 → (선택) TOML 파일 → 환경변수 오버라이드.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from trace.common.errors import ConfigError

# 기본 제외 규칙 (스캔 대상에서 제외)
_DEFAULT_EXCLUSIONS = [
    "**/.git/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/dist/**",
    "**/build/**",
    "**/.trace/**",
]

_DEFAULT_MODEL = "claude-sonnet-5"
_DEFAULT_KEY_ENV = "ANTHROPIC_API_KEY"
_DEFAULT_KNOWLEDGE_DIR = ".trace/knowledge"
_DEFAULT_PROVIDER = "anthropic"        # "anthropic"(1st-party) | "bedrock"(Amazon Bedrock)
_PROVIDERS = ("anthropic", "bedrock")


class LLMSettings(BaseModel):
    model: str = _DEFAULT_MODEL
    provider: str = _DEFAULT_PROVIDER   # 백엔드 선택 (BR-SEC-002 유지: 값은 late lookup)
    api_key_env: str = _DEFAULT_KEY_ENV  # 키 '이름' — 값 아님 (BR-SEC-001, provider=anthropic)
    bedrock_region: str | None = None    # provider=bedrock 리전 (미지정 시 AWS 표준 체인)
    temperature: float = 0.0            # 결정성 (BR-DET-001)
    max_tokens: int = 4096
    max_retries: int = 2                # 제약 교정 재시도 (NFR-0F-REL-3)
    seed: int | None = None

    def resolve_api_key(self) -> str:
        """소비 직전 환경변수에서 키를 조회 (late lookup, P7).

        미설정 시 ConfigError — 값은 메시지에 노출하지 않는다.
        provider=anthropic 경로 전용. Bedrock은 AWS 자격증명 체인을 사용한다.
        """
        key = os.environ.get(self.api_key_env)
        if not key:
            raise ConfigError(
                f"환경변수 {self.api_key_env} 가 설정되지 않았습니다. "
                f".env 또는 셸에서 API 키를 지정하세요."
            )
        return key


class Config(BaseModel):
    exclusions: list[str] = Field(default_factory=lambda: list(_DEFAULT_EXCLUSIONS))
    llm: LLMSettings = Field(default_factory=LLMSettings)
    knowledge_dir: str = _DEFAULT_KNOWLEDGE_DIR
    raw: dict = Field(default_factory=dict)


def load_config(path: str | None = None) -> Config:
    """설정 로드: 기본값 → TOML 파일(있으면) → 환경변수 오버라이드.

    path 미지정 시 파일 로딩을 생략하고 기본값+환경변수만 사용한다.
    """
    config = Config()

    if path is not None:
        p = Path(path)
        if not p.exists():
            raise ConfigError(f"설정 파일을 찾을 수 없습니다: {path}")
        try:
            with p.open("rb") as f:
                raw = tomllib.load(f)
        except (tomllib.TOMLDecodeError, OSError) as exc:
            raise ConfigError(f"설정 파일 로드 실패: {exc}") from exc
        config = _apply_raw(config, raw)

    return _apply_env(config)


def _apply_raw(config: Config, raw: dict) -> Config:
    config.raw = raw
    if "exclusions" in raw:
        config.exclusions = list(raw["exclusions"])
    if "knowledge_dir" in raw:
        config.knowledge_dir = str(raw["knowledge_dir"])
    llm_raw = raw.get("llm", {})
    if llm_raw:
        config.llm = config.llm.model_copy(update=llm_raw)
    return config


def _apply_env(config: Config) -> Config:
    # 모델·provider·키 이름만 환경변수로 오버라이드 (자격증명 값 자체는 late lookup)
    if model := os.environ.get("TRACE_LLM_MODEL"):
        config.llm.model = model
    if provider := os.environ.get("TRACE_LLM_PROVIDER"):
        provider = provider.strip().lower()
        if provider not in _PROVIDERS:
            raise ConfigError(
                f"지원하지 않는 TRACE_LLM_PROVIDER='{provider}'. "
                f"허용: {', '.join(_PROVIDERS)}"
            )
        config.llm.provider = provider
    if key_env := os.environ.get("TRACE_API_KEY_ENV"):
        config.llm.api_key_env = key_env
    if region := (os.environ.get("TRACE_BEDROCK_REGION") or os.environ.get("AWS_REGION")):
        config.llm.bedrock_region = region
    return config


def get_exclusions(config: Config | None = None) -> list[str]:
    """제외 규칙 반환 (중복 제거, 안정 순서)."""
    cfg = config or load_config()
    seen: dict[str, None] = {}
    for pattern in cfg.exclusions:
        seen.setdefault(pattern, None)
    return list(seen.keys())


def get_llm_settings(config: Config | None = None) -> LLMSettings:
    """LLM 세팅 반환 (모델·키 이름·결정성 파라미터). 키 값은 담지 않음."""
    cfg = config or load_config()
    return cfg.llm
