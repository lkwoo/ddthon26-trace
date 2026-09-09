# UOW-03 (Claims/Evidence/Conflict) — NFR Design 계획

**단계**: CONSTRUCTION / NFR Design (UOW-03)
**작성일**: 2026-09-09
**입력**: nfr-requirements(COST/PERF/REL/SEC/TST/PBT-03-A~D), functional-design(BR-CLAIM/EVID/CONF/CONFLICT/OUT/PIPE/DET/SEC)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).
**추가 질문 없음** — 패턴이 앞 단계 결정(NFR 요구·기능 설계)에서 일의적으로 도출됨(UOW-02와 동일 판단).

---

## 계획 스텝 (체크박스)
- [x] S1. 추출 step 패턴 — 구조화 호출 + Feature별 격리 강등(NFR-03-REL-1, BR-PIPE-002)
- [x] S2. 비-LLM 결정적 코어 패턴 — assign_confidence/detect_conflicts/classify(순수함수, NFR-03-PERF-3/TST-1)
- [x] S3. 충돌 유형 분류 패턴 — 상수·전용 함수 국소화, 모호 시 value_mismatch 폴백(NFR-03-REL-3/MAINT-2)
- [x] S4. 완본화·오케스트레이션 패턴 — enrich + analyze_project 캐시-완본 스테이지(NFR-03-PERF-1/2)
- [x] S5. 보안/재현성 패턴 — 허구근거 드롭·위치표기·안정정렬(NFR-03-SEC-1~3/DET)
- [x] S6. 테스트 배치 — 순수함수 단위·PBT-03-A~D·FakeLLM 파이프라인·옵트인 통합(NFR-03-TST)
- [x] S7. nfr-design-patterns.md / logical-components.md 작성 + 확장 컴플라이언스 요약

---

## 산출물
- `aidlc-docs/construction/uow-03/nfr-design/nfr-design-patterns.md`
- `aidlc-docs/construction/uow-03/nfr-design/logical-components.md`
