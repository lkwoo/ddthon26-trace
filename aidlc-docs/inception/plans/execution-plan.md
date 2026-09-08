# Execution Plan — TRACE

**단계**: INCEPTION / Workflow Planning
**작성일**: 2026-09-08
**프로젝트 유형**: Greenfield

## Detailed Analysis Summary

### Change Impact Assessment
- **User-facing changes**: Yes — 3 페르소나가 Claude Code(에이전트) 경유로 5개 MCP 도구와 상호작용
- **Structural changes**: Yes — 신규 시스템 아키텍처(MCP 서버 / 로컬 엔진 / AI 워크플로우 / 지식 저장) 정의 필요
- **Data model changes**: Yes — Feature / Claim / Evidence / Conflict / Impact 신규 데이터 모델
- **API changes**: Yes — 5개 MCP 도구 계약 + 리소스/프롬프트 (신규)
- **NFR impact**: Yes — 그라운딩·환각 처리·시크릿·로깅·시연 안정성 + PBT 전면·Resiliency 확장

### Risk Assessment
- **Risk Level**: Medium — 신규 greenfield PoC, 로컬 단일 프로세스라 롤백 쉬움. 다만 AI 워크플로우 신뢰성/시연 안정성이 핵심 불확실성
- **Rollback Complexity**: Easy — 로컬 프로세스, 상태는 파일(knowledge/) 기반
- **Testing Complexity**: Moderate — PBT 전면 적용, AI 출력 결정성/폴백 테스트 필요

## Workflow Visualization

```mermaid
flowchart TD
    Start(["User Request"])

    subgraph INCEPTION["INCEPTION PHASE"]
        WD["Workspace Detection<br/><b>COMPLETED</b>"]
        RE["Reverse Engineering<br/><b>SKIP (greenfield)</b>"]
        RA["Requirements Analysis<br/><b>COMPLETED</b>"]
        US["User Stories<br/><b>COMPLETED</b>"]
        WP["Workflow Planning<br/><b>COMPLETED</b>"]
        AD["Application Design<br/><b>EXECUTE</b>"]
        UG["Units Generation<br/><b>EXECUTE</b>"]
    end

    subgraph CONSTRUCTION["CONSTRUCTION PHASE"]
        FD["Functional Design<br/><b>EXECUTE (per-unit)</b>"]
        NFRA["NFR Requirements<br/><b>EXECUTE (per-unit)</b>"]
        NFRD["NFR Design<br/><b>EXECUTE (per-unit)</b>"]
        ID["Infrastructure Design<br/><b>SKIP</b>"]
        CG["Code Generation<br/><b>EXECUTE (per-unit)</b>"]
        BT["Build and Test<br/><b>EXECUTE</b>"]
    end

    subgraph OPERATIONS["OPERATIONS PHASE"]
        OPS["Operations<br/><b>PLACEHOLDER</b>"]
    end

    Start --> WD
    WD --> RA
    RA --> US
    US --> WP
    WP --> AD
    AD --> UG
    UG --> FD
    FD --> NFRA
    NFRA --> NFRD
    NFRD --> CG
    CG --> BT
    BT --> End(["Complete"])

    style WD fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RA fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style US fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style WP fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style CG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style BT fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style AD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style UG fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style FD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRA fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style RE fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style ID fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style OPS fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style INCEPTION fill:#BBDEFB,stroke:#1565C0,stroke-width:3px,color:#000
    style CONSTRUCTION fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px,color:#000
    style OPERATIONS fill:#FFF59D,stroke:#F57F17,stroke-width:3px,color:#000
    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000

    linkStyle default stroke:#333,stroke-width:2px
```

## Phases to Execute

### 🔵 INCEPTION PHASE
- [x] Workspace Detection (COMPLETED)
- [x] Reverse Engineering (SKIPPED — greenfield, 기존 코드 없음)
- [x] Requirements Analysis (COMPLETED)
- [x] User Stories (COMPLETED)
- [x] Execution Plan (IN PROGRESS)
- [ ] Application Design — **EXECUTE**
  - **Rationale**: 신규 컴포넌트 4계층(MCP 인터페이스/로컬 엔진/AI 워크플로우/지식 저장)과 코어 함수 인터페이스, 컴포넌트 의존성을 정의해야 함. NFR-CORE-001/002(코어·인터페이스 분리, 재사용) 충족의 출발점.
- [ ] Units Generation — **EXECUTE**
  - **Rationale**: 시스템이 UOW-01~06으로 자연 분해됨. 각 유닛 단위로 구성/코드 생성을 순차 진행하기 위해 필요.

### 🟢 CONSTRUCTION PHASE (per-unit loop, UOW별 반복)
- [ ] Functional Design — **EXECUTE (per-unit)**
  - **Rationale**: 신규 데이터 모델(Claim/Evidence/Conflict/Feature)과 복잡한 비즈니스 로직(정규화·값 비교·영향 분류). **PBT-01**(설계 시 테스트 속성 식별)은 이 단계에서 필수.
- [ ] NFR Requirements — **EXECUTE (per-unit)**
  - **Rationale**: 성능/시크릿/로깅/시연 안정성 NFR + 기술 스택 확정(파서 라이브러리, **Hypothesis(PBT-09)**). 확장 요구사항 반영.
- [ ] NFR Design — **EXECUTE (per-unit)**
  - **Rationale**: 그라운딩·환각 처리·폴백 패턴, Resiliency 확장 준수(대부분 인프라 룰 N/A 명시), 프롬프트 분리 설계.
- [ ] Infrastructure Design — **SKIP**
  - **Rationale**: 로컬 stdio 단일 프로세스 PoC. 클라우드 리소스·배포 인프라·멀티존/리전 없음(RTO/RPO=N/A, Q11=E). Resiliency 인프라 룰(RESILIENCY-08~13)은 N/A. 패키징·진입점은 Code Generation에서 처리. *필요 시 사용자가 포함 요청 가능.*
- [ ] Code Generation — **EXECUTE (ALWAYS, per-unit)**
  - **Rationale**: 실제 구현. PBT + 예제 테스트 동반 생성.
- [ ] Build and Test — **EXECUTE (ALWAYS)**
  - **Rationale**: 빌드·유닛/통합/PBT 실행·Hero E2E 검증·시연 스크린샷.

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Units 개요 (Units Generation 입력)

**UOW-00 데모 데이터셋 & 픽스처 (신설, 사용자 요청)** · UOW-01 스캐너/파서 · UOW-02 Feature/지식 · UOW-03 Claim/Evidence/Conflict · UOW-04 Task Impact · UOW-05 MCP 인터페이스 · UOW-06 통합/신뢰성/시연

### UOW-00 — 데모 데이터셋 & 픽스처 (신설)
- **분리 이유(사용자 요청)**: 데모 데이터셋은 분석의 **입력**이자 의도적 충돌을 심는 독립 산출물. 코드(엔진)와 분리하면 추적성·시연 안정성·재현성이 향상되고, 데이터셋 교체가 엔진에 영향 없음.
- **접근법(확정)**: **하이브리드** — Spring Petclinic REST에서 **Owner 관련 최소 조각만 발췌·경량화**하고, 그 위에 **합성 요구사항 문서(PDF 포함)**와 **의도적 충돌**을 얹는다.
- **핵심 산출물**:
  - `demo/` (또는 유사) 아래 경량 대상 프로젝트 — Owner 도메인 중심: 소스(`Owner*.java` 등), OpenAPI 명세, DB 스키마, 설정, 테스트
  - 의도적 충돌: 전화번호 max length **요구사항 20 vs OpenAPI/코드 10** (§18.3)
  - 합성 요구사항 PDF/문서 (교차소스 커버리지 ↑, PDF 파싱 P0 근거)
  - Hero Task 시연에 필요한 관련 자산 완비 (§18.4)
- **관련 요구사항**: FR-DEMO-001, §18(데모 데이터셋), FR-KNOWLEDGE-003(교차소스), FR-CONFLICT-001(value_mismatch), FR-PROJECT-002(PDF)
- **UOW-06과의 경계**: UOW-00은 **데이터셋/픽스처 자체**를 만든다. UOW-06은 이 데이터셋을 사용한 **턴키 시연 구성·스크린샷·신뢰성/폴백**을 담당한다.
- **NFR-SEC 주의**: 합성 문서/설정에 실제 시크릿·PII를 넣지 않는다(플레이스홀더 사용).

**권장 구현 순서(의존성 기준)**: **UOW-00** → UOW-01 → UOW-02 → UOW-03 → UOW-04 → UOW-05 → UOW-06
(데모 데이터셋이 있어야 스캐너/파서와 이후 파이프라인을 실제 자산으로 검증 가능 → UOW-00을 최우선. 이후 스캔/파싱→지식→Claim/Conflict→Impact→MCP 노출→통합·시연)

## Estimated Timeline
- **Total Phases (execute)**: INCEPTION 2(AD, UG) + CONSTRUCTION per-unit(FD/NFRA/NFRD/CG × **7 UOW**, UOW-00 포함) + Build&Test
- **Estimated Duration**: 2일 해커톤 PoC 범위. P0 우선, P1은 시간 허용 시.
- **참고**: UOW-00은 코드 생성보다 데이터셋 준비 성격이라 Functional/NFR 설계는 최소 깊이로 처리(픽스처 정의 위주).

## Success Criteria
- **Primary Goal**: Hero 시나리오("Owner 등록에 SMS 인증 추가")를 Claude Code에서 E2E로 시연 — 충돌 경고 + 근거 기반 Change Plan
- **Key Deliverables**: Python MCP 서버(5 도구+리소스), 로컬 엔진/AI 워크플로우, knowledge/features/*.md, 폴백 CLI, README 턴키 구성, `result/` 스크린샷
- **Quality Gates**: DoD(§20) 충족, PBT+예제 테스트 통과, 하드코딩 시크릿 없음, 코어/인터페이스 분리, Hero 반복 가능
