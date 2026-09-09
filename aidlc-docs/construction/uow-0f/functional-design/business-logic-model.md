# UOW-0F — 비즈니스 로직 모델 (Business Logic Model)

**단계**: CONSTRUCTION / Functional Design — UOW-0F (Foundation)
**작성일**: 2026-09-09

> 기술중립적으로 Foundation이 제공하는 **흐름/알고리즘 계약**을 서술한다. 구현 언어 세부·프레임워크는 배제.
> 이 흐름들은 UOW-01~06이 그대로 호출·의존한다.

---

## 1. Result 조립 흐름

모든 코어 함수는 도메인 처리 결과를 공통 `Result`로 감싸 반환한다.

```
build_result(summary_text, data, *, conflicts=[], impact=None,
             evidence=[], warnings=[], meta={}) -> Result
```

조립 규칙:
1. `data`는 함수별 구조화 페이로드 그대로.
2. `conflicts`가 비어있지 않으면 **핵심 우선**: summary 앞부분에 충돌 요약 한 줄을 삽입(NFR-MCP-UX-002).
3. `warnings`(구조화 Warning 리스트, Q5=B)가 있으면 summary 말미에 "⚠ N건의 경고" + 사람이 읽는 합본을 덧붙인다. 원본 구조화 warnings는 필드에 그대로 유지(기계 필터 가능).
4. `meta`에는 counts(features/claims/conflicts), timings, model/prompt 버전을 기본 채움.
5. Result는 불변(생성 후 변경 금지) — 어댑터는 읽기만.

---

## 2. 직렬화 / 역직렬화 흐름 (MD+YAML, Q4=A)

`.trace/knowledge/features/<id>.md` 파일 구조:

```
---
# YAML Front Matter = 구조적 진실원
id: owner-registration
title: Owner Registration
claims: [...]
evidence: [...]
confidence: [...]
conflicts: [...]
meta: {...}
---

# Owner Registration        ← 이하 Markdown 본문(사람용 렌더, 파생)
...
```

- **직렬화** `serialize(fk: FeatureKnowledge) -> str`:
  1. 도메인 객체 → YAML Front Matter(구조).
  2. 같은 데이터로 사람이 읽는 Markdown 본문 렌더(`body_markdown`) — 제목·주장표·충돌 강조.
  3. `--- YAML --- \n\n body` 결합.
- **역직렬화** `deserialize(text: str) -> FeatureKnowledge`:
  1. **YAML Front Matter만 파싱**(Q4=A: 본문은 진실원 아님, 재파싱 안 함).
  2. 필드 검증(business-rules §검증). 누락/형식오류 → `StorageError`.
  3. `body_markdown`은 원문 본문 그대로 보존(재저장 시 재렌더).
- 결정성: 필드 순서·리스트 정렬을 고정(같은 입력 → 같은 파일). 재현성(Hero 데모) 보장.

---

## 3. Config 로딩 흐름 (C7)

```
load_config(path=None) -> Config
```
순서(뒤가 앞을 덮어씀):
1. 내장 기본값(기본 exclusions, knowledge_dir=`.trace/knowledge`, temperature=0, max_retries).
2. 프로젝트 설정 파일(존재 시) — path 미지정이면 대상 프로젝트 루트에서 관례 경로 탐색.
3. 환경변수 오버라이드(모델/키 env 이름 등).

- `get_exclusions() -> list[str]`: 기본 + 사용자 확장 병합(중복 제거).
- `get_llm_settings() -> LLMSettings`: 모델·`api_key_env`·결정성 파라미터 반환. **키 값 자체는 담지 않음** — 소비 시점에 `os.environ[api_key_env]` 조회(NFR-SEC-001).
- 결정성 파라미터는 여기(config)에서만 관리(Q7=A). 호출부·서비스는 소비만.

---

## 4. LLMService 호출 계약 흐름 (S4 스켈레톤, Q6=A)

```
complete_structured(prompt, schema, *, settings) -> validated_dict
```
흐름:
1. `settings`에서 결정성 파라미터 취득(temperature=0 등).
2. Claude 호출(실제 클라이언트 구현은 Code Generation; 0F는 주입 가능한 스텁 경계).
3. 응답 → JSON 파싱 → `schema` 검증.
4. 실패 시: **제약 교정** 재프롬프트("아래 스키마를 엄격히 따르라" + 오류 요약) → `settings.max_retries`까지 반복.
5. 최종 실패 → `raise LLMValidationError`. (호출한 AI 단위가 warning 강등 여부 결정 — FR-ANALYSIS-003/§17.4)
6. API 키는 `settings.api_key_env`가 가리키는 환경변수에서만 취득. 키 미설정 → `ConfigError`.

> 결정성 고정(temperature=0/seed)으로 Hero 시나리오 재현성 확보(NFR-AI-004 뒷받침).

---

## 5. 프롬프트 로더 흐름 (C8)

```
get_prompt(name, **vars) -> str
```
1. `prompts/<name>` 템플릿 파일 로드. 미존재 → `ConfigError`.
2. `vars`로 렌더(단순 치환/템플릿 엔진). 미해결 변수 → `ConfigError`(엄격).
3. 렌더 결과 문자열 반환.

> 템플릿 **내용**은 0F 소관 아님(각 AI 단위가 채움). 0F는 로더 계약·디렉터리 규약만 동결.

---

## 6. 로깅 흐름 (NFR-LOG-001)

- 공통 로거: 단계 시작/종료, 자산 카운트, 부분 실패, LLM 재시도 횟수, 소요시간을 구조화 로그로.
- **시크릿·전체 문서 원문은 로그에 남기지 않음**(경로·카운트·요약만). NFR-SEC-001/005.
- 레벨: INFO(진행), WARNING(부분실패/저신뢰=Warning과 정합), ERROR(TraceError).

---

## 데이터 흐름 요약 (Foundation이 잇는 이음새)

```
config.load_config ─┐
                    ├─→ (LLMSettings) ─→ LLMService.complete_structured ─→ AI 단위(02/03/04)
prompts.get_prompt ─┘                                   │
                                                        └─(validated dict)→ 도메인 모델(0F) 구성
도메인 모델 ─→ serialize/deserialize ─→ .trace 저장소(UOW-02가 사용)
모든 코어함수 ─→ build_result ─→ Result ─→ 어댑터(C1/C9, UOW-05/06)
```

## 추적
- FR-ANALYSIS-003(부분실패), NFR-CORE-001/002(결정성·구조화), NFR-LOG-001, NFR-SEC-001/004/005, NFR-MCP-UX-002(핵심 우선).
