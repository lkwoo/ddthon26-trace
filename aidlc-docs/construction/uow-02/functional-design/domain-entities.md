# UOW-02 (Feature & Knowledge) — 도메인 엔티티 (domain-entities)

**단계**: CONSTRUCTION / Functional Design (UOW-02)
**작성일**: 2026-09-09
**결정 반영**: Q1=B(식별 상한), Q2=A(지식 셸), Q3=A(자산 카탈로그), Q4=A(콘텐츠 해시 캐시), Q5=A(.trace 프로젝트 루트)

> UOW-0F가 동결한 `Feature/FeatureKnowledge/Claim/Evidence/Conflict/FeatureSummary`와
> `serialize/deserialize`를 재사용한다. UOW-02는 신규 모델 `FeatureCandidate`와 저장소·캐시 계약을 추가한다.

---

## 1. 신규 모델

### FeatureCandidate — `trace/models/feature_candidate.py`
identify_features의 구조화 출력 요소. Feature로 승격되기 전 후보.
```text
FeatureCandidate(BaseModel):
    id: str            # 파일/URI 안전(소문자-케밥). Feature.id 규칙과 동일 검증
    title: str
    description: str
    related_sources: list[str]   # Asset.rel_path 목록(근거 자산)
    rationale: str = ""          # 왜 하나의 Feature인지(모델 설명, 감사용)
```
- `id` 검증: `/`,`\`,`..` 금지(Feature.id와 동일 — BR-ID-004). LLM이 안전 id를 못 주면 title에서 slug 생성.

### FeatureCandidateList — LLM 구조화 출력 봉투
```text
FeatureCandidateList(BaseModel):
    features: list[FeatureCandidate]
```
- `complete_structured(prompt, FeatureCandidateList)`로 검증(단일 루트 모델 요구 대응).

### AssetCatalogEntry / AssetCatalog — LLM 입력용(Q3=A)
```text
AssetCatalogEntry: rel_path, asset_type, excerpt   # excerpt=content 선두 N자(기본 1200) 정규화
# 카탈로그는 프롬프트 렌더용 문자열로 직렬화(모델 저장 안 함) — 내부 헬퍼 반환형
```

### CacheKey / CacheEntry — 캐시(Q4=A)
```text
CacheEntry(BaseModel):
    assets_hash: str                 # 자산 집합 콘텐츠 해시(키)
    feature_ids: list[str]           # 이 해시로 저장된 Feature id 목록
    meta: dict = {}                  # model, created 등(결정성 위해 타임스탬프는 선택)
```

## 2. 저장소 계약 (C4) — `trace/knowledge/store.py`
`.trace` 루트는 **분석 대상 프로젝트 루트 하위**(Q5=A). 경로 생성은 UOW-01 `is_within_root`/config 정합.
```text
class KnowledgeStore:
    def __init__(self, project_root: str | Path, knowledge_dir=".trace/knowledge") -> None
    def features_dir(self) -> Path                       # <root>/.trace/knowledge/features
    def save_feature(self, fk: FeatureKnowledge) -> str  # serialize→ <features>/<id>.md, 경로 반환
    def load_feature(self, feature_id: str) -> FeatureKnowledge   # deserialize, 손상 시 StorageError
    def list_feature_summaries(self) -> list[FeatureSummary]      # features/*.md 로드→요약(결정적 정렬)
    def read_resource(self, uri: str) -> str             # trace://feature/<id> → body_markdown
```
- `save_feature`는 `id`를 파일명으로 사용(BR-ID-004 안전). 디렉터리 없으면 생성(루트 하위 강제).
- `read_resource` URI 스킴: `trace://feature/<id>`(UOW-05 MCP 리소스가 소비). 미존재 → StorageError.

## 3. 캐시 계약 (C4) — `trace/knowledge/cache.py`
```text
def compute_assets_hash(assets: list[Asset]) -> str
    # sha256 over "\n".join(sorted f"{rel_path}:{size_bytes}:{sha256(content or '')}")  (결정적)
class AnalysisCache:
    def __init__(self, project_root, cache_dir=".trace/cache")
    def get(self, assets_hash: str) -> CacheEntry | None
    def put(self, entry: CacheEntry) -> None
```
- 캐시 위치 `<root>/.trace/cache/<assets_hash>.json`. 해시 불일치=무효화(자동).

## 4. C3 AI step (workflow) — `trace/workflow/features.py`
```text
def identify_features(assets, llm: LLMService, *, max_features: int) -> list[FeatureCandidate]
def generate_feature_knowledge(candidate, assets, llm: LLMService) -> FeatureKnowledge
    # Q2=A: feature+related_sources+body_markdown(개요)만. claims/evidence/conflicts=[] (UOW-03 보강)
```
- `generate_feature_knowledge`는 component-methods의 (feature, claims, evidence, conflicts) 시그니처를
  **기본값 빈 목록**으로 수용해 UOW-03이 동일 함수로 완본화할 수 있게 한다(하위 호환).

## 5. 기존 모델로의 매핑
- FeatureCandidate → `Feature(id,title,description,related_sources)`로 승격.
- `Asset.rel_path` → related_sources / (UOW-03에서) Evidence.source.
- FeatureKnowledge(shell) → `serialize()`로 MD+YAML 저장(UOW-0F). body_markdown이 MCP 리소스 본문.
