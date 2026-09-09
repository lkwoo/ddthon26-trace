# UOW-04 (Task Impact Analysis) — NFR Design 계획

**단계**: CONSTRUCTION / NFR Design (UOW-04)
**작성일**: 2026-09-09
**입력**: nfr-requirements(COST/PERF/REL/SEC/TST/PBT-04-A~D), functional-design(BR-CTX/IMP/CONFWARN/PLAN/PIPE/SEC/DET)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).
**추가 질문 없음** — 패턴이 앞 단계 결정에서 일의적으로 도출됨(UOW-02/03과 동일 판단).

---

## 계획 스텝 (체크박스)
- [x] S1. 컨텍스트 조립 패턴 — build_context + 관련도 랭킹(순수), known_sources 화이트리스트(NFR-04-COST-2/SEC-1)
- [x] S2. LLM step 패턴 — analyze_task 구조화 호출 + 상위 강등(NFR-04-REL-1, BR-PIPE)
- [x] S3. 매핑/강등 순수함수 패턴 — to_impact_out(허구 path·근거부족 review, 정렬)(NFR-04-TST-1, PBT-04-A/B/C)
- [x] S4. 충돌 노출 패턴 — related_conflicts를 LLM과 독립적으로 저장 지식에서 채움(NFR-04-REL-2, PBT-04-D)
- [x] S5. 조립 패턴 — analyze_task_impact(컨텍스트→LLM→매핑→build_result), 지식부재/실패 강등(BR-PIPE)
- [x] S6. 테스트 배치 — 순수함수 단위·PBT-04-A~D·FakeLLM 파이프라인·옵트인 통합(NFR-04-TST)
- [x] S7. nfr-design-patterns.md / logical-components.md 작성 + 확장 컴플라이언스 요약

---

## 산출물
- `aidlc-docs/construction/uow-04/nfr-design/nfr-design-patterns.md`
- `aidlc-docs/construction/uow-04/nfr-design/logical-components.md`
