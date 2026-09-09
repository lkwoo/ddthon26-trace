# UOW-0F — 코드 생성 요약 (Code Summary)

**단계**: CONSTRUCTION / Code Generation — UOW-0F (Foundation)
**작성일**: 2026-09-09
**검증**: `pytest` **31 passed** (로컬 .venv, Python 3.11.9)

> 실제 코드는 워크스페이스 루트(`trace/`·`tests/`). 이 문서는 요약(마크다운)만.

---

## 생성된 애플리케이션 코드 (`trace/`)

| 파일 | 공개 계약 | 설계 근거 |
|---|---|---|
| `models/domain.py` | enums, `Feature/Claim/Evidence/ConfidenceAssessment/ClaimConfidence/Conflict/ConflictValue/FeatureKnowledge`, `make_feature_id`/`make_unique_feature_id`/`normalize_value`/`claim_key` | domain-entities.md, BR-ID/NORM/VAL/CONFLICT |
| `models/result.py` | `Result, Warning, ConflictOut, EvidenceRef, ImpactItem, ImpactOut, FeatureSummary, build_result` | Result envelope, business-logic-model §1 |
| `models/serialize.py` | `serialize/deserialize/render_body` (MD+YAML, safe_load, 결정적) | P6/P8, NFR-0F-DET-1/SEC-4 |
| `common/errors.py` | `TraceError` 계층 + `error_to_result` | P3, BR-ERR-* |
| `common/warnings.py` | `WarningCollector` + 코드 상수 | P4, BR-WARN-* |
| `common/logging.py` | `get_logger`, `log_stage` CM | P5, NFR-0F-OBS-1/SEC-3 |
| `config/settings.py` | `Config, LLMSettings(resolve_api_key), load_config, get_exclusions, get_llm_settings` | P7, BR-SEC/DET |
| `prompts/loader.py` | `get_prompt(name, /, **vars)`, `list_prompts` | C8, MNT-2 |
| `llm/client.py` | `LLMClient` Protocol, `AnthropicClient`(지연 임포트·late lookup) | P1/P7 |
| `llm/service.py` | `LLMService.complete_structured` (검증·제약교정 재시도) | P1/P2, REL-3 |

빌드/설정: `pyproject.toml`(의존성·진입점·mypy·pytest), `.gitignore`, `.env.example`, `README.md`(시작용).

## 생성된 테스트 (`tests/`)

| 파일 | 커버 | NFR |
|---|---|---|
| `conftest.py` | `FakeLLMClient`(주입), 샘플 FeatureKnowledge | TST-1 |
| `test_models_serialize.py` | round-trip·결정성·**PBT 멱등**(Hypothesis) | DET-1, TST-2 |
| `test_domain_rules.py` | slug 멱등·charset·정규화·경로안전·충돌 성립 | TST-2, SEC |
| `test_result_warnings.py` | build_result 충돌 우선·warning 합본·Collector 사본 | REL-2 |
| `test_config_settings.py` | 키 값 미저장·미설정 ConfigError·제외 dedup | SEC-1, DET-2 |
| `test_prompts_loader.py` | 렌더·미존재/미해결/경로안전 ConfigError | MNT-2 |
| `test_llm_service.py` | 1차 성공·교정 후 성공·재시도 소진·코드펜스 제거 | REL-3, TST-1 |

## 생성 중 발견·수정한 버그 (테스트가 포착)
1. `get_prompt` 위치인자 `name`이 템플릿 변수 `name`과 충돌 → **위치 전용 인자(`/`)**로 수정.
2. 직렬화 본문 trailing newline 불일치로 round-trip 멱등 깨짐 → 본문 **strip 후 단일 개행 정규화**로 수정.

## 하위 단위(01~06) 임포트 가이드
- 도메인/Result: `from trace.models.domain import ...`, `from trace.models.result import Result, build_result`
- 지식 I/O(UOW-02): `from trace.models.serialize import serialize, deserialize`
- 오류/경고/로그: `from trace.common.errors import ...`, `from trace.common.warnings import WarningCollector`, `from trace.common.logging import log_stage`
- 설정/LLM: `from trace.config.settings import load_config, get_llm_settings`, `from trace.llm.service import LLMService`, `from trace.llm.client import AnthropicClient, LLMClient`
- 프롬프트(내용은 각 단위가 templates/ 에 추가): `from trace.prompts.loader import get_prompt`

## 남은 작업 (다음 단위로)
- 실제 Claude 호출 경로의 통합 검증은 UOW-02~04에서 프롬프트 채운 뒤. 락파일 생성·통합 테스트는 Build & Test.
