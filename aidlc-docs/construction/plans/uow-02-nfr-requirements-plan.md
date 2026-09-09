# UOW-02 (Feature & Knowledge) — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (UOW-02)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-IDF/KN/STORE/CACHE/FAIL/DET/SEC). LLM/직렬화/캐시 계약은 확정.
여기서는 토큰/비용 상한·재현성·신뢰성·보안·**PBT 속성**을 확정한다.
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 계획 스텝 (체크박스)
- [ ] S1. LLM 비용/토큰 NFR — 카탈로그 발췌 상한·max_features 기본값·프롬프트 크기 관리
- [ ] S2. 성능/캐시 NFR — 캐시 히트 시 LLM 미호출(NFR-PERF-003) 측정 기준
- [ ] S3. 신뢰성 NFR (Resiliency) — LLM/저장 부분 실패 강등 정책 정합화
- [ ] S4. 보안 NFR — 프롬프트/로그 시크릿·원문 위생, 저장 경로 루트 강제
- [ ] S5. 재현성 NFR — 결정성 파라미터·캐시 해시·FakeLLM 오프라인 테스트
- [ ] S6. PBT 속성 대상 확정
- [ ] S7. nfr-requirements.md / tech-stack-decisions.md 작성 + 확장 컴플라이언스 요약

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. LLM 입력 상한 기본값 — 토큰/비용 관리
- **A. 자산당 발췌 1,200자 + 카탈로그 총 상한(예: 자산 200개 또는 총 60,000자)·max_features=12** (권장) — 데모/로컬에 안전, 예측 가능
- **B. 더 큰 상한(발췌 4,000자·max_features 무제한)** — 정밀↑, 토큰/비용/지연↑
- **C. 기타(직접 지정)**

[Answer]:

### Q2. PBT(속성 기반 테스트) 대상 — 무엇을 불변식으로 검증할까? (복수 선택 가능)
- **A. id 안전화 전결정성**: 임의 title/후보 id → 항상 파일/URI 안전한 id(`/\..` 없음, 비어있지 않음)
- **B. 캐시 해시 안정성**: 자산 순서를 섞어도 compute_assets_hash 동일; content 1바이트 변하면 달라짐
- **C. 카탈로그 발췌 상한**: 임의 길이 content → excerpt가 항상 상한 이하, 개행 정규화 유지
- **D. 저장 round-trip**: 임의 FeatureKnowledge 셸 → save→load 결과가 동일(멱등)

선택(권장: **A,B,C,D 전부**):

[Answer]:

### Q3. LLM 테스트 정책 — 네트워크/실호출 없이 검증?
- **A. 전량 FakeLLMClient(주입) 기반, 네트워크·실제 API 키 불필요. 결정적 응답으로 모든 경로 검증** (권장) — CI/재현성·비용 0
- **B. 일부 통합 테스트에서 실제 API 호출(옵트인/키 필요)** — 실측이나 비결정·비용·키 필요

[Answer]:

### Q4. 캐시 손상/버전 불일치 처리
- **A. 손상·스키마 불일치 캐시는 '미스'로 간주하고 조용히 재분석(안전 폴백) + 디버그 로그** (권장) — 견고, 사용자 방해 없음
- **B. 오류로 표면화(warning)** — 가시성↑, 잡음↑

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-02/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/uow-02/nfr-requirements/tech-stack-decisions.md`
