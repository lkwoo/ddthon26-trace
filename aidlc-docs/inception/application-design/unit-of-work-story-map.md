# TRACE — 스토리 ↔ 단위 매핑 (Unit of Work Story Map)

**단계**: INCEPTION / Units Generation (Part 2)
**작성일**: 2026-09-08
**출처**: user-stories/stories.md (22 스토리 / 6 Epic)

> Q5=A: 기존 스토리 매핑 유지. **UOW-0F는 enabler 단위로 직접 대응 스토리 없음**(다수 스토리를 뒷받침).

---

## 매핑 표

| 단위 | 스토리 | 대표 FR/NFR |
|---|---|---|
| **UOW-0F** (enabler) | — (직접 없음) | 뒷받침: US-02.3/03.1/03.2(모델·직렬화), US-06.4(시크릿 env), NFR-CORE-001/002, NFR-MAINT-002, NFR-LOG-001 |
| **UOW-00** 데모 | — (데이터 전제) | 뒷받침: US-06.1(Hero 데이터), US-02.2/03.3(검증 입력); FR-DEMO-001, Q6 |
| **UOW-01** 스캐너 | US-01.1, US-01.2, US-01.3 | FR-PROJECT-001/002/003, FR-ANALYSIS-003, NFR-SEC-004 |
| **UOW-02** Feature/Knowledge | US-02.1, US-02.2, US-02.3 | FR-ANALYSIS-001, FR-KNOWLEDGE-001/002/003, FR-STORAGE-001, NFR-PERF-003 |
| **UOW-03** Claims/Conflict | US-03.1, US-03.2, US-03.3, US-03.4 | FR-CLAIM-001, FR-EVIDENCE-001, FR-CONFIDENCE-001, FR-CONFLICT-001, FR-CONFLICT-OUT-001/002 |
| **UOW-04** Task Impact | US-04.1, US-04.2, US-04.3, US-04.4 | FR-IMPACT-001~006, NFR-AI-003 |
| **UOW-05** MCP 어댑터 | US-05.1, US-05.2, US-05.3, US-05.4(P1) | FR-MCP-001~004, FR-STORAGE-002, NFR-MCP-UX-002/003 |
| **UOW-06** 통합·시연 | US-06.1, US-06.2, US-06.3, US-06.4 | NFR-REL-001/002, NFR-AI-004, FR-DEMO-001/002, NFR-SEC-001/002/005 |

---

## 배정 완결성 확인

- **총 22개 스토리 전부 배정** (UOW-01:3, 02:3, 03:4, 04:4, 05:4, 06:4).
- **UOW-0F / UOW-00**: 직접 대응 스토리 없음 — 각각 기술 enabler / 데이터 전제. 미배정 스토리 아님(설계상 지원 단위).
- **미배정 스토리 없음. 중복 배정 없음.**

## Hero 시나리오 스토리 경로 (E2E)
US-01.1 → US-02.1 → US-02.2/02.3 → US-03.1/03.2/03.3 → US-03.4 → US-04.1/04.2/04.3/04.4 → US-05.x(노출) → US-06.1(E2E 앵커)

각 단위를 완료하면 이 경로가 한 칸씩 이어지며, UOW-06에서 무편집 E2E로 수렴한다.
