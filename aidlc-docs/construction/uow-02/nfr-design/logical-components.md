# UOW-02 (Feature & Knowledge) — Logical Components

**단계**: CONSTRUCTION / NFR Design (UOW-02)
**작성일**: 2026-09-09

> Code Generation의 파일 청사진. 모듈 책임·시그니처·의존 방향.

---

## 모듈 배치
```text
trace/
├── models/
│   └── feature_candidate.py    # [신설] FeatureCandidate, FeatureCandidateList
├── workflow/                   # [신설] C3 AI step
│   ├── __init__.py
│   ├── catalog.py              # build_catalog / render_catalog (P1)
│   └── features.py             # identify_features, generate_feature_knowledge, build_knowledge (P2/P6)
├── knowledge/                  # [신설] C4
│   ├── __init__.py
│   ├── ids.py                  # safe_feature_id (P3)
│   ├── store.py                # KnowledgeStore (P4)
│   └── cache.py                # compute_assets_hash, AnalysisCache, CacheEntry (P5)
└── prompts/templates/
    ├── identify_features.md    # [신설] (P7)
    └── feature_knowledge.md    # [신설] (P7)
tests/
├── test_features_workflow.py       # [신설]
├── test_knowledge_store.py         # [신설]
├── test_analysis_cache.py          # [신설]
├── test_features_properties.py     # [신설] PBT
└── test_llm_integration.py         # [신설] 옵트인
pyproject.toml                      # markers = [llm_integration]
```

## 시그니처

### models/feature_candidate.py
```python
class FeatureCandidate(BaseModel):
    id: str; title: str; description: str
    related_sources: list[str] = []
    rationale: str = ""
class FeatureCandidateList(BaseModel):
    features: list[FeatureCandidate] = []
class KnowledgeBody(BaseModel):     # 지식 본문 구조화 봉투
    markdown: str
```

### knowledge/ids.py
```python
def safe_feature_id(raw: str) -> str        # P3, 항상 안전·비어있지 않음
```

### workflow/catalog.py
```python
def build_catalog(assets: list[Asset], *, excerpt_chars: int = 4000) -> list[CatalogEntry]
def render_catalog(entries: list[CatalogEntry]) -> str
# CatalogEntry: rel_path, asset_type, excerpt (dataclass, 내부용)
```

### workflow/features.py
```python
def identify_features(assets, llm: LLMService, *, max_features: int | None = None
                      ) -> tuple[list[FeatureCandidate], list[Warning]]
def generate_feature_knowledge(candidate, assets, llm: LLMService,
                               claims=(), evidence=(), conflicts=()) -> FeatureKnowledge
def build_knowledge(assets, llm, store, cache) -> tuple[list[FeatureSummary], list[Warning]]
```

### knowledge/store.py
```python
class KnowledgeStore:
    def __init__(self, project_root: str | Path, knowledge_dir: str = ".trace/knowledge")
    def features_dir(self) -> Path
    def save_feature(self, fk: FeatureKnowledge) -> str
    def load_feature(self, feature_id: str) -> FeatureKnowledge
    def list_feature_summaries(self) -> list[FeatureSummary]
    def read_resource(self, uri: str) -> str
```

### knowledge/cache.py
```python
def compute_assets_hash(assets: list[Asset]) -> str
class CacheEntry(BaseModel): assets_hash: str; feature_ids: list[str] = []; meta: dict = {}
class AnalysisCache:
    def __init__(self, project_root: str | Path, cache_dir: str = ".trace/cache")
    def get(self, assets_hash: str) -> CacheEntry | None    # 손상=None(미스)
    def put(self, entry: CacheEntry) -> None
```

## 의존성 방향 (순환 없음)
```text
workflow/features → workflow/catalog, knowledge/{ids,store,cache}, llm/service, prompts/loader, models/*
knowledge/store   → models/{domain,result}, models/serialize, common/errors
knowledge/cache   → models/asset, hashlib, json, pydantic
```
- 모두 UOW-0F/UOW-01(leaf/스캐너)과 표준·서드파티에만 의존. UOW-03은 이 모듈을 소비·보강.

## 산출물 변경(Code Generation 예정)
- `pyproject.toml`: `[tool.pytest.ini_options].markers` 에 `llm_integration` 추가.
- 신규 런타임 의존성 없음.
