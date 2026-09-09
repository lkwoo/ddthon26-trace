# UOW-03 (Claims/Evidence/Conflict) — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (UOW-03)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-CLAIM/EVID/CONF/CONFLICT/OUT/PIPE/DET/SEC). 결정적 검출·근거일치
Confidence·analyze_project 완성 확정. 여기서는 성능·재현성·부분실패·보안·**PBT 속성**을 확정한다.
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 계획 스텝 (체크박스)
- [ ] S1. LLM 비용/토큰 — 추출 입력(발췌 상한)·Feature당 1회 호출 정책(UOW-02 상속 확인)
- [ ] S2. 성능/캐시 — 완본 스테이지 캐시(재실행 LLM 미호출) 기준
- [ ] S3. 신뢰성(Resiliency) — Feature별 추출/충돌 실패 강등, 전체 계속
- [ ] S4. 보안 — 프롬프트/로그 위생, Evidence 원문 비노출
- [ ] S5. 재현성 — 결정적 검출/Confidence, FakeLLM 오프라인 + 옵트인 통합
- [ ] S6. PBT 속성 대상 확정(순수 함수 중심)
- [ ] S7. nfr-requirements.md / tech-stack-decisions.md 작성 + 확장 컴플라이언스 요약

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. PBT(속성 기반 테스트) 대상 — 무엇을 불변식으로? (복수 선택)
UOW-03의 핵심 로직(detect_conflicts/classify/assign_confidence)은 순수 함수 → PBT에 이상적.
- **A. 충돌 검출 건전성**: distinct 정규화 값이 1개 이하면 절대 Conflict를 만들지 않고, 2개 이상이면 반드시 Conflict 1건 생성
- **B. 검출 결정성/멱등**: 동일 ExtractedClaim 입력을 2회(및 evidence 순서 섞어) 처리해도 동일 conflicts
- **C. 유형 분류 전결정성**: classify_conflict_type은 임의 입력에 항상 유효한 ConflictType 하나 반환(예외 없음)
- **D. Confidence 규칙 정합**: contradicts/≥2값이면 반드시 LOW, 일치·다근거면 HIGH, 그 외 MEDIUM (규칙과 100% 일치)

선택(권장: **A,B,C,D 전부**):

[Answer]:

### Q2. LLM 테스트 정책 — UOW-02와 동일하게?
- **A. 기본 FakeLLM 오프라인 + 기존 `llm_integration` 마커 옵트인(analyze_project 실 API 통합 1건 추가)** (권장) — 일관·재현성·비용 0
- **B. 오프라인만(통합 테스트 없음)** — 더 단순, 실측 없음
- **C. 기타(직접 지정)**

[Answer]:

### Q3. 추출 입력 상한 — UOW-02 카탈로그 상한 상속?
- **A. UOW-02와 동일(자산 발췌 4,000자, 관련 자산만) 상속** (권장) — 일관·예측 가능
- **B. UOW-03 전용 상한 별도 지정(직접 지정)**

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-03/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/uow-03/nfr-requirements/tech-stack-decisions.md`
