"""S4 LLMService — Claude 접근 캡슐화 + 결정적 replay (UOW-0F).

두 백엔드를 지원한다:
- **live**: 실제 Anthropic Claude 호출. 구조화(JSON) 출력을 요구하고 검증하며, 파싱 실패 시
  제약 교정 재시도 1회(§17.4). Claude Sonnet 5는 샘플링 파라미터를 허용하지 않으므로
  temperature를 보내지 않는다(400 방지).
- **replay**: 사전 저장된 응답을 재생. **API 키 없이** Hero 데모를 결정적으로 재현한다
  (NFR-AI-004 시연 안정성, NFR-REL-001 반복 가능 E2E).

C3 워크플로우 step들은 `service.structured(step_key, prompt)`로 파싱된 JSON을 얻는다.
`anthropic` 패키지는 live 모드에서만 지연 임포트한다(코어 로직 오프라인 테스트 가능).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from trace.common import ConfigError, LLMError, get_logger
from trace.config import LLMSettings

_log = get_logger("trace.llm")

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(text: str) -> Any:
    """모델 응답에서 JSON을 관대하게 추출한다(코드펜스 허용)."""
    candidate = text.strip()
    m = _JSON_FENCE.search(candidate)
    if m:
        candidate = m.group(1).strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # 본문 중 첫 {..} 또는 [..] 블록 시도
        for opener, closer in (("{", "}"), ("[", "]")):
            start, end = candidate.find(opener), candidate.rfind(closer)
            if 0 <= start < end:
                try:
                    return json.loads(candidate[start : end + 1])
                except json.JSONDecodeError:
                    continue
        raise


def _safe_key(step_key: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", step_key)


class LLMService:
    """LLM 접근 파사드. `structured()`가 유일한 공개 진입점."""

    def __init__(self, settings: LLMSettings, replay_dir: str | Path | None = None):
        self.settings = settings
        # replay 우선순위: 명시 인자 > 설정(env TRACE_REPLAY_DIR)
        rd = replay_dir or settings.replay_dir
        self.replay_dir = Path(rd) if rd else None
        self._client = None  # live 클라이언트 지연 생성

    # ------------------------------------------------------------------ live
    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.settings.api_key:
            raise ConfigError(
                "live LLM 백엔드에 ANTHROPIC_API_KEY가 필요합니다. "
                "환경변수를 설정하거나 TRACE_LLM_BACKEND=replay 로 실행하세요."
            )
        try:
            import anthropic  # 지연 임포트
        except ImportError as exc:  # pragma: no cover
            raise ConfigError("`anthropic` 패키지가 설치되어 있지 않습니다.") from exc
        self._client = anthropic.Anthropic(api_key=self.settings.api_key)
        return self._client

    def _call_live(self, prompt: str) -> str:
        client = self._get_client()
        # Sonnet 5: temperature 등 샘플링 파라미터 금지. 구조화 출력은 프롬프트 지시로 유도.
        resp = client.messages.create(
            model=self.settings.model,
            max_tokens=self.settings.max_tokens,
            system=(
                "You are TRACE's structured extraction engine. "
                "Always respond with a single valid JSON value and nothing else. "
                "Ground every value in the provided source excerpts; never invent sources."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        return "".join(parts)

    def _structured_live(self, prompt: str) -> Any:
        raw = self._call_live(prompt)
        try:
            return _extract_json(raw)
        except json.JSONDecodeError:
            # 제약 교정 재시도 1회 (§17.4)
            _log.warning("live 구조화 출력 파싱 실패 — 제약 교정 재시도")
            retry = self._call_live(
                prompt + "\n\nIMPORTANT: Your previous reply was not valid JSON. "
                "Respond with ONLY a single valid JSON value, no prose, no code fences."
            )
            try:
                return _extract_json(retry)
            except json.JSONDecodeError as exc:
                raise LLMError("LLM이 유효한 JSON을 반환하지 않았습니다(재시도 후).") from exc

    # ---------------------------------------------------------------- replay
    def _structured_replay(self, step_key: str) -> Any:
        if self.replay_dir is None or not self.replay_dir.is_dir():
            raise LLMError(
                f"replay 백엔드에 사전 응답 디렉터리가 없습니다 (step={step_key}). "
                "TRACE_REPLAY_DIR을 설정하거나 데모 프로젝트를 분석하세요."
            )
        path = self.replay_dir / f"{_safe_key(step_key)}.json"
        if not path.is_file():
            raise LLMError(
                f"replay 픽스처 없음: {path.name} (step={step_key}). "
                "live 모드로 실행하거나 픽스처를 추가하세요."
            )
        return json.loads(path.read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- public
    def structured(self, step_key: str, prompt: str = "") -> Any:
        """구조화 JSON 결과를 반환한다.

        Args:
            step_key: 재생/캐시 식별자 (예: "identify_features", "extract_claims.owner-registration").
            prompt: live 모드에서 사용할 렌더링된 프롬프트. replay 모드에서는 무시.
        """
        if self.settings.backend == "replay":
            _log.info("replay step: %s", step_key)
            return self._structured_replay(step_key)
        _log.info("live LLM step: %s (model=%s)", step_key, self.settings.model)
        return self._structured_live(prompt)


__all__ = ["LLMService", "_extract_json"]
