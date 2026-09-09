# UOW-0F — 논리 컴포넌트 (Logical Components)

**단계**: CONSTRUCTION / NFR Design — UOW-0F (Foundation)
**작성일**: 2026-09-09

> 인프라 컴포넌트(큐·캐시·서킷브레이커)는 없음(in-process). 여기서 "논리 컴포넌트"는 0F가 제공하는
> **순수 코드 모듈과 그 협력·주입 지점**이다. 이 배치가 UOW-01~06이 임포트하는 물리 구조가 된다.

---

## 0F 서브모듈 구성 (`trace/` 하위)

```text
trace/
├── models/           # 도메인 모델 (Pydantic)
│   ├── domain.py     #   Feature, Claim, Evidence, Conflict, FeatureKnowledge, enums
│   ├── result.py     #   Result, Warning, ConflictOut, ImpactOut, EvidenceRef, FeatureSummary
│   └── serialize.py  #   serialize()/deserialize() (P6, PyYAML safe)
├── common/
│   ├── errors.py     #   TraceError 계층 (P3) + error_to_result() 헬퍼
│   ├── warnings.py   #   WarningCollector (P4)
│   └── logging.py    #   log_stage 컨텍스트매니저 + 로거 설정 (P5)
├── config/
│   └── settings.py   #   load_config/get_exclusions/get_llm_settings (P7, late lookup)
├── prompts/
│   └── loader.py     #   get_prompt(name, **vars) (템플릿 내용은 하위 단위)
└── llm/
    ├── client.py     #   LLMClient Protocol + AnthropicClient(스텁) (P1)
    └── service.py    #   LLMService.complete_structured (P1, P2)
```

---

## 컴포넌트 책임·의존 (0F 내부)

| 컴포넌트 | 책임 | 의존(0F 내부) | NFR |
|---|---|---|---|
| `models/domain` | 도메인 엔티티·enum·필드검증(Pydantic) | — | MNT-1 |
| `models/result` | Result/Warning/출력 DTO | domain | REL-2, OBS-2 |
| `models/serialize` | 결정적 직렬화/역직렬화 | domain, PyYAML | DET-1, SEC-4, TST-2 |
| `common/errors` | 예외 계층 + Result 변환 헬퍼 | result | REL-1 |
| `common/warnings` | Warning 누적기 | result | REL-2 |
| `common/logging` | 구조화 로깅·log_stage·마스킹 | — | OBS-1, SEC-3 |
| `config/settings` | Config·LLMSettings 로딩(env 이름만) | errors | SEC-1, DET-2 |
| `prompts/loader` | 템플릿 로드·렌더 | errors | MNT-2 |
| `llm/client` | LLMClient Protocol + Anthropic 구현(스텁) | settings, errors | SEC-1, TST-1 |
| `llm/service` | 구조화 출력·검증·재시도 | client, models, prompts | REL-3, TST-1 |

**내부 의존 방향(순환 없음)**: `logging` (leaf) · `domain`→`result`→{`serialize`,`errors`,`warnings`}; `settings`→`errors`; `llm/service`→{`client`,`models`,`prompts`}.

---

## 주입 지점 (Composition)

- **LLMService 조립**: `LLMService(client=AnthropicClient(settings), settings=settings)`.
  - 프로덕션: `AnthropicClient`(실제 호출은 Code Gen에서 완성).
  - 테스트: `FakeLLMClient`(고정 응답) 주입 → PBT·단위테스트 네트워크 프리.
- **조립 위치**: 어댑터/엔진 부트스트랩(UOW-05/01)에서 1회 구성해 코어 함수에 전달. 0F는 전역 싱글턴을 강제하지 않는다(테스트성).
- **WarningCollector**: 파이프라인 진입점(UOW-01 `analyze_project`)에서 생성 → 하위 단계로 전달 → `build_result`에서 취합.

---

## 하위 단위(01~06)와의 계약 요약

| 하위 단위 | 0F에서 임포트 |
|---|---|
| UOW-01 | Result·WarningCollector·config·errors(PathValidationError)·log_stage |
| UOW-02 | domain·serialize(지식 I/O)·LLMService·prompts.loader |
| UOW-03 | domain(Claim/Evidence/Conflict/Confidence)·LLMService |
| UOW-04 | ImpactOut·LLMService·prompts |
| UOW-05 | Result·models(MCP 입력스키마=Pydantic JSON 스키마)·error_to_result |
| UOW-06 | 전체 + logging·시크릿 위생 점검 |

> 이 논리 컴포넌트 배치는 Code Generation에서 그대로 파일/클래스로 구현된다.
