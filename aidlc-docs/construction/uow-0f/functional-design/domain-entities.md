# UOW-0F — 도메인 엔티티 (Domain Entities)

**단계**: CONSTRUCTION / Functional Design — UOW-0F (Foundation)
**작성일**: 2026-09-09
**결정 반영**: Q1=slug ID, Q2=Confidence(enum+reason), Q3=relation enum, Q4=YAML 진실원, Q5=구조화 warnings, Q6=LLMService 계약, Q7=결정성 중앙관리, Q8=TraceError 계층

> 이 문서는 이후 모든 단위(01~06)가 임포트하는 **동결된 도메인 계약**이다. 타입은 개념 수준
> (Python 힌트 형태). 실제 클래스/직렬화 구현은 Code Generation에서 이 계약을 그대로 따른다.
> 기술중립 원칙: 여기엔 인프라·프레임워크 관심사를 두지 않는다.

---

## Enum

```python
class Confidence(str, Enum):     # 근거 일치도 기반 (FR-CONFIDENCE-001)
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class EvidenceRelation(str, Enum):   # Q3=A: 3값 고정
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MENTIONS = "mentions"

class EvidenceType(str, Enum):   # 근거 출처 자산 종류 (스캐너 분류와 정합)
    SOURCE = "source"            # 소스코드
    OPENAPI = "openapi"
    SQL = "sql"
    CONFIG = "config"
    TEST = "test"
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"

class ConflictType(str, Enum):   # P0=value_mismatch (FR-CONFLICT-001)
    VALUE_MISMATCH = "value_mismatch"
    # (P1 확장 여지) MISSING_IMPL, CONTRADICTORY_STATEMENT ...

class ImpactCategory(str, Enum): # Task Impact 3분류 (FR-IMPACT)
    MUST_CHANGE = "must_change"
    LIKELY_CHANGE = "likely_change"
    REVIEW = "review"
```

---

## 코어 도메인 엔티티

### Feature
검출된 "기능/능력" 단위. 자동 검출(Q4=완전자동).

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | str (slug) | ✔ | 안정적 식별자. **Q1=A slug**. 파일명·리소스 URI에 사용. 생성 규칙은 business-rules.md §ID |
| `title` | str | ✔ | 사람이 읽는 제목 |
| `description` | str | ✔ | 1~3문장 요약 |
| `related_sources` | list[str] | ✔(비어도 됨) | 이 Feature와 연관된 자산 경로 |

### Claim
Feature에 대한 **원자적** 주장(FR-CLAIM-001). subject-predicate-value 삼항.

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `subject` | str | ✔ | 주어 (예: `"owner.telephone"`) |
| `predicate` | str | ✔ | 술어 (예: `"max_length"`) |
| `value` | str | ✔ | 값 (예: `"20"`). 비교 위해 문자열 정규화(business-rules §정규화) |
| `feature_id` | str | ✔ | 소속 Feature |

> 원자성 규칙: 하나의 Claim은 하나의 (subject, predicate, value)만 담는다. 복합 진술은 분해.

### Evidence
Claim을 뒷받침/반박하는 **근거 조각**(FR-EVIDENCE-001).

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `source` | str | ✔ | 근거 자산 경로 |
| `type` | EvidenceType | ✔ | 자산 종류 |
| `location` | str | ✔ | 위치(줄번호·섹션·경로 등, 사람이 확인 가능) |
| `extracted_value` | str \| None | — | 근거에서 추출한 값(비교 대상) |
| `relation` | EvidenceRelation | ✔ | Claim과의 관계 (supports/contradicts/mentions) |

### Confidence 판정 결과 (ConfidenceAssessment)
**Q2=B**: enum + 사유. 신뢰도는 값 자체가 아니라 Claim에 부여되는 판정.

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `level` | Confidence | ✔ | HIGH/MEDIUM/LOW |
| `reason` | str | ✔ | 왜 그 등급인지(근거 일치/상충/희소 등) — 에이전트 설명용 |

### Conflict
같은 Claim에 대해 값이 어긋나는 상황(FR-CONFLICT-001). P0=value_mismatch.

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `type` | ConflictType | ✔ | value_mismatch(P0) |
| `claim` | str | ✔ | 충돌 대상 주장 식별(예: `"owner.telephone.max_length"`) |
| `values` | list[ConflictValue] | ✔ | 상충하는 값들 (아래) |
| `interpretation` | str | ✔ | 사람이 읽는 해석/영향 설명 |

#### ConflictValue
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `value` | str | ✔ | 값 (예: `"20"`, `"10"`) |
| `source` | str | ✔ | 출처 자산 경로 |
| `location` | str | ✔ | 위치 |

### FeatureKnowledge (집계 루트)
한 Feature의 지식 전체. `.trace/knowledge/features/<id>.md`로 영속화되는 단위(Q4=A YAML 진실원).

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `feature` | Feature | ✔ | 헤더 |
| `claims` | list[Claim] | ✔ | 원자적 주장들 |
| `evidence` | list[Evidence] | ✔ | 근거들(claim과 연결은 subject/predicate 매칭) |
| `confidence` | list[ClaimConfidence] | ✔ | Claim별 신뢰도 판정 (claim_key → ConfidenceAssessment) |
| `conflicts` | list[Conflict] | ✔(비어도 됨) | 검출된 충돌 |
| `body_markdown` | str | ✔ | 사람이 읽는 지식 본문(파생 렌더) |
| `meta` | dict | ✔ | 생성시각·소스카운트·모델·프롬프트버전 등 |

> `ClaimConfidence = {claim_key: str, assessment: ConfidenceAssessment}` (claim_key = `subject.predicate`)

---

## 출력 DTO (Result envelope 구성요소)

모든 코어 함수는 공통 `Result`를 반환한다(component-methods 계약 동결).

### Result
| 필드 | 타입 | 설명 |
|---|---|---|
| `summary` | str | 사람이 읽는 요약(에이전트가 그대로 설명) — **핵심 우선**(NFR-MCP-UX-002) |
| `data` | dict | 구조화 페이로드(함수별 상이) |
| `conflicts` | list[ConflictOut] | 있으면 상위 노출 |
| `impact` | ImpactOut \| None | Task Impact 결과 |
| `evidence` | list[EvidenceRef] | 근거 참조 |
| `warnings` | list[Warning] | **Q5=B 구조화** 부분실패/저신뢰 |
| `meta` | dict | confidence·counts·timings 등 저수준 |

### Warning (Q5=B — Resiliency Baseline)
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `code` | str | ✔ | 기계 필터용 코드(예: `PARSE_PARTIAL`, `LLM_LOW_CONFIDENCE`, `PATH_SKIPPED`) |
| `message` | str | ✔ | 사람이 읽는 설명 |
| `source` | str \| None | — | 관련 자산/단계 |

> Result 조립 시 `summary`에는 warnings의 사람이 읽는 합본도 함께 반영(business-logic-model §Result 조립).

### ConflictOut / EvidenceRef / ImpactOut / FeatureSummary
| DTO | 필드 | 설명 |
|---|---|---|
| `ConflictOut` | `claim, values:[{value,source,location}], interpretation, type` | get_conflicts 출력 |
| `EvidenceRef` | `source, location, relation` | 결과에 첨부하는 근거 포인터 |
| `ImpactOut` | `must_change:[ImpactItem], likely_change:[…], review:[…], related_conflicts:[ConflictOut](P1), change_plan:[str]` | Task Impact |
| `ImpactItem` | `path, reason, evidence:[EvidenceRef]` | 영향 항목 |
| `FeatureSummary` | `id, title, confidence, conflicts_count, related_sources` | list_features 출력 |

---

## 설정·서비스 계약 엔티티 (C7/C8/S4)

### Config (C7)
| 필드 | 타입 | 설명 |
|---|---|---|
| `exclusions` | list[str] | 스캔 제외 glob (기본값 + 사용자 확장) |
| `llm` | LLMSettings | 아래 |
| `knowledge_dir` | str | 기본 `.trace/knowledge` |
| `raw` | dict | 원본 설정(확장 대비) |

### LLMSettings (Q7=A 결정성 중앙관리)
| 필드 | 타입 | 설명 |
|---|---|---|
| `model` | str | 예: `claude-sonnet-5` |
| `api_key_env` | str | 키를 읽을 **환경변수 이름**(값 아님, NFR-SEC-001) |
| `temperature` | float | 결정성: 기본 `0` |
| `max_tokens` | int | 응답 상한 |
| `max_retries` | int | 구조화 검증 실패 시 제약교정 재시도 횟수 |
| `seed` | int \| None | 지원 시 재현성 |

### LLMService 계약 (S4 스켈레톤, Q6=A)
```python
def complete_structured(prompt: str, schema: dict, *, settings: LLMSettings) -> dict:
    """Claude 호출 → JSON 구조화 출력 → schema 검증.
       검증 실패 시 제약교정 프롬프트로 max_retries까지 재시도.
       최종 실패: raise LLMValidationError (호출 단위가 warning으로 강등 결정).
       결정성 파라미터는 settings에서만 취득(Q7). 실제 Claude 클라이언트 호출부는 Code Generation."""
```
> 0F에서는 **시그니처·예외·정책**을 동결. 실제 네트워크 호출은 스텁(NotImplemented 또는 주입형)로 두고 UOW-02/03/04 통합 시점/Code Generation에서 채운다.

### 프롬프트 로더 계약 (C8)
```python
def get_prompt(name: str, **vars) -> str:
    """prompts/<name>.md(.j2) 템플릿 로드 후 vars 렌더. 미존재 → ConfigError.
       템플릿 내용(프롬프트 본문)은 각 AI 단위(02/03/04)가 채운다 — 로더 계약만 0F 소관."""
```

---

## 오류 타입 계층 (Q8=A)

```
TraceError (base)
├── ConfigError            # 설정/템플릿 로드 실패
├── PathValidationError    # NFR-SEC-004: 스캔 경로 이탈/접근불가
├── ParseError             # 자산 파싱 실패(부분 실패 허용 → warning 강등 가능)
├── LLMValidationError     # 구조화 출력 재시도 소진
└── StorageError           # .trace 저장소 I/O 실패
```
- 어댑터(C1 MCP / C9 CLI)는 이 예외를 잡아 `Result.warnings` 또는 오류 요약으로 변환(사용자에게 stack trace 노출 금지).

---

## 엔티티 관계 (텍스트 다이어그램)

```
FeatureKnowledge (집계 루트)
  └─ feature: Feature
  └─ claims: [Claim]            (Feature 1 ── * Claim)
  └─ evidence: [Evidence]       (Claim 1 ── * Evidence, subject.predicate로 연결)
  └─ confidence: [ClaimConfidence → ConfidenceAssessment]
  └─ conflicts: [Conflict → [ConflictValue]]   (같은 claim_key의 상충 값 집합)

Result (모든 코어 함수 반환)
  └─ data / conflicts:[ConflictOut] / impact:ImpactOut / evidence:[EvidenceRef] / warnings:[Warning] / meta
```

## 스토리/요구사항 추적
- 뒷받침: US-02.3·US-03.1·US-03.2(모델·직렬화), US-06.4(시크릿=api_key_env), NFR-CORE-001/002, NFR-MAINT-002, NFR-LOG-001, NFR-SEC-001/004.
