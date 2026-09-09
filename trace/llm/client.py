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

    provider 에 따라 백엔드를 선택한다(둘 다 anthropic SDK):
      * "anthropic" — 1st-party API. ANTHROPIC_API_KEY(late lookup).
      * "bedrock"   — Amazon Bedrock. AWS 표준 자격증명 체인(AWS_ACCESS_KEY_ID/…/AWS_REGION),
                      모델은 Bedrock 모델 ID/inference profile 이어야 하므로 TRACE_LLM_MODEL 필수.
    실제 네트워크 호출부. anthropic SDK는 호출 시점에 지연 임포트한다.
    """

    def __init__(self) -> None:
        self._sdk_client: object = None  # 지연 생성 (Anthropic | AnthropicBedrock)

    def _ensure_client(self, settings: LLMSettings):  # type: ignore[no-untyped-def]
        if self._sdk_client is not None:
            return self._sdk_client

        from trace.common.errors import ConfigError

        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - 환경 의존
            raise ConfigError(
                "anthropic 패키지가 설치되어 있지 않습니다. `pip install anthropic`"
            ) from exc

        provider = (settings.provider or "anthropic").lower()
        if provider == "bedrock":
            try:
                from anthropic import AnthropicBedrock
            except ImportError as exc:  # pragma: no cover - 환경 의존
                raise ConfigError(
                    "Bedrock 백엔드에는 boto3 가 필요합니다. `pip install 'anthropic[bedrock]'`"
                ) from exc
            from trace.config.settings import _DEFAULT_MODEL
            if not settings.model or settings.model == _DEFAULT_MODEL:
                raise ConfigError(
                    "Bedrock 사용 시 TRACE_LLM_MODEL 에 Bedrock 모델 ID/inference profile 을 "
                    "지정하세요 (예: anthropic.claude-3-5-sonnet-20241022-v2:0)."
                )
            kwargs: dict = {}
            if settings.bedrock_region:
                kwargs["aws_region"] = settings.bedrock_region
            # AWS 키·리전은 SDK 표준 체인(환경변수/프로파일)에서 late lookup — 값은 보관하지 않음
            self._sdk_client = AnthropicBedrock(**kwargs)
        else:
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
