# AI-DLC State Tracking

## Project Information
- **Project Name**: TRACE — 개발자 지식 인텔리전스 (작업명)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: Increment 1(TRACE 코어) CONSTRUCTION 완료 → **Increment 2(온보딩 맵) INCEPTION/Requirements Analysis 진행 중** (아래 "Increment 2" 섹션)

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

---

## Increment 2 — 프로젝트 온보딩 맵 (2026-09-09 착수, 브라운필드 적응형)
**목표**: TRACE 사용 신입 개발자가 낯선 프로젝트의 전체 흐름·파일 관계·함수 관계를 온보딩 관점에서 파악하도록 돕는 신규 기능. 사용자가 기능 확장(=B)을 선택 → 요구사항부터 재정의.

| 단계 | 상태 | 비고 |
|---|---|---|
| Requirements Analysis | [x] 완료 | 답변 확정(Q1=A,Q2=A,Q3=B,Q4=A,Q5=A) → requirements.md §4.10 FR-MAP-001~007 + §9 UOW-07 추가 |
| User Stories | [x] 완료 | P4 '뉴비' 페르소나 신설 + UOW-07 Epic 5개 스토리(US-07.1~5, Given/When/Then·추적성). 총 27스토리/7Epic |
| Application Design | [x] 완료 | C10 `map/` 신설(관계추출·Mermaid·내러티브·overview.md). onboarding-map-design.md + components/methods/dependency/unit-of-work 증분 반영. FR-MAP→메서드 1:1 |
| Units Generation | [x] 완료 (minimal) | 단일 UOW-07 확정. story-map(27스토리)·dependency 매트릭스에 UOW-07 반영. 순환 없음 |
| Construction — UOW-07 Functional Design | [~] 진행 예정 | 정적 추출기 파서 세부·overview.md YAML 스키마·PBT 속성 |
| Construction — UOW-07 Code Generation | [ ] 대기 | C10 map/ 구현 + C2/C3/C8/C1/C9 배선 + replay 픽스처 |
| Construction — Build and Test | [ ] 대기 | UOW-07 단위/통합/PBT + Hero 온보딩 E2E |

- **확정된 결정(답변)**: Q1=A 하이브리드(정적 단서+LLM 서술), Q2=A MCP 도구+CLI+`overview.md` 영속화, Q3=B 파일+함수 레벨, Q4=A Mermaid, Q5=A Java/Python 정적+LLM 폴백. → requirements.md §4.10 FR-MAP-001~007, §9 UOW-07 반영.

## Current Status
- **Lifecycle Phase**: INCEPTION (Increment 2) — Increment 1은 CONSTRUCTION 완료
- **Current Stage**: Increment 2 "온보딩 맵" — INCEPTION 전 단계 완료(Req·Stories·App Design·Units Gen) → **CONSTRUCTION UOW-07 착수(Functional Design)**
- **Next Stage**: UOW-07 Functional Design → Code Generation → Build and Test
- **완료**: UOW-0F ~ UOW-06 전 단위. 전체 62 테스트 통과. 설치된 `trace`/`trace-mcp` 명령이 저장소 밖에서도 동작(replay Hero E2E 검증). value_mismatch(전화번호 20 vs 10) 검출·영향분석·Change Plan 확인.
- **Status**: 8개 단위 코드 생성 완료. import 패키지 `trace`→`traceki` 개명(파이썬 stdlib `trace` 충돌 해소, 명령어명·로거명·`.trace/` 디렉터리는 유지). result/hero-run.txt 실행 전사 갱신.
- **핵심 Construction 결정**: LLMService는 (1) live Anthropic 다이렉트(sk-ant) + (2) bedrock(Amazon Bedrock, bearer 토큰) + (3) cache/replay 백엔드를 지원.
  데모 Hero 시나리오는 사전 캐시된 응답으로 API 키 없이 결정적 재현 가능(NFR-AI-004, NFR-REL-001).
- **후속 개선(2026-09-09, 사용자 요청 — Build and Test 이후)**:
  - LLM 백엔드에 **bedrock** 추가(AnthropicBedrock, Authorization: Bearer). config: AWS_BEARER_TOKEN_BEDROCK·TRACE_BEDROCK_MODEL·AWS_REGION. 테스트 격리(tests/conftest.py)로 실제 .env 오염 차단. 커밋 e81c16a.
  - **live 실증**: Amazon Bedrock 크로스리전 프로파일 `global.anthropic.claude-opus-4-8`(리전 ap-northeast-2)로 데모 실제 분석 성공. 계정 IAM 권한 문제로 us./apac. 리전 프로파일은 불가, global 프로파일만 호출됨.
  - **extract_claims 프롬프트 개선**: live Opus가 값 20/10을 한 claim으로 병합해 충돌 미검출 → "값이 다르면 값마다 별도 claim(병합 금지)" 규칙 추가. 재실행 시 value_mismatch(전화번호 10 vs 20) live 검출·Change Plan 충돌 인지 확인. result/hero-run-live-opus48.txt 저장. 전체 63 테스트 통과. 커밋 c6fa45d.
