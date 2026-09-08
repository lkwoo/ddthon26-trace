# TRACE — 컴포넌트 메서드/시그니처 (Component Methods)

**단계**: INCEPTION / Application Design
**작성일**: 2026-09-08

> 고수준 시그니처와 입출력만 정의한다. 상세 비즈니스 규칙·필드 검증·프롬프트 내용은 Construction/Functional Design(유닛별)에서 확정. 타입은 개념 수준(Python 힌트 형태로 표기).

---

## 공통 result envelope (Q4=A)
모든 코어 함수는 사람이 읽는 요약과 구조화 데이터를 함께 담는 공통 봉투를 반환한다. 핵심 우선 순서(NFR-MCP-UX-002).

```python
class Result:
    summary: str                 # 사람이 읽는 요약 (에이전트가 그대로 설명 가능)
    data: dict                   # 구조화 페이로드 (아래 각 함수별)
    conflicts: list[ConflictOut] # 있을 때 상위 노출
    impact: ImpactOut | None
    evidence: list[EvidenceRef]
    warnings: list[str]          # 부분 실패/저신뢰 경고 (FR-ANALYSIS-003)
    meta: dict                   # confidence, counts, timings 등 저수준
```

---

## C2 로컬 지식 엔진 — 코어 함수 (= MCP 도구 구현 대상, §13.2)

```python
def scan_project(path: str) -> Result:
    """대상 디렉터리 스캔·분류. data: {project_name, assets:[{path,type,filename,parse_status}]}.
       무효/접근불가 경로는 warnings + 오류 요약 (NFR-SEC-004)."""

def analyze_project(path: str) -> Result:
    """전체 파이프라인 실행(스캔→파싱→Feature→Claim/Evidence→Conflict→지식→영속화).
       data: {features:[summary], conflicts_count, assets_count}. 캐시 존재 시 재사용(NFR-PERF-003).
       부분 실패는 warnings로, 전체 중단 없음(FR-ANALYSIS-003)."""

def list_features() -> Result:
    """검출된 Feature 요약 목록. data: {features:[{id,title,confidence,conflicts,related_sources}]}."""

def get_feature_knowledge(feature_id: str) -> Result:
    """단일 Feature 지식. data: YAML 구조화 필드; summary: Markdown 본문 발췌.
       리소스 경로(.trace/knowledge/features/<id>.md) 포함."""

def get_conflicts(feature_id: str | None = None) -> Result:
    """충돌 목록/상세. conflicts:[{claim, values:[{value,source,location}], interpretation}].
       meta: {conflicts_count}."""

def analyze_task_impact(task: str, feature_id: str | None = None) -> Result:
    """자연어 작업 영향 분석. impact: {must_change:[{path,reason,evidence}],
       likely_change:[...], review:[...]}, related_conflicts(P1), change_plan:[step...]."""
```

## C3 AI 워크플로우 — 내부 step (구조화 출력 검증)

```python
def identify_features(assets: list[Asset]) -> list[FeatureCandidate]      # FR-KNOWLEDGE-001 (자동)
def extract_claims(feature: FeatureCandidate, assets) -> list[Claim]      # FR-CLAIM-001 (원자적)
def group_evidence(claims, assets) -> list[EvidenceLink]                  # FR-EVIDENCE-001
def assign_confidence(claim, evidence) -> Confidence                      # FR-CONFIDENCE-001 (근거 일치도)
def generate_feature_knowledge(feature, claims, evidence, conflicts) -> FeatureKnowledge
def analyze_task(task, context: KnowledgeContext) -> ImpactOut            # FR-IMPACT-002 (지식 기반)
```
- 각 step: `prompts.get_prompt(...)` 사용, JSON 스키마 검증 실패 시 제약 교정 재시도 → 실패 시 단계 warning(§17.4).

## C4 지식 모델 & 저장소

```python
def save_feature(fk: FeatureKnowledge) -> str            # .trace/knowledge/features/<id>.md (MD+YAML)
def load_feature(feature_id: str) -> FeatureKnowledge
def list_feature_summaries() -> list[FeatureSummary]
def read_resource(uri: str) -> str                       # MCP 리소스 콘텐츠 (Markdown 본문)
# 도메인 모델(개념): Feature, Claim(subject,predicate,value), Evidence(source,type,location,extracted_value,relation),
#                    Confidence(HIGH/MEDIUM/LOW), Conflict(type,claim,values,interpretation)
```

## C5 충돌 검출

```python
def detect_conflicts(feature: FeatureKnowledge) -> list[Conflict]   # value_mismatch(P0) 우선
def summarize_conflicts(feature_id: str | None) -> list[ConflictOut]
```

## C6 Task Impact

```python
def analyze_task_impact(task: str, feature_id: str | None) -> ImpactOut
# classify → {must_change, likely_change, review} + reasons + evidence refs
# + related existing conflicts (P1) + ordered change_plan
```

## C7 설정 / C8 프롬프트 / C9 CLI

```python
# config
def load_config(path: str | None) -> Config
def get_exclusions() -> list[str]
def get_llm_settings() -> LLMSettings          # 모델·키(env), 결정성 파라미터

# prompts
def get_prompt(name: str, **vars) -> str        # 파일 템플릿 로드+렌더

# cli (얇은 어댑터)
def main(argv) -> int                           # engine 코어 함수 호출·출력
```
