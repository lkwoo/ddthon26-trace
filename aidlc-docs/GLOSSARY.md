# TRACE 용어표 (Glossary)

**대상 독자**: 이 문서와 `aidlc-docs/` 산출물을 읽는 평가자·후속 개발자.
**원칙**: 아래 약어는 **설계/프로세스 문서 내부 표기**다. TRACE **최종 사용자**가 보는 화면
(README·MCP 도구 응답·`Result.summary`)에는 약어를 노출하지 않고 평범한 문장으로 설명한다.

---

## 요구사항·규칙 라벨

| 약어 | 원어 | 뜻 | 예 |
|---|---|---|---|
| **FR** | Functional Requirement | 기능 요구사항 — 시스템이 "무엇을 해야 하는가" | FR-CONFLICT-001(충돌 검출) |
| **NFR** | Non-Functional Requirement | 비기능 요구사항 — 성능·보안·신뢰성·관측성 등 "얼마나 잘" | NFR-SEC-004(경로 검증) |
| **BR** | Business Rule | 비즈니스 규칙 — 이 프로젝트 설계 문서에서 도메인 검증·판정·불변식에 붙인 라벨(표준 약어 아님) | BR-ID-001(slug 생성) |
| **DoD** | Definition of Done | 완료 정의 — 해당 단위/시나리오가 "끝났다"고 볼 조건 | Hero 무편집 E2E 통과 |
| **PBT** | Property-Based Testing | 속성 기반 테스트 — 개별 입력이 아니라 "항상 성립할 성질"을 검증 | serialize→deserialize 동등 |

## AI-DLC 프로세스 용어

| 약어/용어 | 뜻 |
|---|---|
| **AI-DLC** | AI-assisted Development Life Cycle — 이 프로젝트가 따르는 단계형(Inception→Construction→Operations) 워크플로우 |
| **UOW** | Unit of Work — 개발 단위(서브모듈 경계). 예: UOW-0F(Foundation), UOW-01(스캐너) |
| **enabler 단위** | 직접 대응 사용자 스토리는 없으나 다른 단위를 뒷받침하는 기술 기반 단위(예: UOW-0F) |
| **Wave (웨이브)** | 병렬 개발 묶음. W0/W1/W2로 나눠 최대 4트랙 동시 진행 |
| **GATE** | 사용자 명시 승인 없이는 다음 단계로 넘어가지 않는 정지점 |

## TRACE 도메인 용어

| 용어 | 뜻 |
|---|---|
| **Feature** | 검출된 기능/능력 단위(자동 검출). 지식의 최상위 묶음 |
| **Claim** | Feature에 대한 원자적 주장. `subject·predicate·value` 삼항(예: `owner.telephone·max_length·20`) |
| **Evidence** | Claim을 뒷받침/반박하는 근거 조각(출처·위치·관계) |
| **Confidence** | 근거 일치도로 매긴 신뢰도(HIGH/MEDIUM/LOW) + 사유 |
| **Conflict** | 같은 주장에 값이 어긋나는 상황. P0 = `value_mismatch` |
| **Result envelope** | 모든 코어 함수가 반환하는 공통 봉투(summary·data·conflicts·impact·evidence·warnings·meta) |
| **Task Impact** | 자연어 작업을 지식에 비춰 Must/Likely/Review로 분류한 영향 분석 |
| **Hero 시나리오** | 데모의 대표 E2E 흐름(스캔→Feature→충돌 검출→작업 영향). 완성도 증거 앵커 |
| **`.trace/`** | 프로젝트 루트에 생성되는 지식 저장소 디렉터리(MD+YAML 지식 파일) |
| **MCP** | Model Context Protocol — TRACE가 Claude Code에 도구·리소스를 노출하는 프로토콜 |

## 확장(Extension) 관련

| 용어 | 뜻 |
|---|---|
| **Resiliency Baseline** | 부분 실패 허용·경고 노출·오류 계층 등 복원력 규칙(본 프로젝트 활성, Blocking) |
| **Property-Based Testing** | 위 PBT 확장(본 프로젝트 활성, Blocking) |
| **Security Baseline** | 보안 확장(본 프로젝트 미적용 — 단, NFR-SEC 요구사항 자체는 유효) |
