# UOW-04 (Task Impact Analysis) — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (UOW-04)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-CTX/IMP/CONFWARN/PLAN/PIPE/SEC/DET). 지식 그라운딩·3범주 분류·
허구 path 강등·기존 충돌 노출·순서형 Change Plan·소스 자동수정 없음. 여기서 성능·재현성·부분실패·보안·**PBT 속성** 확정.
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 계획 스텝 (체크박스)
- [x] S1. LLM 비용/토큰 — analyze_task 1회 호출, 컨텍스트 발췌 상한 상속(Q3)
- [x] S2. 성능 — build_context/to_impact_out/rank_by_relevance 순수(무네트워크), 저장 지식 재사용(analyze_project 산출)
- [x] S3. 신뢰성(Resiliency) — LLM 실패·지식부재·손상 파일 강등, related_conflicts는 LLM과 무관하게 노출
- [x] S4. 보안 — 프롬프트 known_sources 화이트리스트, reason/warning 원문·절대경로 비노출
- [x] S5. 재현성 — 매핑·정렬·랭킹 결정적, FakeLLM + llm_integration 옵트인(Q2)
- [x] S6. PBT 속성 대상 확정(Q1)
- [x] S7. nfr-requirements.md / tech-stack-decisions.md 작성 + 확장 컴플라이언스 요약

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. PBT(속성 기반 테스트) 대상 — 무엇을 불변식으로? (복수 선택)
UOW-04 코어(to_impact_out/rank_by_relevance)는 순수 함수 → PBT에 적합.
- **A. 매핑 건전성**: `path ∉ known_sources` 후보는 절대 must/likely에 남지 않고 항상 review로 강등
- **B. 근거 부족 강등**: evidence가 빈 후보는 항상 review + Insufficient evidence 표기
- **C. 정렬 결정성/멱등**: 후보 입력 순서를 섞어도 동일 ImpactOut(카테고리별 path 정렬)
- **D. related_conflicts 정합**: focus conflicts 수 == related_conflicts 수(누락·중복 없음)

선택(권장: **A,B,C,D 전부**):

[Answer]: A,B,C,D (권장)

### Q2. LLM 테스트 정책 — UOW-02/03과 동일하게?
- **A. 기본 FakeLLM 오프라인 + 기존 `llm_integration` 마커 옵트인(analyze_task_impact 실 API 통합 1건 추가)** (권장) — 일관·재현·비용 0
- **B. 오프라인만(통합 테스트 없음)**
- **C. 기타(직접 지정)**

[Answer]: A (권장)

### Q3. 컨텍스트 상한 — 발췌·focus 개수
- **A. 자산/근거 발췌 4,000자 상속(UOW-02/03) + focus 상세는 관련도 상위 N=3 기본(전체 요약은 항상 포함)** (권장) — 토큰 예측성·집중
- **B. UOW-04 전용 상한 별도 지정(직접 지정)**

[Answer]: A (권장)

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-04/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/uow-04/nfr-requirements/tech-stack-decisions.md`
