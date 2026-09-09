# UOW-05 (MCP 서버 인터페이스) — NFR Design 계획

**단계**: CONSTRUCTION / NFR Design (UOW-05)
**작성일**: 2026-09-09
**입력**: nfr-requirements(IF/RUN/REL/UX/SEC/TST/MAINT), tech-stack-decisions(mcp>=2.0·MCPServer·serialize_result·코어 래퍼)
**활성 확장**: Resiliency Baseline(Blocking). **추가 질문 없음** — 패턴이 앞 단계 결정에서 일의적으로 도출됨.

---

## 계획 스텝 (체크박스)
- [x] S1. 서버 구성 패턴 — build_server(): MCPServer + 도구/리소스/프롬프트 데코레이터 등록
- [x] S2. 도구 핸들러 패턴 — 얇은 래퍼(입력→루트 주입→코어→serialize_result), 오류 격리(NFR-05-REL-1)
- [x] S3. 직렬화 패턴 — serialize_result(Result→dict, 핵심 우선·None 제외)(NFR-05-UX-1)
- [x] S4. 코어 래퍼 — list_features/get_feature_knowledge(store 위임, Result 반환)
- [x] S5. 리소스/프롬프트 패턴 — trace://feature/{id} 리소스, 구현전검토 프롬프트(P1)
- [x] S6. nfr-design-patterns.md / logical-components.md 작성 + 확장 컴플라이언스 요약

---

## 산출물
- `aidlc-docs/construction/uow-05/nfr-design/nfr-design-patterns.md`
- `aidlc-docs/construction/uow-05/nfr-design/logical-components.md`
