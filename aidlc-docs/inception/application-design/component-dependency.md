# TRACE — 컴포넌트 의존성 & 데이터 흐름 (Component Dependency)

**단계**: INCEPTION / Application Design
**작성일**: 2026-09-08

---

## 의존성 매트릭스 (행 → 열: "행이 열에 의존")

| ↓의존 \ 대상→ | C1 mcp_server | C2 engine | C3 workflow | C4 knowledge | C5 conflict | C6 impact | C7 config | C8 prompts | LLM |
|---|---|---|---|---|---|---|---|---|---|
| **C1 mcp_server** | — | ✅ | | ✅(읽기) | | ✅ | ✅ | (P1) | |
| **C2 engine** | | — | ✅ | ✅ | ✅ | ✅ | ✅ | | |
| **C3 workflow** | | | — | ✅(모델) | | | ✅ | ✅ | ✅ |
| **C4 knowledge** | | | | — | | | ✅ | | |
| **C5 conflict** | | | | ✅ | — | | | | |
| **C6 impact** | | | ✅ | ✅ | ✅ | — | | ✅ | (via C3) |
| **C7 config** | | | | | | | — | | |
| **C8 prompts** | | | | | | | | — | |
| **C9 cli** | | ✅(코어 함수) | | | | | ✅ | | |

- 순환 의존 없음. C7(config)·C8(prompts)은 잎(leaf). C4(knowledge)는 C5·C6·C3가 공유하는 모델 허브.
- 어댑터(C1, C9)는 서비스/코어 함수에만 의존하고 C3(AI)에 직접 의존하지 않음 → 코어/인터페이스 분리(NFR-CORE-001).

**Increment 2 (C10 map) 추가 의존** *(상세: `onboarding-map-design.md` §6)*:
- **C10 map** → C4(knowledge), C3(workflow), C8(prompts), C7(config).
- **C2 engine** → **+C10** (코어함수 `generate_onboarding_map` 오케스트레이션). C1/C9는 코어함수만 호출(변화 없음).
- 위상 `C7/C8 ← C4 ← C10 ← C2 ← C1/C9`, `C2→C10→C3`(기존 C2→C3와 동형) — **순환 없음** 유지.

## 통신 패턴
- **동기 함수 호출**(in-process, 로컬). 원격/네트워크 없음(NFR-LOCAL-001, stdio 전송은 C1↔클라이언트 경계에서만).
- LLM 접근은 C3 내부 LLMService로 캡슐화(단일 창구). 시크릿은 C7 통해 환경변수로만(NFR-SEC-001).
- 파일시스템 접근은 C2(스캔·파싱)·C4(지식 I/O)로 국한.

---

## 데이터 흐름 — analyze_project

```text
[대상 프로젝트 파일]
      │ (C2 scan/parse, C7 제외규칙)
      ▼
   assets ──► [C3 identify_features] ──► candidates
                     │ (C8 prompts, LLM)
                     ▼
         claims/evidence/confidence ──► [C5 detect_conflicts] ──► conflicts
                     │                                              │
                     └──────────► [C3 generate_feature_knowledge] ◄─┘
                                          │
                                          ▼
                              [C4 save_feature] ──► .trace/knowledge/features/<id>.md
                                          │
                                          ▼
                                     Result envelope ──► [C1 도구 결과] / [C9 CLI 출력]
```

## 데이터 흐름 — analyze_task_impact

```text
task(자연어) + feature_id?
      │ (C4 load knowledge/evidence — 그라운딩)
      ▼
  KnowledgeContext ──► [C5 관련 충돌 수집] ──► related_conflicts (경고, P1)
      │
      ▼
 [C6/C3 analyze_task] ──► Must/Likely/Review (+reason,+evidence)
      │
      ▼
 [C6 build change_plan] ──► ordered steps
      │
      ▼
  Result envelope (summary→conflicts→impact→evidence) ──► [C1]/[C9]
```

## MCP 경계 (C1 ↔ Claude Code)
- 전송: **stdio** (FR-MCP-004). 도구=코어 함수 1:1, 리소스=`.trace/knowledge/*.md`, 프롬프트=P1.
- 결과 봉투는 JSON 구조화 + 사람 요약 텍스트 동반. 시크릿 비노출(NFR-SEC-005).

## NFR 준수 확인 (설계 수준)
- **NFR-CORE-001/002**: 코어(C2 서비스)와 인터페이스(C1/C9) 분리, 서비스 재사용 ✅
- **NFR-MAINT-001**: 모듈 분리(C1~C9 경계) ✅ / **NFR-MAINT-002**: 프롬프트 분리(C8) ✅
- **NFR-LOCAL-001**: 파일 접근 C2/C4 국한 ✅
- **NFR-AI-001/002/003**: 구조화 출력·그라운딩·불확실성은 C3 step 계약 ✅
- **NFR-SEC-001/004/005**: 시크릿 env(C7), 경로 검증(C2), stdio 비노출(C1) ✅
- **Resiliency**: 로컬 in-process·단일 프로세스 → 인프라 룰(멀티존/리전/DR) N/A, 관측성은 로깅(NFR-LOG-001)로 최소 충족. (NFR Design에서 상세 컴플라이언스 요약)
