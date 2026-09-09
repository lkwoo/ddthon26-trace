# TRACE — 요구사항 (AI-DLC Requirements Artifact)

**단계**: INCEPTION / Requirements Analysis
**깊이(Depth)**: Comprehensive
**작성일**: 2026-09-08
**원천 문서**: `requirments/trace-requirements.md` (사용자 제공, 상세 요구사항 — 이하 "원천 요구사항")
**평가 기준**: `requirments/assessment.md`

> 이 문서는 원천 요구사항을 AI-DLC 워크플로우로 소화한 산출물이다. 원천 요구사항의 FR/NFR ID를 그대로 계승하며, Requirements Analysis 단계에서 **확정된 결정(Q1~Q11)** 을 반영해 미해결 항목(§23)을 닫는다.

---

## 1. Intent 분석 요약

| 항목 | 값 |
|---|---|
| **User Request** | requirments 경로 요구사항을 확인하고 AI-DLC 워크플로우로 TRACE를 개발 |
| **Request Type** | New Project (greenfield) |
| **Clarity** | 명확 — 상세 요구사항 문서 제공 |
| **Scope** | System-wide (MCP 서버 + 로컬 엔진 + AI 워크플로우 + 지식 저장) |
| **Complexity** | Complex |
| **Depth 결정** | Comprehensive |

**제품 한 줄 정의**: 흩어진 개발 자산(요구사항·API 명세·소스·DB·설정·테스트)을 **기능(Feature) 중심·근거 기반 지식**으로 재구성하고, 이를 **로컬 MCP 서버**로 AI 코딩 에이전트(Claude Code)에 노출해 **구현 착수 직전에 충돌·영향 범위를 근거와 함께** 알려주는 개발자 지식 인텔리전스 시스템.

**핵심 구조적 차별**: RAG/위키는 *'비슷한 것'* 을 찾고, TRACE는 정규화된 Claim↔Evidence 비교로 *'어긋난 것(value_mismatch)'* 을 1급 산출물로 검출한다. (원천 §1.3)

---

## 2. 대상 사용자 & Hero 시나리오

세 사용자 모두 **Claude Code 안에서** TRACE MCP 도구를 통해 상호작용한다. (원천 §3)

- **개발자 (Understand)** — "어디를 바꿔야 하지?"
- **유지보수자 (Maintain)** — "왜 이 문제가 생겼고 또 무엇을 고쳐야 하지?"
- **기획자/PM (Plan Change)** — "이 요구사항이 바뀌면 영향은 어디까지 번지지?"

**Hero 시나리오** (원천 부록 B): 개발자가 Claude Code에서 낯선 시스템 변경을 시작 → `analyze_project` → `get_feature_knowledge` → `get_conflicts`(문서/구현 충돌 경고) → `"Add SMS verification to Owner registration"` 입력 → `analyze_task_impact` → Must/Likely/Review 분류 + 기존 충돌 경고 → 근거 기반 Change Plan. **핵심: 에이전트가 코드를 짜기 전에 TRACE에게 물어 충돌을 경고받는다.**

---

## 3. Requirements Analysis에서 확정된 결정 (원천 §23 종결)

| # | 미해결 항목 | 확정 결정 |
|---|---|---|
| Q1 | 구현 언어/SDK | **Python + 공식 Python MCP SDK (`mcp`)** |
| Q2 | LLM 제공자/모델 | **Anthropic Claude** (예: Claude Sonnet 5), API 키는 환경변수 |
| Q3 | 문서 파서 범위 | Markdown/텍스트·OpenAPI(YAML/JSON)·SQL·설정·소스·테스트 + **PDF는 P0**; DOCX/PPTX는 P1 |
| Q4 | Feature 검출 | **완전 자동** (AI가 자산에서 Feature 식별) |
| Q5 | 시연 폴백 | **분석 결과 캐시 + 얇은 폴백 CLI 둘 다 구현** (P1) |
| Q6 | 데모 데이터셋 | **Spring Petclinic REST(선별 부분집합) + 의도적 충돌 심은 합성 문서** |
| Q7 | 명칭 | **TRACE** 확정 |
| Q11 | RTO/RPO·DR | **E: N/A** — 로컬 단일 프로세스로 충분, cross-region DR 불필요 |

**미결로 남기는 세부(Construction에서 확정)**: 정확한 파서 라이브러리 선택, 정확한 YAML 스키마, Confidence 계산 정책 세부. (원천 §23-4,6,7 — Application/Functional Design 단계에서 확정)

---

## 4. 기능 요구사항 (Functional Requirements)

원천 요구사항의 FR ID를 계승한다. 우선순위(P0/P1/P2)와 확정 결정을 병기한다.

### 4.1 프로젝트 입력 (§5)
- **FR-PROJECT-001** (P0) 로컬 프로젝트 로딩 — MCP 설정의 `--project` 경로 또는 `analyze_project(path)` 인자. 유효/무효 경로 처리, 로드 요약 반환.
- **FR-PROJECT-002** (P0) 자산 탐색·분류 — 소스/MD·텍스트/**PDF(P0)**/OpenAPI/SQL/설정/테스트. (DOCX·PPTX는 P1)
- **FR-PROJECT-003** (P0) 제외 규칙 — `.git`, `node_modules`, `build`, `dist`, `target`, 바이너리, IDE 메타 등. 설정/중앙 상수로 구성 가능.

### 4.2 프로젝트 분석 (§6)
- **FR-ANALYSIS-001** (P0) `analyze_project` — 스캔→파싱→추출→Feature 식별→Claim·Evidence→Conflict→지식 생성→영속화→요약.
- **FR-ANALYSIS-002** (P1) 진행 가시성 — 고수준 단계 로그(내부 CoT 비노출).
- **FR-ANALYSIS-003** (P0) 결함 허용 — 한 파일 파싱 실패가 전체를 중단시키지 않음. 경고와 함께 완료.

### 4.3 기능 중심 지식 (§7)
- **FR-KNOWLEDGE-001** (P0) Feature 자동 검출 — 최소 1개 Hero Feature 정확 식별 + 교차소스 근거.
- **FR-KNOWLEDGE-002** (P0) Feature Knowledge 뷰 — 개요/비즈니스 규칙/코드/API/DB/설정/테스트/충돌/근거/의존성.
- **FR-KNOWLEDGE-003** (P0) 교차소스 연결 — Hero Feature는 최소 3개 산출물 범주 연관.

### 4.4 Claim / Evidence / Confidence / Conflict (§8)
- **FR-CLAIM-001** (P0) 정규화 원자 Claim 추출 (`subject + predicate + value`).
- **FR-EVIDENCE-001** (P0) Evidence 연관 — 소스 경로/유형/위치/추출값/관계(direct·supporting·related·contradicting).
- **FR-CONFIDENCE-001** (P1) Confidence(HIGH/MEDIUM/LOW) — LLM 자기확신이 아닌 **근거 일치도** 기반.
- **FR-CONFLICT-001** (P0) 값 불일치(`value_mismatch`) 검출. (다른 conflict 유형은 P1)

### 4.5 지식 저장 (§9)
- **FR-STORAGE-001** (P0) `knowledge/features/<id>.md` — YAML Front Matter(구조화) + Markdown(사람용). 단일 진실원 유지.
- **FR-STORAGE-002** (P0) 생성 지식을 MCP 리소스로 노출.

### 4.6 충돌 결과 (§10)
- **FR-CONFLICT-OUT-001** (P0) 충돌 수를 구조화 필드로 제공.
- **FR-CONFLICT-OUT-002** (P0) 각 상충 값의 근거 소스 파일 참조 제공.

### 4.7 Task Impact Analysis (§11)
- **FR-IMPACT-001** (P0) `analyze_task_impact(task, feature_id?)` — 자연어 변경 요청 입력.
- **FR-IMPACT-002** (P0) 기존 Feature Knowledge·Evidence를 컨텍스트로 사용(일반 LLM 프롬프트 단독 금지).
- **FR-IMPACT-003** (P0) 영향 분류 Must Change / Likely Change / Review + 이유.
- **FR-IMPACT-004** (P1) 충돌 인지 영향 분석 — 관련 기존 충돌을 변경 권고 전 강조.
- **FR-IMPACT-005** (P0) 근거 기반 권고 — 각 파일/컴포넌트에 이유·근거 참조.
- **FR-IMPACT-006** (P0) 순서형 Change Plan (자문용, 소스 자동수정 없음).

### 4.8 MCP 인터페이스 (§12)
- **FR-MCP-001** (P0) 도구 노출: `analyze_project`, `list_features`, `get_feature_knowledge`, `get_conflicts`, `analyze_task_impact` — 명확한 입력 스키마 + 구조화(JSON) 결과.
- **FR-MCP-002** (P0) `knowledge/features/*.md`를 MCP 리소스로 노출.
- **FR-MCP-003** (P1) 구현 전 검토 MCP 프롬프트 템플릿.
- **FR-MCP-004** (P0) **stdio 전송**, 기준 클라이언트 **Claude Code**, README에 복붙 설정 스니펫 + 예제 프롬프트.

### 4.9 시연 (§18)
- **FR-DEMO-001** (P0) Claude Code 턴키 시연 구성 + **`result/` 또는 `screenshots/`에 시연 스크린샷 필수**.
- **FR-DEMO-002** (P1) 동일 코어 함수를 호출하는 얇은 폴백 CLI (Q5 확정에 따라 구현).

### 4.10 프로젝트 온보딩 맵 (Increment 2 — 신입 개발자 온보딩)
**목표**: TRACE를 쓰는 신입 개발자가 낯선 프로젝트에 투입됐을 때, 전체 흐름·파일 간 관계·함수 간 관계를 온보딩 관점에서 파악하도록 돕는다. 아래 결정은 onboarding-map-questions.md 답변(Q1=A 하이브리드, Q2=A 도구+CLI+영속화, Q3=B 파일+함수 레벨, Q4=A Mermaid, Q5=A 데모중심+LLM폴백)에서 도출.

- **FR-MAP-001** (P0) **온보딩 맵 생성** — `generate_onboarding_map(path, feature_id?)`. 스캔·파싱으로 이미 수집된 자산(UOW-01) 위에서 진입점·파일/모듈 의존·핵심 경로 함수 호출 관계를 추출하고, "여기서 시작하세요" 온보딩 내러티브를 포함한 프로젝트 맵을 생성한다.
- **FR-MAP-002** (P0) **관계 추출 = 하이브리드** (Q1=A) — 정적 단서(import/require, 함수 호출·정의)를 **가볍게 정적 추출**해 결정적 뼈대를 만들고, **LLM이 근거(Evidence)와 함께 관계·흐름을 서술**한다. 기존 Claim↔Evidence 근거기반 철학·인프라(파서/스캐너/LLMService) 재사용. 일반 LLM 단독 추론 금지(NFR-AI-002 준수).
- **FR-MAP-003** (P0) **맵 구성 범위 = 파일 + 함수 레벨** (Q3=B) — (a) 진입점 목록, (b) 파일/모듈 의존 그래프, (c) Feature→파일 매핑, (d) 핵심 경로의 **함수 간 호출 관계**(예: 요청 핸들러→서비스→저장), (e) 온보딩 내러티브.
- **FR-MAP-004** (P0) **정적 추출 언어 범위 = 데모 중심 + LLM 폴백** (Q5=A) — Java·Python의 import·호출 단서를 정적 추출하고, 그 외 언어는 LLM 서술로 폴백한다. 데모 Hero(Java Petclinic)·TRACE 자체(Python)를 확실히 커버하면서 범용성 유지. 결함 허용: 정적 추출 실패 파일은 경고 후 LLM 폴백으로 완료(FR-ANALYSIS-003과 동일 원칙).
- **FR-MAP-005** (P0) **시각화 = Mermaid** (Q4=A) — 파일/모듈 의존 그래프(`graph`/`flowchart`)와 핵심 흐름 시퀀스(`sequenceDiagram`)를 Mermaid로 산출. Markdown 뷰어·GitHub에서 바로 렌더. content-validation.md의 Mermaid 문법 검증 필수.
- **FR-MAP-006** (P0) **산출물 소비 형태 = 도구+CLI+영속화** (Q2=A) — 새 MCP 도구(예: `generate_onboarding_map`)와 폴백 CLI 서브커맨드(예: `trace map`)로 조회하고, 동시에 `.trace/knowledge/overview.md`(Mermaid 포함)로 영속화. 기존 analyze/conflicts/task 도구·CLI 패턴과 정합.
- **FR-MAP-007** (P1) **근거 인용** — 맵의 각 관계·흐름 서술은 실제 자산(파일 경로/위치)을 Evidence로 인용한다(NFR-AI-002 확장). 근거 부족 관계는 LOW/Insufficient evidence로 표기(NFR-AI-003).

---

## 5. 비기능 요구사항 (Non-Functional Requirements)

- **NFR-LOCAL-001** (P0) 로컬 파일 직접 접근(로컬 엔진 경유).
- **NFR-CORE-001 / -002** (P0) 코어/인터페이스 분리, 코어 재사용(MCP·CLI·향후 IDE/CI 공유).
- **NFR-AI-001** (P0) 기계 판독(JSON/YAML) 구조화 출력.
- **NFR-AI-002** (P0) 근거 그라운딩 — Claim/Conflict/Impact는 실제 자산 참조.
- **NFR-AI-003** (P0) 환각 처리 — 근거 부족 시 Review/LOW/Insufficient evidence로 표기.
- **NFR-AI-004** (P1) 시연 안정성 — 안정·반복 가능 출력, 캐시 폴백(Q5).
- **NFR-PERF-001~003** — 소규모 데모 저장소 최적화, 진행 상태 전달, 반복 조회 시 불필요 LLM 호출 없음(캐시).
- **NFR-REL-001 / -002** (P0) Hero 시나리오 수동편집 없이 E2E 반복 가능, 실패 시 사람이 읽을 오류 + 진단 로그.
- **NFR-MAINT-001 / -002** — 모듈 분리(MCP 인터페이스/스캔·파싱/AI 워크플로우/지식 모델·저장/충돌·영향/설정), 프롬프트는 코드와 분리 저장.
- **NFR-LOG-001** — 스캔·파싱실패·AI실패·지식생성·충돌수·영향분석 로깅, 시크릿 비노출.
- **NFR-MCP-UX-001~003** — 설명 가능성(근거 포함), 점진적 노출(Feature→Conflict→Impact→Evidence), 시연 명료성(README로 ~30초 재현).

### 5.1 보안 요구사항 (원천 §16 — Security 확장 미적용이나 P0 요구사항으로 유효)
- **NFR-SEC-001** (P0) 하드코딩 시크릿 금지 — API 키는 환경변수/로컬 설정.
- **NFR-SEC-002** (P0) 로컬 우선 처리 — 원시 파일은 LLM에 명시 전송분 외 로컬 유지.
- **NFR-SEC-003** (P1) 향후 시크릿/PII 필터·민감파일 제외·사설 엔드포인트 삽입 지점.
- **NFR-SEC-004** (P0) 경로 검증 — 분석 전 존재·디렉터리 확인.
- **NFR-SEC-005** (P0) 로컬 stdio 전송, 결과·로그에 시크릿 비노출.

---

## 6. 확장(Extension) 구성 및 적용 방침

| 확장 | 적용 | 요구사항에의 영향 |
|---|---|---|
| **Security Baseline** | ❌ 미적용 (Q8=B) | 확장 blocking 룰은 미적용. 단 원천 §16 NFR-SEC-*는 위 5.1대로 유효. |
| **Resiliency Baseline** | ✅ 적용 (Q9=A) | RESILIENCY-02 RTO/RPO = **N/A(E)** 확정. 로컬 stdio 단일 프로세스 PoC이므로 멀티존/멀티리전/DR/백업/오토스케일 등 인프라성 룰(RESILIENCY-08~13)은 대부분 **N/A** 전망. 관측성 최소선(RESILIENCY-05 로깅)은 NFR-LOG-001로 충족. RESILIENCY-03/04/14/15(변경관리·배포·DR테스트·인시던트)는 NFR Design 단계에서 사용자 결정. |
| **Property-Based Testing** | ✅ 적용 (Q10=A, 전면) | PBT-01(설계 시 속성 식별)~PBT-10 전면 blocking. TRACE는 Claim 정규화·YAML 직렬화·값 비교(Conflict) 등 **속성 테스트에 적합한 순수 로직**이 많아 실질 가치 높음. 프레임워크: **Hypothesis**(Python) 예정(PBT-09, NFR Requirements에서 확정). |

**Resiliency 적용의 현실적 해석**: 인프라 성격 룰이 N/A로 다수 정리되는 것은 blocking finding이 아니라 정상적인 N/A 판정이다(룰 문서 명시). 설계·NFR 단계 완료 메시지에 "Resiliency Compliance" 요약(각 룰 compliant/N/A)을 포함한다.

---

## 7. 범위 (MVP Scope, 원천 §19)

- **P0 (필수)**: 로컬 로딩·자산 탐색·핵심 파싱(**PDF 포함**)·Feature 자동검출·Feature 지식 생성·Claim/Evidence·value_mismatch Conflict·근거 인용·MD+YAML 영속화·**MCP 서버(도구+리소스)**·Task 입력·Impact 분석·Must/Likely/Review·Change Plan·**Claude Code 턴키 시연 + 스크린샷**·기본 에러 처리·환경 기반 시크릿.
- **P1 (고가치)**: DOCX/PPTX·Confidence·missing_implementation·undocumented_behavior·충돌 인지 Impact·진행 상황·캐시/폴백 결과·MCP 프롬프트·폴백 CLI·기본 재분석·리스크 요약.
- **P2 / Out of Scope**: 원천 §19.3, §19.4 그대로 (웹 UI, 벡터DB, 자동 소스 수정, 프로덕션 권한 등 제외).

---

## 8. 완료 정의 (Definition of Done, 원천 §20 요약)

- 로컬 데모 프로젝트 로드 → 다중 자산 검출 → 수동개입 없이 분석 완료
- 최소 1개 Hero Feature 정확 식별, 다중 소스 연결, 중요 Claim에 Evidence, 최소 1개 Conflict 검출·설명
- Claude Code에서 Hero Task 입력 → 관련 파일 식별 → Must/Likely/Review 분리 → 이유·근거 포함 → Change Plan 생성
- README 스니펫+예제 프롬프트만으로 평가자가 E2E 흐름 재현, **`result/`(또는 `screenshots/`)에 시연 스크린샷 존재**
- 하드코딩 시크릿 없음, 코어/인터페이스 분리, 실패 로깅, 지식 영속화, Hero 반복 가능

---

## 9. 제안 Unit of Work 경계 (원천 §22 — Units Generation 입력)

- **UOW-01** 프로젝트 스캐너 & 파서 — FR-PROJECT-001/002/003, FR-ANALYSIS-003
- **UOW-02** Feature & Knowledge 생성 — FR-ANALYSIS-001, FR-KNOWLEDGE-001/002/003, FR-STORAGE-001
- **UOW-03** Claims/Evidence/Conflict — FR-CLAIM-001, FR-EVIDENCE-001, FR-CONFIDENCE-001, FR-CONFLICT-001, FR-CONFLICT-OUT-001/002
- **UOW-04** Task Impact Analysis — FR-IMPACT-001~006
- **UOW-05** MCP 서버 인터페이스 — FR-STORAGE-002, FR-MCP-001~004, §12 전체
- **UOW-06** 통합·신뢰성·시연 — NFR-AI-003/004, NFR-REL-001/002, FR-DEMO-001/002, §17/§18/§20
- **UOW-07** 프로젝트 온보딩 맵 (Increment 2, 신설) — FR-MAP-001~007. UOW-01(스캐너/파서 자산)·UOW-02(Feature 매핑)·UOW-0F(LLMService/Result/프롬프트 로더) 위에 관계 추출기 + 온보딩 맵 생성기 + Mermaid 렌더 + 새 MCP 도구/CLI 서브커맨드를 얹는다.

---

## 10. 핵심 요구사항 요약 (한눈에)

1. **로컬 MCP 서버(Python, stdio) + Claude Code** 가 유일한 "화면"이다.
2. 5개 MCP 도구로 코어 함수(scan/analyze/list/get_knowledge/get_conflicts/analyze_task_impact)를 노출한다.
3. 핵심 산출물은 **정규화 Claim ↔ Evidence 링크와 value_mismatch 충돌** — RAG와의 구조적 차별점.
4. Hero: **"Owner 등록에 SMS 인증 추가"** → 충돌 경고 + 근거 기반 Change Plan.
5. 데이터셋: **Spring Petclinic REST + 의도적 전화번호 길이 충돌(20 vs 10)**.
6. 시연 스크린샷을 `result/`에 남겨 완성도·사용성 평가에 대응한다.
7. 확장: PBT 전면 적용(Hypothesis), Resiliency 적용(대부분 인프라 룰 N/A), Security 확장 미적용(단 NFR-SEC P0 유효).
