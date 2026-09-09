# UOW-03 (Claims/Evidence/Conflict) — Logical Components

**단계**: CONSTRUCTION / NFR Design (UOW-03)
**작성일**: 2026-09-09

> Code Generation의 파일 청사진. 모듈 책임·시그니처·의존 방향. UOW-0F/01/02 모듈을 소비·보강.

---

## 모듈 배치
```text
trace/
├── models/
│   ├── domain.py          # [수정] ConflictType += STALE_KNOWLEDGE, POLICY_CONFLICT
│   └── extraction.py      # [신설] ExtractedClaim, ClaimExtractionResult
├── workflow/
│   └── claims.py          # [신설] extract_claims, assign_confidence, enrich_feature_knowledge (P1/P2/P3/P5)
├── conflict/              # [신설] C5
│   ├── __init__.py
│   ├── detect.py          # detect_conflicts, classify_conflict_type, ABSENCE_TOKENS (P3/P4)
│   └── summarize.py       # summarize_conflicts → ConflictOut (P6)
├── engine/
│   └── analyze.py         # [신설] analyze_project, get_conflicts (코어 공개, P5/P6)
└── prompts/templates/
    └── extract_claims.md  # [신설] (P7)
tests/
├── test_conflict_detect.py        # [신설] demo 3충돌 유형 검증
├── test_confidence.py             # [신설] Confidence 경계 규칙
├── test_conflict_properties.py    # [신설] PBT-03-A~D
├── test_analyze_project.py        # [신설] FakeLLM 파이프라인·캐시-완본 스테이지
└── test_llm_integration.py        # [수정] analyze_project 실 API 통합 케이스 추가(옵트인)
```

## 시그니처

### models/extraction.py
```python
class ExtractedClaim(BaseModel):
    subject: str
    predicate: str
    evidence: list[Evidence] = []       # UOW-0F Evidence 재사용
class ClaimExtractionResult(BaseModel):  # complete_structured 루트
    claims: list[ExtractedClaim] = []
```

### workflow/claims.py
```python
def extract_claims(feature: Feature, assets: list[Asset], llm: LLMService
                   ) -> tuple[list[ExtractedClaim], list[Warning]]        # P1/P2, Feature당 1회
def assign_confidence(ec: ExtractedClaim) -> ClaimConfidence               # P3, 비-LLM 순수함수
def enrich_feature_knowledge(fk_shell: FeatureKnowledge, assets, llm: LLMService
                             ) -> tuple[FeatureKnowledge, list[Warning]]   # P5, meta.stage="complete"
```

### conflict/detect.py
```python
ABSENCE_TOKENS: frozenset[str]        # {absent,none,missing,n/a,null,없음,부재}
def detect_conflicts(claims: list[ExtractedClaim], feature_id: str) -> list[Conflict]   # P3, 결정적 순수함수
def classify_conflict_type(ec: ExtractedClaim, vals: list[tuple[str,str,str]]) -> ConflictType  # P4, 전결정성
```

### conflict/summarize.py
```python
def summarize_conflicts(conflicts: list[Conflict]) -> list[ConflictOut]    # P6
```

### engine/analyze.py
```python
def analyze_project(path: str) -> Result       # P5, 전체 파이프라인(Q5=A), Warning 강등
def get_conflicts(feature_id: str | None = None) -> Result   # P6, meta.conflicts_count
```

## 의존성 방향 (순환 없음)
```text
engine/analyze   → workflow/{claims,features}, conflict/{detect,summarize}, knowledge/{store,cache},
                   engine/scanner(UOW-01), models/{result,domain}, llm/service, common/errors
workflow/claims  → workflow/catalog(UOW-02), conflict/detect, models/{domain,extraction,serialize}, llm/service, prompts/loader
conflict/detect  → models/{domain,extraction}, models(normalize_value/claim_key)  # 순수, 서드파티 없음
conflict/summarize → models/{domain,result}
```
- 신규 순환 없음. `conflict/detect`는 표준 라이브러리·모델만 의존(순수 함수 → PBT 대상).

## 산출물 변경 (Code Generation 예정)
- `trace/models/domain.py`: `ConflictType` 열거자 2개 추가(하위 호환 — 기존 데이터 영향 없음).
- `tests/test_llm_integration.py`: analyze_project 실 API 통합 케이스 추가(기존 `llm_integration` 마커 재사용).
- **신규 런타임 의존성 없음.**
