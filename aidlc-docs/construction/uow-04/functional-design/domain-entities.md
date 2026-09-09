# UOW-04 (Task Impact Analysis) — 도메인 엔티티 (domain-entities)

**단계**: CONSTRUCTION / Functional Design (UOW-04)
**작성일**: 2026-09-09
**결정 반영**: Q1=A(저장 지식 한정)·Q2=A(전체 요약+관련 상세)·Q3=A(기존 conflicts 노출)·Q4=A(LLM 순서 Change Plan)·Q5=A(1회 호출·강등)

> UOW-0F의 출력 DTO(`ImpactOut/ImpactItem/EvidenceRef`, `ConflictOut`)를 **재사용**한다.
> UOW-04은 (1) LLM 중간 스키마 신설, (2) 지식 컨텍스트 조립 뷰만 추가한다. 신규 코어 모델 없음.

---

## 1. LLM 추출 중간 스키마 — `trace/models/impact.py` 신설
`analyze_task` step 1회 구조화 호출로 영향 후보와 Change Plan을 함께 산출.
```text
class ImpactCandidate(BaseModel):
    path: str                      # 영향 파일/컴포넌트 (저장 지식의 소스 rel_path)
    category: ImpactCategory       # must_change | likely_change | review (domain, UOW-0F)
    reason: str                    # 왜 영향을 받는가 (한 줄)
    evidence: list[EvidenceRef] = []   # 근거 참조(source·location·relation) — UOW-0F 재사용

class TaskImpactResult(BaseModel):     # complete_structured 루트
    candidates: list[ImpactCandidate] = []
    change_plan: list[str] = []        # 순서형 단계(자문용)
```
- `ImpactCategory`(UOW-0F domain): `MUST_CHANGE / LIKELY_CHANGE / REVIEW`.
- `EvidenceRef`(UOW-0F result): `source · location · relation`.

## 2. 지식 컨텍스트 뷰 — `trace/impact/context.py` 내부(비영속)
```text
@dataclass
class KnowledgeContext:
    task: str
    features: list[FeatureSummary]        # 전체 요약(광범위, Q2=A)
    focus: list[FeatureKnowledge]         # 상세 포함 대상(feature_id 또는 관련도 상위)
    conflicts: list[Conflict]             # focus Feature들의 기존 충돌(Q3=A)
    known_sources: set[str]               # focus의 related_sources·evidence 소스 합집합(Q1=A 화이트리스트)
```
- 컨텍스트는 프롬프트 렌더 입력이자, 후처리 검증(허구 path 드롭)의 기준이 된다.

## 3. 파생 규칙 (중간 → 최종 ImpactOut)
| 중간(TaskImpactResult) | 최종(ImpactOut) |
|---|---|
| candidates[category=MUST_CHANGE] | must_change: list[ImpactItem{path,reason,evidence}] |
| candidates[category=LIKELY_CHANGE] | likely_change: [...] |
| candidates[category=REVIEW] | review: [...] |
| (컨텍스트) focus.conflicts | related_conflicts: summarize_conflicts(...) (Q3=A, P1) |
| change_plan | change_plan: list[str] (그대로) |
- 각 카테고리 항목은 `path` 순 안정 정렬(결정성). 허구 path(known_sources 밖)는 review로 강등 또는 드롭+warning(BR-IMP-004).

## 4. 코어 함수 계약
```text
# impact (C6) / workflow (C3)
def analyze_task(ctx: KnowledgeContext, llm) -> TaskImpactResult      # 1회 LLM(FR-IMPACT-002)
def build_context(task, feature_id, store) -> KnowledgeContext        # 지식 조립(Q1/Q2/Q3=A)
def to_impact_out(result, ctx) -> ImpactOut                           # 매핑·정렬·근거부족 강등
# engine (C2) — 코어 공개
def analyze_task_impact(task: str, feature_id: str | None = None, *, path=".") -> Result
```

## 5. analyze_task_impact 데이터 계약
```text
analyze_task_impact(task, fid?).impact = ImpactOut{
    must_change:[{path,reason,evidence:[{source,location,relation}]}], likely_change:[...], review:[...],
    related_conflicts:[ConflictOut...], change_plan:["1. ...","2. ..."] }
  + Result.conflicts = related_conflicts (핵심 우선 노출, build_result)
  + meta = {feature_scope, candidates_count, conflicts_count}
```
- **소스 자동수정 없음**(FR-IMPACT-006/US-04.4-AC2): 출력은 자문 데이터뿐, 파일 쓰기 없음.
