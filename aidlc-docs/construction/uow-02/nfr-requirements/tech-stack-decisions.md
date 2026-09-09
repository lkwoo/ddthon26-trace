# UOW-02 (Feature & Knowledge) — Tech Stack Decisions

**단계**: CONSTRUCTION / NFR Requirements (UOW-02)
**작성일**: 2026-09-09

## 상속/재사용 (변경 없음)
| 항목 | 결정 | 근거 |
|---|---|---|
| LLM 클라이언트/서비스 | UOW-0F `LLMService.complete_structured` + `LLMClient`(anthropic) | UOW-0F |
| 프롬프트 | UOW-0F `get_prompt` + `prompts/templates/*.md` | C8, NFR-MAINT-002 |
| 직렬화 | UOW-0F `serialize/deserialize`(MD+YAML) | US-02.3 |
| 도메인 모델 | UOW-0F Feature/FeatureKnowledge 등 | 재사용 |
| 해시 | 표준 `hashlib.sha256` | 결정적, 무의존 |
| 캐시 직렬화 | 표준 `json` (CacheEntry.model_dump) | 무의존·가독 |

## UOW-02 고유 결정
| 항목 | 값 |
|---|---|
| 자산 발췌 상한 | 4,000자/자산 (Q1=B) |
| max_features | 무제한(None) (Q1=B) |
| .trace 루트 | 분석 대상 프로젝트 루트 하위 (Q5=A) |
| 캐시 경로 | `<root>/.trace/cache/<assets_hash>.json` |
| 지식 경로 | `<root>/.trace/knowledge/features/<id>.md` |

## 테스트 스택 (Q3=B)
- 기본: `hypothesis`(PBT) + FakeLLMClient(UOW-0F conftest) — 오프라인·결정적.
- 옵트인 통합: `pytest` 마커 `llm_integration` 등록(pyproject `[tool.pytest.ini_options] markers`),
  `TRACE_RUN_LLM_INTEGRATION=1` + 유효 API 키일 때만 실행(그 외 skip). 실제 anthropic 호출.

## 의존성 변경
- 신규 런타임 의존성 **없음**(anthropic/pydantic/PyYAML 기존). 표준 라이브러리(hashlib/json)만 추가 사용.
- pyproject: pytest markers에 `llm_integration` 추가(경고 억제·문서화).
