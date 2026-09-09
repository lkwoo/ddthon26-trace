"""LLMService — 구조화 출력 검증 + 제약 교정 재시도 (UOW-0F, NFR Design P1/P2).

complete_structured(prompt, schema): Claude 호출 → JSON 파싱 → Pydantic 검증.
검증 실패 시 스키마 오류 요약을 덧붙여 max_retries까지 재프롬프트(제약 교정),
소진 시 LLMValidationError (호출한 AI 단위가 warning 강등 여부 결정).
결정성 파라미터는 settings에서만 취득 (하드코딩 금지, BR-DET-001).
"""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from trace.common.errors import LLMValidationError
from trace.common.logging import get_logger
from trace.config.settings import LLMSettings, get_llm_settings
from trace.llm.client import LLMClient

T = TypeVar("T", bound=BaseModel)

_CORRECTION_HINT = (
    "\n\n[중요] 이전 응답이 요구 스키마를 만족하지 못했습니다. "
    "아래 오류를 반영해 **유효한 JSON만** 출력하세요(코드펜스·설명 금지):\n{errors}\n"
    "요구 JSON 스키마:\n{schema}"
)


class LLMService:
    """LLMClient를 감싸 구조화·검증·재시도를 담당한다."""

    def __init__(self, client: LLMClient, settings: LLMSettings | None = None) -> None:
        self._client = client
        self._settings = settings or get_llm_settings()
        self._log = get_logger("trace.llm")

    def complete_structured(self, prompt: str, schema: type[T]) -> T:
        """prompt 응답을 schema(Pydantic 모델)로 검증해 반환.

        실패 시 제약 교정으로 재시도, 소진되면 LLMValidationError.
        """
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        current_prompt = prompt
        last_error: Exception | None = None

        for attempt in range(self._settings.max_retries + 1):
            raw = self._client.complete(current_prompt, settings=self._settings)
            try:
                payload = self._extract_json(raw)
                return schema.model_validate(payload)
            except (ValueError, ValidationError) as exc:
                last_error = exc
                self._log.warning(
                    f"event=llm_validation_retry attempt={attempt} "
                    f"error_type={type(exc).__name__}"
                )
                current_prompt = prompt + _CORRECTION_HINT.format(
                    errors=str(exc), schema=schema_json
                )

        raise LLMValidationError(
            f"{schema.__name__} 구조화 출력 검증을 {self._settings.max_retries + 1}회 "
            f"시도했으나 실패했습니다: {last_error}"
        )

    @staticmethod
    def _extract_json(raw: str) -> object:
        """응답 텍스트에서 JSON 페이로드를 파싱. 코드펜스가 있으면 벗겨낸다."""
        text = raw.strip()
        if text.startswith("```"):
            # ```json ... ``` 또는 ``` ... ``` 제거
            text = text.split("```", 2)[1] if text.count("```") >= 2 else text
            if text.startswith("json"):
                text = text[len("json"):]
            text = text.strip("`").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON 파싱 실패: {exc}") from exc
