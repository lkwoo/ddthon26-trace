# AI-DLC State Tracking

## Project Information
- **Project Name**: TRACE — 개발자 지식 인텔리전스 (작업명)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: CONSTRUCTION - Per-Unit Loop 완료 (UOW-0F ~ UOW-06) → Build and Test

## Workspace State
- **Existing Code**: No
- **Programming Languages**: None yet (미결정 — 요구사항 §23 참조)
- **Build System**: None yet
- **Project Structure**: Empty (문서만 존재)
- **Reverse Engineering Needed**: No
- **Workspace Root**: /home/wsl/aidlc-workshop/ddthon26-trace

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
- **유닛 순서(위상)**: UOW-0F(Foundation, 신설) → 00(데모) → 01 → 02 → 03 → 04 → 05 → 06
- **UOW-00 신설(사용자 요청)**: 데모 데이터셋 & 픽스처를 별도 유닛으로 분리. 접근법=하이브리드(Petclinic Owner 조각 발췌 + 합성 PDF·의도적 충돌).
- **UOW-0F 신설(Units Generation Q1=A)**: 공유 계약(C4 모델·Result envelope·config·프롬프트 로더·LLM 스켈레톤) 단위. 병렬화 이음새(enabler, 직접 스토리 없음).
- **병렬 개발 계획(사용자 제약: 최대 4인, Units Generation Q3=A)**: 3-웨이브. W0=[0F ∥ 00], W1=[01 ∥ (02→03) ∥ 05 ∥ 04선작업] 최대 4트랙, W2=[04 마감 → 06 수렴]. 밀결합(02↔03)·수렴(04·06)은 병렬화 안 함.

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [ ] Reverse Engineering (SKIP — greenfield)
- [x] Requirements Analysis
- [x] User Stories
- [x] Workflow Planning
- [x] Application Design — EXECUTE
- [x] Units Generation — EXECUTE (Part 1 계획 + Part 2 산출물 완료, 승인됨 — 사용자 위임)

### 🟢 CONSTRUCTION PHASE (per-unit loop)
진행 순서(위상): 0F → 00 → 01 → 02 → 03 → 04 → 05 → 06

| 단위 | Functional Design | NFR Req/Design | Code Generation |
|---|---|---|---|
| UOW-0F Foundation | [x] | [x] | [x] |
| UOW-00 데모 | [x] | N/A | [x] (데이터셋+replay 픽스처 4종 완료: identify/generate/extract/analyze_task) |
| UOW-01 스캐너 | [x] | [x] | [x] |
| UOW-02 Feature/Knowledge | [x] | N/A | [x] |
| UOW-03 Claims/Conflict | [x] | N/A | [x] |
| UOW-04 Task Impact | [x] | N/A | [x] |
| UOW-05 MCP 어댑터 | [x] | N/A | [x] |
| UOW-06 통합·시연 | [x] | N/A | [x] (폴백 CLI + Hero E2E + 시크릿 위생 + README; import 패키지 trace→traceki 개명으로 stdlib 충돌 해소) |

- [ ] Infrastructure Design — SKIP (로컬 stdio 단일 프로세스)
- [x] Build and Test — EXECUTE 완료 (build/unit/integration/performance/summary 지침 5종, 62 테스트 통과)

### 🟡 OPERATIONS PHASE
- [ ] Operations (placeholder)

## Current Status
- **Lifecycle Phase**: CONSTRUCTION
- **Current Stage**: CONSTRUCTION 완료 (Per-Unit Loop 8개 단위 + Build and Test)
- **Next Stage**: OPERATIONS (placeholder — 향후 배포·모니터링 확장)
- **완료**: UOW-0F ~ UOW-06 전 단위. 전체 62 테스트 통과. 설치된 `trace`/`trace-mcp` 명령이 저장소 밖에서도 동작(replay Hero E2E 검증). value_mismatch(전화번호 20 vs 10) 검출·영향분석·Change Plan 확인.
- **Status**: 8개 단위 코드 생성 완료. import 패키지 `trace`→`traceki` 개명(파이썬 stdlib `trace` 충돌 해소, 명령어명·로거명·`.trace/` 디렉터리는 유지). result/hero-run.txt 실행 전사 갱신.
- **핵심 Construction 결정**: LLMService는 (1) live Anthropic Claude 백엔드 + (2) cache/replay 백엔드를 지원.
  데모 Hero 시나리오는 사전 캐시된 응답으로 API 키 없이 결정적 재현 가능(NFR-AI-004, NFR-REL-001).
