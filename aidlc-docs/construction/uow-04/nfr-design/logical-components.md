# UOW-04 (Task Impact Analysis) — Logical Components

**단계**: CONSTRUCTION / NFR Design (UOW-04)
**작성일**: 2026-09-09

> Code Generation의 파일 청사진. 모듈 책임·시그니처·의존 방향. UOW-0F/02/03 모듈을 소비.

---

## 모듈 배치
```text
trace/
├── models/
│   └── impact.py          # [신설] ImpactCandidate, TaskImpactResult
├── impact/                # [신설] C6
│   ├── __init__.py
│   ├── context.py         # build_context, KnowledgeContext, rank_by_relevance (P1)
│   └── analyze.py         # analyze_task(LLM step), to_impact_out (P2/P3/P4)
├── engine/
│   └── analyze.py         # [수정] analyze_task_impact 추가 (P5, 코어 공개)
└── prompts/templates/
    └── analyze_task.md    # [신설] (P6)
tests/
├── test_impact_mapping.py         # [신설]
├── test_impact_context.py         # [신설]
├── test_impact_properties.py      # [신설] PBT-04-A~D
├── test_analyze_task_impact.py    # [신설] FakeLLM 파이프라인
└── test_llm_integration.py        # [수정] analyze_task_impact 실 API 케이스
```

## 시그니처

### models/impact.py
```python
class ImpactCandidate(BaseModel):
    path: str
    category: ImpactCategory        # UOW-0F domain (must_change/likely_change/review)
    reason: str
    evidence: list[EvidenceRef] = []
class TaskImpactResult(BaseModel):  # complete_structured 루트
    candidates: list[ImpactCandidate] = []
    change_plan: list[str] = []
```

### impact/context.py
```python
@dataclass
class KnowledgeContext:
    task: str
    features: list[FeatureSummary]
    focus: list[FeatureKnowledge]
    conflicts: list[Conflict]
    known_sources: set[str]

def rank_by_relevance(task: str, summaries: list[FeatureSummary]) -> list[str]   # 순수, id 정렬 tie-break
def build_context(task: str, feature_id: str | None, store: KnowledgeStore, *, top_n: int = 3
                  ) -> tuple[KnowledgeContext, list[Warning]]
```

### impact/analyze.py
```python
def analyze_task(ctx: KnowledgeContext, llm: LLMService) -> TaskImpactResult    # 1회 LLM, 실패 raise
def to_impact_out(result: TaskImpactResult, ctx: KnowledgeContext) -> ImpactOut  # 순수, 강등·정렬
```

### engine/analyze.py (추가)
```python
def analyze_task_impact(task: str, feature_id: str | None = None, *,
                        path: str = ".", llm: LLMService | None = None) -> Result   # P5
```

## 의존성 방향 (순환 없음)
```text
engine/analyze     → impact/{context,analyze}, knowledge/store, conflict/summarize, models/{result,domain}, llm/service
impact/analyze     → models/{impact,result,domain}, conflict/summarize, llm/service, prompts/loader, workflow/catalog(발췌)
impact/context     → knowledge/store, models/{domain,result}   # rank_by_relevance 순수
```
- `to_impact_out`/`rank_by_relevance`는 표준 라이브러리·모델만(순수 → PBT 대상).

## 산출물 변경 (Code Generation 예정)
- `engine/__init__.py`: `analyze_task_impact` export 추가.
- `tests/test_llm_integration.py`: analyze_task_impact 실 API 케이스 추가(기존 `llm_integration` 마커 재사용).
- **신규 런타임 의존성 없음.**
