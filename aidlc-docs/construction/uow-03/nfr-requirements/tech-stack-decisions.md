# UOW-03 (Claims/Evidence/Conflict) — Tech Stack Decisions

**단계**: CONSTRUCTION / NFR Requirements (UOW-03)
**작성일**: 2026-09-09

## 상속/재사용 (변경 없음)
| 항목 | 결정 | 근거 |
|---|---|---|
| LLM 서비스/프롬프트 | UOW-0F LLMService·get_prompt | 재사용 |
| 도메인 모델 | UOW-0F Claim/Evidence/Conflict/ClaimConfidence + `claim_key`/`normalize_value` | 재사용 |
| 카탈로그 | UOW-02 build_catalog/render_catalog(발췌 4000) | Q3=A 상속 |
| 저장소/캐시 | UOW-02 KnowledgeStore/AnalysisCache | 재사용(완본 재저장) |
| 스캔 | UOW-01 scan_project_assets | analyze_project 입력 |
| PBT | hypothesis(기존 dev) | Q1 |
| 통합 테스트 마커 | 기존 `llm_integration`(UOW-02 등록) | Q2=A 재사용 |

## UOW-03 고유 결정
| 항목 | 값 |
|---|---|
| ConflictType 확장 | STALE_KNOWLEDGE, POLICY_CONFLICT 추가(domain.py 수정) |
| 부재 토큰 집합 | {absent, none, missing, n/a, null, 없음, 부재} (conflict/detect 상수) |
| 추출 호출 | Feature당 1회(ExtractedClaim 목록) |
| 충돌 검출 | 결정적 순수 함수(비-LLM) |

## 의존성 변경
- 신규 런타임 의존성 **없음**(표준 라이브러리 + 기존). 통합 마커도 UOW-02에서 이미 등록됨.

## 미결(후속 단위)
- Task Impact(UOW-04)는 이 완본 지식·충돌을 소비. MCP 노출(UOW-05)은 analyze_project/get_conflicts를 래핑.
