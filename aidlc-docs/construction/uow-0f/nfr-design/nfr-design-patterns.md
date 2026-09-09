# UOW-0F — NFR 설계 패턴 (NFR Design Patterns)

**단계**: CONSTRUCTION / NFR Design — UOW-0F (Foundation)
**작성일**: 2026-09-09
**결정 반영**: Q1=Protocol+주입, Q2=어댑터 변환, Q3=warning 누적기, Q4=log_stage CM, Q5=단일 serialize, Q6=env 소비직전

> in-process 라이브러리 계층이므로 분산 패턴 대신 **코드 구조 패턴**으로 NFR을 만족시킨다.
> 각 패턴은 대응 NFR과 Code Generation에서 만들 산출물을 명시한다.

---

## P1. LLMService 주입 경계 — Ports & Adapters (NFR-0F-TST-1, REL-3)

```python
class LLMClient(Protocol):
    def complete(self, prompt: str, *, model, temperature, max_tokens, seed) -> str: ...

class LLMService:
    def __init__(self, client: LLMClient, settings: LLMSettings): ...
    def complete_structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        # settings에서 결정성 파라미터, client.complete 호출, Pydantic 검증, 실패 시 제약교정 재시도
```

- **의도**: Claude 호출부(`AnthropicClient`)를 `LLMClient` Protocol 뒤로 숨겨, 테스트에서 `FakeLLMClient` 주입 → 네트워크 없이 검증.
- **결정성**: 파라미터는 `settings`(config)에서만 취득(하드코딩 0).
- **산출물(Code Gen)**: `llm/service.py`(LLMService), `llm/client.py`(Protocol + Anthropic 구현 스텁), `tests`의 FakeLLMClient.

## P2. 재시도 = 제약 교정 (Retry with Correction) (NFR-0F-REL-3)

```
complete_structured:
  for attempt in range(max_retries + 1):
    raw = client.complete(prompt if attempt==0 else prompt + correction_hint)
    try: return Schema.model_validate_json(raw)
    except ValidationError as e: correction_hint = format_schema_errors(e)
  raise LLMValidationError(last_errors)
```
- 지수 백오프 없음(로컬·결정성 우선). `max_retries` 기본 2(settings).

## P3. 오류 → Result 변환은 어댑터 경계에서만 (Boundary Translation) (NFR-0F-REL-1)

- **코어(engine/workflow/…)**: 실패 시 `TraceError` 하위 raise. Result로 감싸지 않음.
- **어댑터(C1 MCP / C9 CLI)**: `try/except TraceError` → 사용자용 `Result`(요약 + warnings). **stack trace·내부 경로 비노출**.
- **의도**: 코어는 순수·테스트 용이, 사용자 표현은 한 곳(어댑터)에 집약. (BR-ERR-002 정합)
- **주의**: 0F는 이 계약(예외 계층·변환 헬퍼 `error_to_result(e) -> Result`)을 제공. 실제 어댑터는 UOW-05/06.

## P4. 부분 실패 강등 = Warning 누적기 (Collector) (NFR-0F-REL-2)

```python
class WarningCollector:
    def add(self, code: str, message: str, source: str | None = None): ...
    def to_list(self) -> list[Warning]: ...
```
- 파이프라인 각 단계에 collector 전달. 비치명 실패는 `collector.add(...)` 후 진행.
- `build_result(..., warnings=collector.to_list())`로 최종 취합. summary에 사람이 읽는 합본 반영(BR-WARN-002).
- 치명(경로 이탈·키 부재)은 collector가 아니라 raise.

## P5. 로깅 횡단 = 컨텍스트 매니저/데코레이터 (NFR-0F-OBS-1)

```python
with log_stage("scan", logger) as st:
    ...
    st.count("assets", n)     # 종료 시 stage·소요시간·카운트를 구조화 1줄 로그
```
- 표준 `logging`, 포맷은 키=값. 레벨은 `TRACE_LOG_LEVEL` env.
- **마스킹**: 값 필드·문서 원문은 로깅 금지(경로·카운트·요약만) — NFR-0F-SEC-3.

## P6. 직렬화 결정성 = 단일 serialize + 정렬 규칙 집약 (NFR-0F-DET-1)

- `serialize(fk)`: 도메인 → dict(Pydantic `model_dump`) → YAML `safe_dump(sort_keys=True)` + 리스트 정렬 키 고정(claims=subject,predicate / evidence=source,location) → Front Matter + 렌더 본문.
- `deserialize(text)`: Front Matter만 `safe_load` → `model_validate`. 본문은 진실원 아님(보존만).
- **계약 고정**: Hypothesis 속성 `deserialize(serialize(x)) == x`, `serialize(x)` 안정성.

## P7. 시크릿 조회 = 소비 직전 env (Late Lookup) (NFR-0F-SEC-1)

- `get_llm_settings()` → `LLMSettings(api_key_env="ANTHROPIC_API_KEY", ...)` (값 아님).
- `AnthropicClient`가 호출 직전 `os.environ[settings.api_key_env]` 조회. 미설정 → `ConfigError`(값 노출 없는 안내).
- 키가 객체·로그·직렬화 산출물에 머무는 구간 최소화.

## P8. 안전 역직렬화 (Safe Deserialization) (NFR-0F-SEC-4)

- YAML은 `yaml.safe_load`만. `yaml.load`(임의 객체) 금지 — 지식 파일이 신뢰 경계 밖일 수 있음.

---

## 패턴 ↔ NFR 매핑

| 패턴 | 충족 NFR |
|---|---|
| P1 주입 경계 | TST-1, DET-2 |
| P2 제약교정 재시도 | REL-3 |
| P3 어댑터 변환 | REL-1, SEC-3(비노출) |
| P4 warning 누적기 | REL-2, OBS-2 |
| P5 로깅 CM | OBS-1, SEC-3 |
| P6 단일 serialize | DET-1, TST-2 |
| P7 late lookup | SEC-1 |
| P8 safe_load | SEC-4 |
