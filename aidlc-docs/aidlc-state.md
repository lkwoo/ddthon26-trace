# AI-DLC State Tracking

## Project Information
- **Project Name**: TRACE — 개발자 지식 인텔리전스 (작업명)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: CONSTRUCTION - Functional Design (UOW-00 데모 데이터셋)

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
- [x] Units Generation — EXECUTE (Part 1+2 완료, 2026-09-09 승인)

### 🟢 CONSTRUCTION PHASE (per-unit loop)
- [ ] Functional Design — EXECUTE (per-unit) — ✅ UOW-0F/00/01/02/03 / ✅ UOW-04 산출물 생성(2026-09-09, GATE)
- [ ] NFR Requirements — EXECUTE (per-unit) — ✅ UOW-0F/00/01/02/03/04 완료 / ✅ UOW-05 산출물 생성(2026-09-09, GATE)
- [ ] NFR Design — EXECUTE (per-unit) — ✅ UOW-0F / UOW-00 SKIP / ✅ UOW-01/02/03/04 완료 / ✅ UOW-05 산출물 생성(2026-09-09, GATE)
- [ ] Infrastructure Design — SKIP
- [x] Code Generation — EXECUTE (per-unit) — ✅ UOW-0F/00/01/02/03/04/05 완료 / ✅ UOW-06 완료·승인대기(2026-09-09, 145 pass·3 skip)
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations (placeholder)

## Current Status
- **Lifecycle Phase**: CONSTRUCTION
- **Current Stage**: Code Generation — UOW-06 (통합·시연), Part 2 구현 완료 — 승인 대기 (GATE). per-unit loop **전체 완료**.
- **Next Stage**: UOW-06 Code Generation 승인 → Build and Test(ALWAYS) → Construction 완료
- **Status(코드 UOW-06)**: trace/cli(C9 폴백)·demo/run_demo.py(결정적 Hero 하니스 무키)·tests/test_hero_e2e.py·README(.mcp.json)·result/{usage-walkthrough,hero-demo-output.txt,README}. pytest 145 pass·3 skip. Hero E2E 3충돌+영향+Change Plan 재현. 보안 위생 OK. 스크린샷: GUI는 키+Claude Code 필요 → CLI 실행증거+캡처가이드 대체.
- **스크린샷 한계**: GUI 캡처는 API 키+Claude Code 필요 → 결정적 CLI/데모 텍스트 실행증거(result/hero-demo-output.txt) + GUI 캡처 가이드로 대체.
- **Status(코드 UOW-05)**: mcp_server/{serialize,server,__main__} + engine list_features/get_feature_knowledge + error_to_result 견고화. pytest 142 pass·3 skip, 신규 mypy-clean. build_server 5도구=코어 1:1+trace:// 리소스+P1 프롬프트, 핸들러 오류 격리 무크래시, 직렬화 핵심우선. mcp>=2.0(설치 2.x MCPServer 검증), mcp 지연임포트. 코어 5함수 전부 MCP 노출 완료. (사전존재 llm/client.py mypy 경고 1건은 범위 밖 유지)
- **Status(NFR-Design UOW-05)**: build_server 팩토리+데코레이터·얇은 핸들러 오류 격리·_root(cwd/env)·serialize_result 핵심우선·코어 래퍼 list_features/get_feature_knowledge·trace:// 리소스·P1 프롬프트. mcp_server/{__main__,server,serialize}, pyproject mcp>=2.0, mcp 지연임포트. 확장 Resiliency Compliant·PBT N/A.
- **Status(NFR UOW-05)**: Q1~Q4=A. mcp>=2.0 상향(설치 2.x MCPServer), 5도구=코어 1:1(타입힌트 스키마)·stdio·cwd+TRACE_PROJECT_ROOT·오류 격리 무크래시·직렬화 핵심우선·trace:// 리소스·P1 프롬프트. 코어 래퍼 list_features/get_feature_knowledge 추가 예정. mcp 지연임포트. 확장 Resiliency Compliant·PBT N/A.
- **Status(코드 UOW-04)**: models/impact + impact/{context,analyze} + engine.analyze_task_impact + analyze_task 프롬프트. pytest 131 pass·3 skip(옵트인), 신규 mypy-clean. 지식 그라운딩·허구 path/근거부족 review 강등·기존 conflicts related_conflicts 노출(LLM 실패에도 유지)·순서형 Change Plan·소스 자동수정 없음. to_impact_out 정렬 완전 순서화(PBT-04-C). 코어 5함수 중 analyze_project/get_conflicts/analyze_task_impact 완비(scan_project·list_features 잔여는 UOW-05 배선).
- **Status(NFR-Design UOW-04)**: nfr-design-patterns(P1 컨텍스트/랭킹·P2 LLM step 상위강등·P3 매핑/강등 순수함수·P4 충돌 독립노출·P5 조립·P6 프롬프트·P7 테스트 5종·P8 결정성/보안), logical-components(models/impact·impact/{context,analyze}·engine analyze_task_impact). 신규 의존성 없음. 확장 Resiliency·PBT Compliant.
- **Status(NFR UOW-04)**: Q1=A,B,C,D/Q2=A/Q3=A. PBT-04-A~D(매핑 건전성·근거부족 강등·정렬 결정성·related_conflicts 정합), FakeLLM+llm_integration 옵트인, 발췌 4000 상속·focus top-N=3. 순수함수(build_context/to_impact_out/rank), 저장지식 재사용(무재스캔). 확장 Resiliency·PBT Compliant. 신규 의존성 없음.
- **Status(FD UOW-04)**: Q1~Q5=A. models/impact.py(ImpactCandidate/TaskImpactResult) + impact/{context,analyze} + engine/analyze.analyze_task_impact + analyze_task 프롬프트. 지식 그라운딩(저장 FeatureKnowledge/Evidence 컨텍스트)·3범주 분류+근거참조·허구path review 강등·근거부족 LOW·기존 conflicts related_conflicts 노출(P1)·순서형 Change Plan(충돌해소 우선)·소스 자동수정 없음. 기존 ImpactOut/ImpactItem/EvidenceRef(UOW-0F) 재사용.
- **Status(코드 UOW-03)**: conflict/{detect,summarize} + workflow/claims + engine/analyze + models/extraction + extract_claims 프롬프트. `pytest` 113 pass·2 skip(옵트인), 신규 mypy-clean. 결정적 충돌검출(구조 비교, RAG 차별점)·3유형 전결정 분류·근거일치 Confidence(비-LLM)·캐시-완본 스테이지(2회차 LLM 0콜)·Feature 격리 강등. PBT-03-B가 동일 claim_key 정렬 비결정 결함 검출→정렬키 보강. analyze_project/get_conflicts 코어 공개(루트=명시 인자, UOW-06 주입).
- **Status(NFR-Design UOW-03)**: nfr-design-patterns(P1 원자추출·P2 Feature격리강등·P3 비-LLM 결정적 코어[구조적 충돌비교]·P4 유형분류 국소화+value_mismatch 폴백·P5 완본화·캐시-완본 스테이지·P6 조회·P7 프롬프트·P8 테스트 5종·P9 결정성/보안), logical-components(models/extraction·workflow/claims·conflict/{detect,summarize}·engine/analyze·프롬프트·테스트). ConflictType 2개 추가(하위호환), 신규 런타임 의존성 없음. 확장 Resiliency·PBT Compliant.
- **Status(코드)**: UOW-02 코드 생성 완료 — models/feature_candidate + knowledge/{ids,store,cache} + workflow/{catalog,features} + 프롬프트 2종. `pytest` 90 passed·1 skipped(옵트인 llm_integration), 신규 모듈 mypy-clean. FakeLLM 실증: demo/ 식별→지식셸 저장, 2회차 캐시 히트(LLM 0콜). Q2=A 셸(claims/evidence/conflicts=[], UOW-03 보강). build_knowledge가 前반부 재사용 단위.
- **Status(NFR)**: NFR Design 완료 — nfr-design-patterns(P1 카탈로그·P2 구조화 LLM 강등·P3 id 안전화·P4 저장소·P5 콘텐츠해시 캐시·P6 build_knowledge·P7 프롬프트·P8 테스트 배치·P9 결정성/보안), logical-components(models/feature_candidate·workflow/{catalog,features}·knowledge/{ids,store,cache}·프롬프트 2종·테스트 5종·llm_integration 마커). 신규 런타임 의존성 없음.
- **Status**: UOW-02 Functional Design 완료 — Q1=B(식별상한)/Q2=A(지식 셸)/Q3=A(자산 카탈로그)/Q4=A(콘텐츠해시 캐시)/Q5=A(.trace 프로젝트 루트). 산출물 3종: FeatureCandidate·저장소(KnowledgeStore)·캐시(compute_assets_hash/AnalysisCache) 계약, BR-IDF/KN/STORE/CACHE/FAIL/DET/SEC 규칙, workflow/·knowledge/ 배치·식별/지식/캐시 알고리즘. Claim/Evidence/Conflict는 UOW-03.
