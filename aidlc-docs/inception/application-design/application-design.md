# TRACE — 애플리케이션 설계 (통합 문서)

**단계**: INCEPTION / Application Design
**작성일**: 2026-09-08
**상세 문서**: `components.md` · `component-methods.md` · `services.md` · `component-dependency.md` · **`onboarding-map-design.md`**(Increment 2)

---

## 1. 설계 개요

TRACE는 **로컬 stdio MCP 서버**로, 흩어진 개발 자산을 기능 중심·근거 기반 지식으로 재구성해 AI 코딩 에이전트(Claude Code)에 노출한다. 설계는 요구사항 §4(4계층)·§13(코어 인터페이스)를 따르며, **코어 로직과 인터페이스를 엄격히 분리**(NFR-CORE-001/002)한다.

### 확정 설계 결정 (Application Design Q1~Q5)
| # | 결정 |
|---|---|
| Q1 | `trace/` 하위 계층별 서브모듈(C1~C9) |
| Q2 | 코어=순수 서비스, MCP/CLI=얇은 어댑터 |
| Q3 | AI는 명시적 순차 파이프라인(step별 구조화 출력·부분실패 허용) |
| Q4 | 공통 result envelope (summary→conflicts→impact→evidence→warnings→meta) |
| Q5 | 지식/캐시는 대상 밖 `.trace/`(대상 저장소 비오염) |

## 2. 컴포넌트 (요약)

| ID | 모듈 | 책임 | UOW |
|---|---|---|---|
| C1 | `mcp_server/` | MCP 도구/리소스/프롬프트 노출(얇은 어댑터), stdio | UOW-05 |
| C2 | `engine/` | 스캔·파싱·분류, 코어 함수·오케스트레이션 진입 | UOW-01 |
| C3 | `workflow/` | AI step(Feature/Claim/Evidence/Confidence/지식/작업분석) | UOW-02,03,04 |
| C4 | `knowledge/` | 도메인 모델 + MD/YAML 저장·리소스 | UOW-02,03 |
| C5 | `conflict/` | value_mismatch 등 충돌 검출 | UOW-03 |
| C6 | `impact/` | Task Impact + Change Plan | UOW-04 |
| C7 | `config/` | 제외규칙·시크릿(env)·상수 | 전역 |
| C8 | `prompts/` | 프롬프트 템플릿(코드 분리) | UOW-02,03,04 |
| C9 | `cli/` | 폴백 CLI(얇은 어댑터) | UOW-06 |
| (data) | `demo/` | 데모 데이터셋·픽스처 | UOW-00 |
| **C10** *(Inc.2)* | `map/` | **온보딩 맵 빌더**(관계 추출·Mermaid·내러티브·overview.md) | **UOW-07** |

## 3. 서비스 (오케스트레이션)
- **S1 AnalysisService** = `analyze_project` 순차 파이프라인 (스캔→파싱→Feature→Claim/Evidence→Confidence→Conflict→지식→영속화, 캐시)
- **S2 KnowledgeQueryService** = `list_features`/`get_feature_knowledge`/`get_conflicts` (LLM 없이 조회)
- **S3 ImpactService** = `analyze_task_impact` (지식 그라운딩 → Must/Likely/Review → Change Plan)
- **S4 LLMService** = Claude 접근·구조화 검증·재시도·폴백 (C3 내부 캡슐화)

어댑터 C1(MCP)·C9(CLI)는 S1~S3를 **동일하게 재사용**한다(NFR-CORE-002).

## 4. 핵심 데이터 흐름
- **분석**: 파일 → assets → (AI) claims/evidence → conflicts → FeatureKnowledge(.md) → Result
- **영향**: task + 지식 컨텍스트 → 관련 충돌 경고 → Must/Likely/Review → Change Plan → Result
- 상세 다이어그램: `component-dependency.md`

## 5. 아키텍처 원칙 & NFR 매핑
- **코어/인터페이스 분리** (NFR-CORE-001): AI 로직은 C3에만, 어댑터는 호출만
- **재사용** (NFR-CORE-002): 서비스가 MCP·CLI·(향후)IDE/CI에 공유
- **모듈 분리** (NFR-MAINT-001) / **프롬프트 분리** (NFR-MAINT-002)
- **로컬 우선** (NFR-LOCAL-001): 파일 접근 C2/C4 국한, LLM은 명시 전송분만
- **그라운딩·구조화·불확실성** (NFR-AI-001/002/003): C3 step 계약
- **보안** (NFR-SEC-001/004/005): env 시크릿, 경로 검증, stdio 비노출
- **점진적 노출** (NFR-MCP-UX-002): 공통 result envelope 순서
- **Resiliency 확장**: 로컬 단일 프로세스 → 인프라 룰 대부분 N/A, 관측성=로깅(NFR-LOG-001). 상세 컴플라이언스는 NFR Design.
- **PBT 확장**: 순수 로직(Claim 정규화·YAML 직렬화·값 비교)에 속성 테스트 적합 — Functional Design에서 PBT-01 속성 식별.

## 6. 다음 단계 (Construction 이연 사항)
- 데이터 모델 상세 필드·검증 규칙 (Functional Design)
- 정확한 파서 라이브러리·YAML 스키마·Confidence 계산식 (NFR Requirements / Functional Design)
- 프롬프트 실제 내용·구조화 스키마 (Code Generation)
- PBT 프레임워크(Hypothesis) 및 속성 목록 (NFR Requirements / Functional Design)
