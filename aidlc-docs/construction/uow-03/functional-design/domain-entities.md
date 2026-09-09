# UOW-03 (Claims/Evidence/Conflict) — 도메인 엔티티 (domain-entities)

**단계**: CONSTRUCTION / Functional Design (UOW-03)
**작성일**: 2026-09-09
**결정 반영**: Q1=A(ConflictType 확장), Q2=A(결정적 검출), Q3=A(Feature당 1회 추출), Q4=A(근거 일치도), Q5=A(analyze_project 완성)

> UOW-0F 모델(Claim/Evidence/ClaimConfidence/Conflict/ConflictValue/claim_key/normalize_value)을 재사용.
> UOW-03은 (1) ConflictType 확장, (2) LLM 추출 중간 스키마 신설을 추가한다.

---

## 1. ConflictType 확장 (Q1=A) — `trace/models/domain.py` 수정
```text
class ConflictType(str, Enum):
    VALUE_MISMATCH = "value_mismatch"      # P0 (기존)
    STALE_KNOWLEDGE = "stale_knowledge"    # P1 (추가) — 문서/지식이 구현과 어긋남(드리프트)
    POLICY_CONFLICT = "policy_conflict"    # P1 (추가) — 요구(필수/규정) vs 구현 부재
```
- 기존 `Conflict._at_least_two_distinct` 검증(값 2개 이상·정규화 후 상이)은 3유형 모두에 그대로 적용.
- 하위 호환: 저장된 기존 데이터는 value_mismatch만 사용했으므로 역직렬화 영향 없음.

## 2. LLM 추출 중간 스키마 (Q3=A) — `trace/models/extraction.py` 신설
Feature당 1회 구조화 호출로 Claim과 각 Claim의 Evidence를 함께 산출.
```text
class ExtractedClaim(BaseModel):
    subject: str            # 예: "Owner.telephone"
    predicate: str          # 예: "max_length"
    evidence: list[Evidence]  # 각 소스별 extracted_value·relation (UOW-0F Evidence 재사용)

class ClaimExtractionResult(BaseModel):   # complete_structured 루트
    claims: list[ExtractedClaim] = []
```
- Evidence(UOW-0F): `source(rel_path)·type(EvidenceType)·location·extracted_value·relation(supports/contradicts/mentions)`.
- 이 중간 결과를 평탄화해 FeatureKnowledge.claims/evidence 를 채우고, 그룹 단위로 confidence·conflict를 계산한다.

## 3. 파생 규칙 (중간 → 최종 모델)
| 중간 | 최종(FeatureKnowledge) |
|---|---|
| ExtractedClaim.subject/predicate | Claim.subject/predicate, value=대표값(아래) , feature_id=현재 feature |
| 대표 Claim.value | 그 claim의 evidence 중 **최다 지지(supports) 값**; 동률/부재 시 정규화 사전순 첫 값 |
| ExtractedClaim.evidence[*] | FeatureKnowledge.evidence 에 평탄 추가 |
| (claim별 계산) | ClaimConfidence(claim_key, assessment) — §Confidence 규칙 |
| (claim별 계산) | Conflict(type, claim=claim_key, values, interpretation) — §Conflict 규칙 |

## 4. 코어 함수 계약 (component-methods)
```text
# workflow (C3)
def extract_claims(feature, assets, llm) -> list[ExtractedClaim]      # Feature당 1회 LLM
def assign_confidence(ec: ExtractedClaim) -> ClaimConfidence          # 비-LLM, 근거 일치도(Q4=A)
# conflict (C5)
def detect_conflicts(claims: list[ExtractedClaim], feature_id) -> list[Conflict]   # 결정적(Q2=A)
def summarize_conflicts(store, feature_id: str | None) -> list[ConflictOut]
# engine (C2) — 코어 공개
def get_conflicts(feature_id: str | None = None) -> Result           # ConflictOut 목록/상세
def analyze_project(path: str) -> Result                              # 전체 파이프라인(Q5=A)
```
- `group_evidence`는 Q3=A로 추출 단계에 흡수(별도 호출 없음) — evidence가 ExtractedClaim에 내장.

## 5. get_conflicts / analyze_project 데이터 계약
```text
analyze_project(path).data = {features:[FeatureSummary...], assets_count, conflicts_count}
   + Result.conflicts = 전체 ConflictOut(핵심 우선 노출, build_result)
get_conflicts(fid).conflicts = [ConflictOut{type, claim, values:[{value,source,location}], interpretation}]
   + meta.conflicts_count (FR-CONFLICT-OUT-001/002)
```
- FeatureKnowledge는 conflicts/claims/evidence/confidence가 채워져 **완본**으로 재저장(UOW-02 셸 대체).
