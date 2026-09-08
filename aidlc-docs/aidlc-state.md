# AI-DLC State Tracking

## Project Information
- **Project Name**: TRACE — 개발자 지식 인텔리전스 (작업명)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: INCEPTION - Requirements Analysis

## Workspace State
- **Existing Code**: No
- **Programming Languages**: None yet (미결정 — 요구사항 §23 참조)
- **Build System**: None yet
- **Project Structure**: Empty (문서만 존재)
- **Reverse Engineering Needed**: No
- **Workspace Root**: C:\claude\aidlc-workshop\ddthon26-trace

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Input Artifacts
- **Requirements Source**: requirments/trace-requirements.md (사용자 제공, 1458줄, 매우 상세)
- **Assessment Criteria**: requirments/assessment.md (100점 만점 해커톤 평가)

## Extension Configuration
| Extension | Enabled | Mode | Decided At |
|---|---|---|---|
| Security Baseline | No | — | Requirements Analysis (Q8=B) |
| Resiliency Baseline | Yes | Blocking (전면) | Requirements Analysis (Q9=A) |
| Property-Based Testing | Yes | Blocking (전면) | Requirements Analysis (Q10=A) |

**참고**: Security Baseline 확장은 미적용이나, 요구사항 문서 자체의 NFR-SEC-001~005(P0 시크릿/경로검증/로컬처리 등)는 그대로 유효한 요구사항으로 유지된다.

## 확정된 기술 결정 (Requirements Q1~Q7)
| # | 결정 | 값 |
|---|---|---|
| Q1 | 구현 스택 | Python + 공식 Python MCP SDK (`mcp`) |
| Q2 | LLM | Anthropic Claude (예: Claude Sonnet 5) |
| Q3 | 문서 파서 | Markdown/텍스트/OpenAPI/SQL/설정/소스/테스트 + **PDF(P0)**; DOCX/PPTX는 P1 |
| Q4 | Feature 검출 | 완전 자동 |
| Q5 | 폴백 | 분석 결과 캐시 + 얇은 폴백 CLI (둘 다) |
| Q6 | 데모 데이터셋 | Spring Petclinic REST + 의도적 충돌 합성 문서 |
| Q7 | 명칭 | TRACE (확정) |

## Execution Plan Summary
- **Stages to Execute**: Application Design, Units Generation, (per-unit) Functional Design, NFR Requirements, NFR Design, Code Generation, Build and Test
- **Stages to Skip**: Reverse Engineering (greenfield), Infrastructure Design (로컬 stdio 단일 프로세스, 클라우드 인프라 없음)
- **권장 유닛 순서**: UOW-00(데모 데이터셋, 신설) → 01 → 02 → 03 → 04 → 05 → 06
- **UOW-00 신설(사용자 요청)**: 데모 데이터셋 & 픽스처를 별도 유닛으로 분리. 접근법=하이브리드(Petclinic Owner 조각 발췌 + 합성 PDF·의도적 충돌).

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [ ] Reverse Engineering (SKIP — greenfield)
- [x] Requirements Analysis
- [x] User Stories
- [x] Workflow Planning
- [x] Application Design — EXECUTE
- [ ] Units Generation — EXECUTE

### 🟢 CONSTRUCTION PHASE (per-unit loop)
- [ ] Functional Design — EXECUTE (per-unit)
- [ ] NFR Requirements — EXECUTE (per-unit)
- [ ] NFR Design — EXECUTE (per-unit)
- [ ] Infrastructure Design — SKIP
- [ ] Code Generation — EXECUTE (per-unit)
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations (placeholder)

## Current Status
- **Lifecycle Phase**: INCEPTION
- **Current Stage**: Units Generation (Part 1 Planning — 승인 대기)
- **Next Stage**: Units Generation Part 2 (Generation) → CONSTRUCTION
- **Status**: Application Design 승인 완료. unit-of-work-plan.md 생성, 병렬화 전략 포함(최대 4인 3-웨이브 계획). 사용자 승인 대기 중.
