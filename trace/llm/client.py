"""LLM 클라이언트 경계 (UOW-0F, NFR Design P1/P7).

LLMClient Protocol 뒤로 Claude 호출을 숨겨, 테스트에서 Fake 주입이 가능하게 한다.
AnthropicClient는 호출 직전 os.environ 에서 키를 조회한다(late lookup, BR-SEC-002).
실제 SDK 호출은 지연 임포트 — Foundation 임포트/테스트에 anthropic 설치·네트워크 불필요.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from trace.config.settings import LLMSettings


@runtime_checkable
class LLMClient(Protocol):
    """구조화 출력 이전의 원시 텍스트 완성 계약."""

    def complete(self, prompt: str, *, settings: LLMSettings) -> str:
        """prompt에 대한 모델 응답 텍스트를 반환한다."""
        ...


class AnthropicClient:
    """Anthropic Claude 기반 LLMClient 구현.

    실제 네트워크 호출부. anthropic SDK는 호출 시점에 지연 임포트한다.
    """

    def __init__(self) -> None:
        self._sdk_client = None  # 지연 생성

    def _ensure_client(self, settings: LLMSettings):  # type: ignore[no-untyped-def]
        if self._sdk_client is None:
            try:
                import anthropic
            except ImportError as exc:  # pragma: no cover - 환경 의존
                from trace.common.errors import ConfigError

                raise ConfigError(
                    "anthropic 패키지가 설치되어 있지 않습니다. `pip install anthropic`"
                ) from exc
            api_key = settings.resolve_api_key()  # late lookup (P7)
            self._sdk_client = anthropic.Anthropic(api_key=api_key)
        return self._sdk_client

    def complete(self, prompt: str, *, settings: LLMSettings) -> str:
        client = self._ensure_client(settings)
        kwargs: dict = {
            "model": settings.model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        message = client.messages.create(**kwargs)
        # content 블록들의 텍스트를 연결
        return "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
