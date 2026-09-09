# UOW-05 (MCP 서버 인터페이스) — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (UOW-05)
**작성일**: 2026-09-09
**Functional Design**: **SKIP**(얇은 어댑터 — 5 도구=코어함수 1:1, 새 비즈니스 로직 없음).
**책임**: 5 MCP 도구 노출(입력스키마·구조화 결과), 지식 리소스(`.trace/knowledge/*.md`), stdio 전송, (P1)프롬프트.
**요구사항**: FR-MCP-001~004, FR-STORAGE-002, NFR-MCP-UX-001~003, US-05.1~05.4.
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면 — 해당 시).
**환경 사실**: 설치된 `mcp`는 **2.x**(`from mcp.server.mcpserver import MCPServer`, 구 FastMCP). 데코레이터 `.tool/.resource/.prompt`,
`run(transport="stdio")`. pyproject는 현재 `mcp>=1.2.0` → 상향 필요.

---

## 계획 스텝 (체크박스)
- [ ] S1. SDK/전송 — MCPServer 고수준 데코레이터·stdio, 의존성 버전 결정(Q1)
- [ ] S2. 코어 래퍼 — list_features/get_feature_knowledge를 Result 반환 얇은 코어로 추가(engine)
- [ ] S3. 도구 배선 — 5 도구=코어함수 1:1, 입력 스키마(타입힌트), 프로젝트 루트 주입(Q2)
- [ ] S4. 직렬화/UX — Result→JSON, 핵심 우선 순서(요약→conflicts→impact→evidence, NFR-MCP-UX-002)
- [ ] S5. 신뢰성 — 어댑터 오류 격리(코어 예외→구조화 오류 Result, 서버 무크래시)(Q3)
- [ ] S6. 리소스/프롬프트 — trace://feature/<id> 리소스, (P1)구현 전 검토 프롬프트(Q4)
- [ ] S7. 테스트 — 도구 등록/직렬화/오류매핑(오프라인), stdio 기동 스모크
- [ ] S8. nfr-requirements.md / tech-stack-decisions.md 작성 + 확장 컴플라이언스 요약

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. MCP SDK API — 설치 환경(mcp 2.x)과 정합?
- **A. `mcp.server.mcpserver.MCPServer` 고수준 데코레이터(.tool/.resource/.prompt) + `run("stdio")`, pyproject `mcp>=2.0`으로 상향** (권장) — 설치 환경 일치·간결·타입힌트 스키마
- **B. 저수준 `mcp.server.Server` API** — 장황, 스키마 수기
- **C. `mcp<2` 핀 + 재설치 후 FastMCP v1** — 환경 변경 필요
- **D. 기타(직접 지정)**

[Answer]:

### Q2. 프로젝트 루트 주입 — 코어 함수 path 인자
- **A. 서버 기동 cwd 기본 + `TRACE_PROJECT_ROOT` 환경변수 오버라이드** (권장) — .mcp.json에서 cwd 지정, 도구 입력 단순
- **B. 각 도구 입력 파라미터로 path 노출** — 유연하나 에이전트가 매번 지정
- **C. 기타(직접 지정)**

[Answer]:

### Q3. 오류/입력검증 실패 처리
- **A. 어댑터가 코어 호출을 감싸 `error_to_result`(구조화 오류 Result·JSON)로 반환, 서버 크래시 없음** (권장, NFR-REL·Resiliency)
- **B. 예외를 MCP 오류로 그대로 전파**
- **C. 기타(직접 지정)**

[Answer]:

### Q4. P1 프롬프트 템플릿(구현 전 검토) 포함?
- **A. 포함 — "구현 착수 전 충돌·영향 검토" MCP 프롬프트 등록(FR-MCP-003)** (권장) — 사용성·의도 유도
- **B. UOW-06로 연기**
- **C. 기타(직접 지정)**

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-05/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/uow-05/nfr-requirements/tech-stack-decisions.md`
