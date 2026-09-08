# TRACE — 개발자 지식 인텔리전스 요구사항

## 1. 프로젝트 개요

### 1.0 문제 정의 (PROBLEM-001)

**누가:** 낯선 코드베이스에 갓 투입된 개발자, 문서와 구현의 드리프트를 쫓는 유지보수자, 변경의 파급 범위를 가늠해야 하는 기획자(PM). 그리고 **이들을 대신해 코드를 생성하는 AI 코딩 에이전트(Claude Code 등)**.

**언제·얼마나 자주:** 변경 티켓을 받을 때마다(상시 발생). 예를 들어 "Owner 등록에 SMS 인증을 추가하라"는 작업 하나를 받으면, 요구사항 문서·OpenAPI 명세·소스 코드·DB 스키마·테스트를 **각각 따로 열어 수작업으로 대조**해야 한다.

**무엇이 아픈가:**

* 정보가 **파일 단위로 흩어져** 있어 "기능 단위"로 재구성되지 않는다. 하나의 기능을 이해하려면 여러 파일을 사람이 머릿속에서 이어붙여야 한다.
* 문서와 구현이 **서로 어긋나 있어도 아무도 모른 채** 개발이 진행된다. (예: 요구사항은 전화번호 최대 20자, OpenAPI·코드는 10자.)
* **AI 코딩 에이전트는 이 충돌을 모른 채** 낡거나 잘못된 명세를 근거로 자신 있게 코드를 생성한다. 사람보다 빠르게, 그러나 같은 오해 위에서.
* 그 결과 **놓친 컴포넌트와 충돌이 구현을 마친 뒤에야** 드러나 재작업·장애로 이어진다.

한마디로: **"이 작업과 무엇이 관련돼 있고, 무엇이 어긋나 있으며, 무엇을 먼저 검토·변경해야 하는가"**를 구현 착수 전에 알 방법이 없다 — 사람에게도, AI 에이전트에게도.

### 1.1 제품 비전

TRACE는 흩어진 소프트웨어 개발 자산을 분석해 **기능(Feature) 중심의, 근거로 뒷받침되는 개발 지식**으로 재구성하고, 이를 **MCP(Model Context Protocol) 서버로 AI 코딩 에이전트에게 직접 노출**하는 개발자 지식 인텔리전스 시스템이다.

개발자·유지보수자·기획자는 자신이 이미 쓰는 AI 코딩 에이전트(Claude Code) 안에서, 낯선 시스템을 빠르게 이해하고 개발 산출물 사이의 불일치를 발견하며 계획한 변경의 영향 범위를 **구현 전에** 평가할 수 있다.

TRACE의 핵심 목적은 파편화된 프로젝트 자산을 **변경 인지(change-aware)·추적 가능(traceable)·검증 가능(verifiable)한 지식**으로 바꿔, 에이전트가 코드를 짜기 전에 근거를 갖게 하는 것이다. (전달 방식은 12장 MCP 인터페이스·13장 로컬 엔진 참조.)

### 1.2 핵심 가치 제안

* 파일 중심 정보를 **기능 중심 지식(Feature-centric Knowledge)**으로 전환한다.
* 중요한 지식을 **주장 → 근거 → 신뢰도 → 충돌(Claim → Evidence → Confidence → Conflict)** 구조로 연결한다.
* 요구사항·API 명세·소스 코드·DB 정의·설정·테스트 사이의 불일치를 검출한다.
* 개발 작업을 분석해 그 변경이 미칠 영향 범위를 식별한다.
* 근거 없는 LLM 추측이 아니라 **근거로 뒷받침되는 변경 권고**를 제공한다.
* 이 모든 지식을 **MCP 도구·리소스로 AI 코딩 에이전트에게 노출**해, 에이전트가 구현 직전 충돌과 영향 범위를 근거와 함께 확인하도록 한다.

### 1.3 제품 포지셔닝

TRACE는 소스 저장소·위키·Obsidian·RAG·코딩 어시스턴트를 대체하지 않는다. **원시 개발 자산과 AI 코딩 에이전트 사이에 놓이는 지식 계층(MCP 서버)**이다.

**개발 프로세스상 위치 — 구현 착수 직전(pre-implementation):** TRACE는 에이전트가 코드를 생성하기 직전에 개입해 "무엇이 관련돼 있고, 무엇이 어긋나 있으며, 무엇을 먼저 검토·변경해야 하는가"를 근거와 함께 도구 호출 결과로 제공한다. 온보딩·유지보수·변경 계획이라는 세 진입점은 3장에서 다룬다.

**구조적 차별 — "비슷한 것 찾기" vs "어긋난 것 찾기":** 기존 도구와의 차이는 표현이 아니라 데이터 구조와 전달 방식에서 나온다.

| 구분 | RAG / 위키 / 코딩 어시스턴트 | TRACE (MCP) |
| --- | --- | --- |
| 데이터 단위 | 유사 청크 / 파일 / 자유 텍스트 | **정규화된 Claim** (subject + predicate + value) |
| 답의 형태 | "관련 있어 보이는" 텍스트 반환 | **Claim↔Evidence 링크 + 교차 소스 값 비교** |
| 불일치 처리 | 감지하지 못하고 요약만 함 | **value_mismatch를 1급 산출물로 검출** |
| 신뢰 근거 | LLM의 자기 확신 | **근거 일치도 기반 Confidence** |
| 소비 방식 | 사람이 채팅으로 질의 | **AI 코딩 에이전트가 MCP 도구로 구현 직전 자동 질의** |

> RAG는 **'비슷한 것'**을 찾고, TRACE는 **'어긋난 것'**을 찾는다. 그리고 그 결과를 사람이 아니라 **코드를 짜기 직전의 AI 에이전트**에게 먹인다. 이 구조적 차이는 8장(Claim·Evidence·Conflict 모델)과 12장(MCP 인터페이스)에서 설계로 구체화된다.

---

## 2. 프로젝트 제약

### 2.1 개발 제약

* 개발 팀: 5명
* 개발 기간: 2일
* 1차 목표: 신뢰할 수 있는 엔드투엔드 PoC로 핵심 아이디어를 증명
* 2차 목표: 명확하고 직관적인 시연 제공
* 프로덕션급 확장성은 요구하지 않음
* 복잡한 인증, 조직 단위 인가, 클라우드 인프라는 시연에 필요하지 않은 한 PoC 범위 밖

### 2.2 우선순위 원칙

요구사항 분류:

* **P0** — 핵심 제품 가치 증명에 필수
* **P1** — 시연 품질 또는 평가 점수를 크게 높임
* **P2** — 프로덕션 진화에 유용하나 PoC에는 불필요
* **Out of Scope** — 현 구현에서 명시적으로 제외

### 2.3 평가 지향 제약

구현 결정은 다음을 우선한다.

1. AI 지원 소프트웨어 개발의 명확한 시연
2. 강한 문제-해결 적합성
3. 일반 위키/RAG/챗봇과의 차별화
4. 신뢰할 수 있는 엔드투엔드 시연 동작
5. **MCP 서버 형태에 맞는 사용성** — 막힘없는 설치·설정, 명확한 도구(API) 문서, 복붙 가능한 예제
6. 유지보수 가능한 모듈형 코드
7. 근거로 뒷받침되는 AI 결과
8. 기본적인 보안 위생

---

## 3. 대상 사용자 및 사용 맥락

세 사용자 모두 **Claude Code(MCP 클라이언트) 안에서** TRACE 도구를 통해 상호작용한다. 사람이 직접 웹 화면을 조작하는 것이 아니라, 에이전트에게 자연어로 요청하면 에이전트가 TRACE MCP 도구를 호출한다.

### 3.1 개발자 — 이해(Understand)

**핵심 질문**

> "어디를 바꿔야 하지?"

**시나리오**

낯선 시스템에 투입된 개발자가 Claude Code에서 변경 작업을 시작한다 → 에이전트가 TRACE 도구로 Feature Knowledge를 조회해 현재 시스템을 파악한다 → 문서와 구현 사이의 충돌을 발견한다 → Task Impact Analysis를 실행한다 → 근거로 뒷받침되는 Change Plan을 받는다.

**기대 가치**

* 더 빠른 시스템 이해
* 수작업 저장소 탐색 감소
* 관련 코드·API·DB·설정·테스트·문서에 대한 가시성
* 영향받는 컴포넌트를 놓칠 위험 감소

### 3.2 유지보수자 — 유지보수(Maintain)

**핵심 질문**

> "왜 이 문제가 생겼고, 또 무엇을 고쳐야 하지?"

**시나리오**

유지보수자가 운영 이슈나 정책 불일치를 조사한다 → 관련 Feature Knowledge를 연다 → 코드/API/DB/설정 근거를 검토한다 → 충돌 또는 낡은 지식을 식별한다 → 영향 범위를 확인한다 → 함께 갱신해야 할 테스트·문서를 포함한 Maintenance Plan을 받는다.

**기대 가치**

* 근본 원인 후보를 더 빨리 좁힘
* 문서/구현 드리프트 검출
* 관련 변경 범위 인식 향상
* 불완전한 수정으로 인한 재발 감소

### 3.3 기획자/PM — 변경 계획(Plan Change)

**핵심 질문**

> "이 요구사항이 바뀌면 영향은 어디까지 번지지?"

**시나리오**

PM이 새 요구사항이나 정책 변경을 평가한다 → 현재 Feature Knowledge를 검토한다 → 문서화된 요구사항과 구현 간 불일치를 식별한다 → 제안 변경을 Task Impact Analysis에 넣는다 → 구현 범위·리스크 요약·개발 전 결정 지점을 받는다.

**기대 가치**

* 코드를 직접 읽지 않고도 현재 동작 이해
* 구현 복잡도에 대한 조기 가시성
* 요구사항-개발 커뮤니케이션 향상
* 제약·상충 정책의 조기 발견

---

## 4. 시스템 구성

### 4.1 주요 컴포넌트

TRACE는 다음 논리 컴포넌트로 구성된다.

#### A. MCP 서버 인터페이스

Claude Code 등 MCP 클라이언트에 연결되는 로컬 MCP 서버(stdio 전송).

책임:

* TRACE 코어 기능을 **MCP 도구(tools)**로 노출
* 생성된 Feature Knowledge를 **MCP 리소스(resources)**로 노출
* 구현 전 검토를 돕는 **MCP 프롬프트(prompts)** 제공(P1)
* 도구 입력 스키마 검증 및 구조화된 결과 반환
* 분석 진행·실패를 도구 결과와 로그로 전달

#### B. 로컬 지식 엔진

선택한 프로젝트에 로컬 파일시스템으로 직접 접근하는 로컬 백엔드 프로세스.

책임:

* 프로젝트 파일 스캔
* 지원 산출물 분류
* 콘텐츠 파싱·정규화
* AI 워크플로우 실행
* 구조화된 지식 구축
* 생성 지식 영속화
* MCP 서버 인터페이스에 결과 제공

#### C. AI 워크플로우 계층

책임:

* Feature 식별
* 구조화 추출
* Claim 정규화
* Evidence 그룹화
* Confidence 결정
* Conflict 검출
* Feature Knowledge 생성
* Task Impact Analysis
* Change Plan 생성

#### D. 지식 저장소

PoC에서는 지식을 로컬에 저장한다.

선호 표현:

```text
knowledge/
  features/
    <feature-id>.md
```

각 Feature Knowledge 파일은 다음을 포함해야 한다.

* 구조화·기계 판독 데이터를 위한 YAML Front Matter
* 사람이 읽는 설명을 위한 Markdown 본문

MCP 서버는 구조화된 YAML 필드를 도구 결과의 구조화 필드로, Markdown 본문을 리소스 콘텐츠로 노출한다.

---

## 5. 프로젝트 입력 요구사항

### 5.1 프로젝트 선택

**FR-PROJECT-001 — 로컬 프로젝트 로딩 — P0**

사용자는 로컬 프로젝트 디렉터리를 대상으로 TRACE를 시작할 수 있어야 한다.

선호 PoC 사용 방식: **Claude Code의 MCP 서버 설정**에 대상 프로젝트 경로를 지정하거나, 분석 도구 호출 시 경로를 인자로 전달한다.

```jsonc
// Claude Code MCP 설정 예시 (.mcp.json 또는 프로젝트 설정)
{
  "mcpServers": {
    "trace": {
      "command": "trace-mcp",
      "args": ["--project", "./spring-petclinic-rest"]
    }
  }
}
```

대안: `analyze_project(path)` 도구 호출 시 경로를 직접 전달.

**수용 기준**

* 유효한 디렉터리를 로드할 수 있다.
* 유효하지 않거나 접근 불가한 경로는 명확한 오류를 반환한다.
* 로드된 프로젝트 이름과 감지된 자산 요약을 도구 결과로 반환한다.

### 5.2 지원 자산 유형

**FR-PROJECT-002 — 자산 탐색 — P0**

시스템은 존재하는 경우 다음 산출물 범주를 탐색·분류해야 한다.

* 소스 코드
* Markdown / 텍스트 문서
* PDF 문서
* OpenAPI / Swagger 등 API 명세(YAML 또는 JSON)
* SQL 스키마 또는 마이그레이션 파일
* YAML / properties / 환경 변수형 설정
* 테스트 소스 파일

**P1**

* PPT/PPTX
* DOC/DOCX

탐색된 각 파일에 대해 TRACE는 최소한 다음을 기록해야 한다.

* 경로
* 산출물 유형
* 파일명
* 선택적 언어/유형 메타데이터
* 파싱 상태

### 5.3 파일 필터링

**FR-PROJECT-003 — 제외 규칙 — P0**

분석기는 기본적으로 흔한 비소스 디렉터리와 생성 산출물을 제외해야 한다.

예:

* `.git`
* `node_modules`
* `build`
* `dist`
* `target`
* 바이너리 파일
* IDE 메타데이터
* 의존성 캐시

제외 규칙은 간단한 설정 파일이나 중앙 상수로 구성 가능해야 한다.

---

## 6. 프로젝트 분석 요구사항

### 6.1 분석 트리거

**FR-ANALYSIS-001 — 프로젝트 분석 — P0**

MCP 서버는 `analyze_project` 도구를 제공해야 한다.

호출 시 로컬 지식 엔진은 다음을 수행해야 한다.

1. 지원 파일 스캔
2. 관련 콘텐츠 파싱
3. 구조화 정보 추출
4. 후보 Feature 식별
5. Claim·Evidence 추출
6. Conflict 검출
7. Feature Knowledge 생성
8. 결과 영속화
9. 분석 요약 반환

### 6.2 분석 진행 상황

**FR-ANALYSIS-002 — 진행 가시성 — P1**

분석 도구는 고수준 진행 단계를 구조화된 결과 또는 로그로 전달해야 한다. 예:

```text
Scanning project
Parsing sources
Extracting features
Building knowledge
Detecting conflicts
Generating feature views
```

내부 사고 과정(chain-of-thought)은 노출하지 않는다.

### 6.3 부분 실패

**FR-ANALYSIS-003 — 결함 허용 — P0**

한 파일의 파싱 실패가 전체 프로젝트 분석을 중단시켜서는 안 된다.

시스템은 다음을 수행해야 한다.

* 실패한 파일 표시
* 실패 로깅
* 가능한 다른 파일 분석 계속
* 분석이 경고와 함께 완료되었음을 결과로 알림

---

## 7. 기능 중심 지식 요구사항

### 7.1 Feature 정의

**Feature**는 사용자에게 보이는 능력, 비즈니스 능력, 또는 응집된 기능 동작을 나타내는 최상위 지식 컨테이너다.

예:

* User Registration
* Owner Registration
* Pet Registration
* Visit Management
* Authentication

Feature는 단일 사실이 아니다. 그 동작을 이해하거나 변경하는 데 필요한 지식을 묶는다.

Feature는 다음을 포함할 수 있다.

* Claims
* Evidence
* Conflicts
* 관련 소스 코드
* API
* 데이터베이스 구조
* 설정
* 테스트
* 문서
* 의존성

### 7.2 Feature 식별

**FR-KNOWLEDGE-001 — Feature 검출 — P0**

AI 워크플로우는 분석된 프로젝트 자산에서 의미 있는 소수의 Feature를 식별해야 한다.

PoC는 완전한 커버리지보다 품질을 우선한다.

**수용 기준**

데모 프로젝트에서 최소 하나의 Hero Feature가 정확히 식별되고, 여러 산출물 유형에 걸친 교차 소스 근거를 포함해야 한다.

### 7.3 Feature Knowledge 뷰

**FR-KNOWLEDGE-002 — Feature Knowledge — P0**

각 Feature에 대해 TRACE는 가능한 경우 다음을 담은 사람 친화적 지식 뷰를 생성해야 한다.

* 개요
* 비즈니스 규칙
* 관련 소스 코드
* 관련 API
* 데이터베이스
* 설정
* 테스트
* 알려진 충돌
* 소스 근거
* 의존성
* 선택적 변경 노트

### 7.4 필수 교차 소스 연관

**FR-KNOWLEDGE-003 — 교차 소스 연결 — P0**

Hero Feature에 대해 TRACE는 최소 세 가지 서로 다른 산출물 범주를 연관시켜야 한다.

선호 시연:

```text
Requirement / Manual
API Specification
Source Code
Database
Configuration
Test
```

PoC는 저장소의 모든 관계를 추론할 필요는 없다.

---

## 8. Claim, Evidence, Confidence, Conflict 모델

### 8.1 Claim

**Claim**은 시스템에 대한 검증 가능한 진술을 나타내는, 가장 작은 정규화된 지식 단위다.

권장 개념 모델:

```text
Subject + Predicate + Value
```

예:

```text
user.password + min_length + 10
owner.telephone + max_length + 10
POST /api/owners + authentication_required + true
```

### 8.2 Claim 요구사항

**FR-CLAIM-001 — Claim 추출 — P0**

시스템은 Hero Feature와 관련된 선택된 비즈니스·기술 규칙에 대해 정규화된 Claim을 추출해야 한다.

Claim은 원자적(atomic)이어야 한다.

나쁨:

```text
Registration uses email, password length is 10, and verification is mandatory.
```

좋음:

```text
user.email.required = true
user.password.min_length = 10
user.email_verification.required = true
```

### 8.3 Evidence

**FR-EVIDENCE-001 — Evidence 연관 — P0**

중요한 각 Claim은 근거가 존재하는 경우 하나 이상의 Evidence 레코드를 가져야 한다.

각 Evidence 레코드는 다음을 포함해야 한다.

* 소스 경로
* 소스 유형
* 가능한 경우 소스 위치
* 추출된 값 또는 관련 사실
* Claim과의 관계

권장 관계 유형:

* `direct`
* `supporting`
* `related`
* `contradicting`

예:

```yaml
evidence:
  - source: src/main/java/User.java
    location: line 42
    type: source_code
    relation: direct
    extracted_value: 10
```

### 8.4 Confidence

**FR-CONFIDENCE-001 — Confidence 수준 — P1**

TRACE는 중요한 Claim에 신뢰도 수준을 부여해야 한다.

허용 PoC 값:

* `HIGH`
* `MEDIUM`
* `LOW`

Confidence는 LLM의 자기 보고 확률이 아니라 주로 근거의 품질과 일치도에 근거해야 한다.

해석 예:

* HIGH: 여러 강한 소스가 일치
* MEDIUM: 제한적 근거 또는 부분 일치
* LOW: 약하거나 모호하거나 상충하며 명확한 유효 동작이 없음

### 8.5 Conflict

**Conflict**는 동일한 정규화 Claim에 연관된 근거가 서로 어긋나거나, 기대 동작과 유효 동작이 갈릴 때 존재한다.

**FR-CONFLICT-001 — 값 불일치 — P0**

TRACE는 정규화된 Claim에 대한 직접적인 값 불일치를 검출해야 한다.

예:

```text
Requirement: password minimum length = 8
OpenAPI:     password minimum length = 10
Code:        password minimum length = 10
```

### 8.6 지원 Conflict 유형

PoC 우선순위:

1. `value_mismatch` — P0
2. `missing_implementation` — P1
3. `undocumented_behavior` — P1
4. `structural_mismatch` — P1

시간이 부족하면 `value_mismatch`만 완전 지원해도 된다.

### 8.7 유효 동작 vs 기대 동작

가능한 경우 TRACE는 다음을 구분해야 한다.

* **기대 동작(Expected Behavior)** — 요구사항 또는 명세의 의도
* **유효 동작(Effective Behavior)** — 코드/설정/테스트가 나타내는 실제 런타임 동작

TRACE는 소스 코드가 항상 옳다고 자동으로 가정해서는 안 된다.

---

## 9. 지식 파일 요구사항

### 9.1 저장 형식

**FR-STORAGE-001 — Markdown + YAML Front Matter — P0**

생성된 각 Feature Knowledge 산출물은 YAML Front Matter를 가진 Markdown 파일을 사용해야 한다.

예:

```markdown
---
id: feature.owner-registration
type: feature
title: Owner Registration
confidence: high

claims:
  - id: owner.telephone.max_length
    subject: owner.telephone
    predicate: max_length
    value: 10
    confidence: high
    conflict: true

related_files:
  - src/main/java/.../OwnerController.java
  - src/main/java/.../Owner.java

apis:
  - method: POST
    path: /api/owners
---

# Owner Registration

## Overview

사람이 읽는 기능 설명.

## Business Rules

...

## Known Conflicts

...
```

### 9.2 데이터 소유 규칙

구조화된 사실은 가능하면 정규 YAML 필드에 한 번만 표현한다.

Markdown 본문은 그 사실을 설명하거나 맥락을 제공한다.

시스템은 실무적으로 가능한 한 동일한 가변 값을 여러 곳에서 독립적으로 유지하지 않아야 한다.

### 9.3 MCP 리소스로서의 노출

**FR-STORAGE-002 — 리소스 노출 — P0**

MCP 서버는 생성된 Feature Knowledge를 리소스로 노출해야 한다. 클라이언트(에이전트)는 다음을 할 수 있어야 한다.

* YAML Front Matter의 구조화 필드를 도구 결과로 수신
* Markdown 본문을 리소스 콘텐츠로 수신
* 요약 메타데이터를 구조화 필드로 수신

예시 메타데이터:

```text
confidence: HIGH
conflicts: 1
related_sources: 6
```

### 9.4 생성 산출물 정책

생성된 지식은 시스템 생성 출력으로 취급한다.

PoC에서 생성된 Feature Knowledge의 수동 편집은 요구하지 않는다.

향후 시스템은 사람의 교정/재정의 워크플로우를 지원할 수 있다.

---

## 10. 충돌 결과 요구사항

### 10.1 충돌 요약

**FR-CONFLICT-OUT-001 — 충돌 가시성 — P0**

Feature 조회 결과는 검출된 충돌 수를 구조화 필드로 명확히 제공해야 한다.

예:

```json
{ "feature": "Owner Registration", "confidence": "HIGH", "conflicts": 1 }
```

### 10.2 충돌 상세

검출된 충돌에 대해 도구 결과는 다음을 포함해야 한다.

* Claim/주제
* 상충하는 값들
* 소스
* 가능한 경우 소스 위치
* 짧은 해석

예:

```text
Telephone Maximum Length

Requirement     20
OpenAPI         10
Source Code     10

해석:
API와 런타임 검증은 10을 사용하지만, 요구사항 문서는 20을 명시한다.
```

### 10.3 근거 참조

**FR-CONFLICT-OUT-002 — 근거 참조 — P0**

에이전트는 각 상충 값을 뒷받침하는 소스 파일이 무엇인지 결과에서 확인할 수 있어야 한다.

파일을 직접 여는 것은 PoC에서 선택 사항이다(에이전트가 경로로 열 수 있음).

---

## 11. Task Impact Analysis 요구사항

### 11.1 작업 입력

**FR-IMPACT-001 — 개발 작업 입력 — P0**

MCP 서버는 자연어 변경 요청을 받는 `analyze_task_impact` 도구를 제공해야 한다.

Hero 예시:

> `Add SMS verification to Owner registration.`

### 11.2 컨텍스트 선택

**FR-IMPACT-002 — 지식 기반 분석 — P0**

Task Impact Analysis는 기존 Feature Knowledge와 Evidence를 컨텍스트로 사용해야 한다.

분석은 작업 텍스트에 대한 일반 LLM 프롬프트에만 의존해서는 안 된다.

### 11.3 영향 출력

**FR-IMPACT-003 — 영향 분류 — P0**

결과는 최소 다음으로 영향 후보를 분류해야 한다.

* **Must Change**
* **Likely Change**
* **Review**

각 결과는 이유를 포함해야 한다.

예:

```text
Must Change
- OwnerController.java
  이유: owner 등록 요청을 처리함.

- openapi.yaml
  이유: 등록 API 계약에 인증 동작이 포함돼야 함.

Likely Change
- application.yml
  이유: SMS 제공자 설정이 필요할 수 있음.

Review
- Database schema
  이유: 인증 상태를 영속화하는 경우에만 필요.
```

### 11.4 관련 기존 충돌

**FR-IMPACT-004 — 충돌 인지 영향 분석 — P1**

제출된 작업과 관련된 기존 Conflict가 있으면, TRACE는 구현 변경을 권고하기 전에 이를 강조해야 한다.

예:

```text
이 변경과 관련된 기존 충돌:
전화번호 길이가 요구사항과 구현 사이에서 다릅니다.
SMS 인증을 구현하기 전에 검증 정책을 해소하세요.
```

### 11.5 영향 근거

**FR-IMPACT-005 — 근거 기반 권고 — P0**

권고된 파일이나 컴포넌트는 가능한 경우 간단한 이유와 뒷받침 지식 참조를 포함해야 한다.

### 11.6 Change Plan

**FR-IMPACT-006 — Change Plan — P0**

TRACE는 간결한 순서형 Change Plan을 생성해야 한다.

예:

1. 현재 전화번호 검증 정책 해소
2. SMS 인증 API 동작 정의
3. owner 등록 흐름 수정
4. 제공자 설정 추가
5. 성공/실패/타임아웃 테스트 추가
6. 요구사항 문서 갱신

Change Plan은 자문용이며 PoC에서 소스 코드를 자동 수정하지 않는다.

---

## 12. MCP 인터페이스 요구사항

### 12.1 MCP 도구(Tools)

**FR-MCP-001 — 도구 노출 — P0**

MCP 서버는 최소 다음 도구를 노출해야 한다.

| 도구 | 목적 | 관련 FR |
| --- | --- | --- |
| `analyze_project(path)` | 대상 프로젝트를 분석하고 지식을 생성 | FR-ANALYSIS-001 |
| `list_features()` | 검출된 Feature 목록과 요약 반환 | FR-KNOWLEDGE-001 |
| `get_feature_knowledge(feature_id)` | 특정 Feature의 지식 반환 | FR-KNOWLEDGE-002 |
| `get_conflicts(feature_id?)` | 충돌 목록/상세 반환 | FR-CONFLICT-OUT-001 |
| `analyze_task_impact(task, feature_id?)` | 작업의 영향 범위와 Change Plan 반환 | FR-IMPACT-001 |

각 도구는 **명확한 입력 스키마**와 **구조화된(JSON) 결과**를 가져야 한다.

### 12.2 MCP 리소스(Resources)

**FR-MCP-002 — 리소스 노출 — P0**

생성된 Feature Knowledge 파일(`knowledge/features/*.md`)을 MCP 리소스로 노출해, 에이전트가 컨텍스트로 읽을 수 있어야 한다(FR-STORAGE-002).

### 12.3 MCP 프롬프트(Prompts)

**FR-MCP-003 — 구현 전 검토 프롬프트 — P1**

"구현 착수 전 충돌·영향 검토"를 유도하는 재사용 가능한 MCP 프롬프트 템플릿을 제공한다. 에이전트가 코드 작성 전 TRACE 도구를 호출하도록 안내한다.

### 12.4 전송 및 클라이언트

**FR-MCP-004 — stdio 전송 / Claude Code 연동 — P0**

* 서버는 stdio 전송으로 로컬 실행되어야 한다.
* **기준 시연 클라이언트는 Claude Code**로 한다.
* README는 **복붙 가능한 MCP 설정 스니펫**과 **예제 프롬프트**를 제공해야 한다(5.1 참조).

### 12.5 설명 가능성 (NFR-MCP-UX-001)

에이전트가 받은 도구 결과만으로 "왜 이 결과가 나왔는지"를 사람에게 설명할 수 있어야 한다. 결과에는 근거(파일·위치·값)가 포함되어야 한다.

### 12.6 점진적 노출 (NFR-MCP-UX-002)

도구 결과는 다음 순서로 핵심을 먼저 담아야 한다.

1. Feature 요약
2. Conflict
3. Impact
4. Evidence

저수준 메타데이터는 접근 가능하되 결과의 앞부분을 지배해서는 안 된다.

### 12.7 시연 명료성 (NFR-MCP-UX-003)

처음 보는 평가자가 README의 설정 스니펫과 예제 프롬프트를 따라 **약 30초 안에** "에이전트가 TRACE에게 물어 충돌을 경고받는" 흐름을 재현할 수 있어야 한다.

---

## 13. 로컬 엔진 요구사항

### 13.1 로컬 우선 실행

**NFR-LOCAL-001 — 로컬 파일 접근 — P0**

지식 엔진은 로컬에서 실행되고 로컬 파일시스템에서 프로젝트 파일에 직접 접근해야 한다.

MCP 클라이언트(에이전트)는 무제한 파일시스템 접근을 담당하지 않으며, 파일 접근은 로컬 엔진을 통한다.

### 13.2 인터페이스 경계

**NFR-CORE-001 — 코어/인터페이스 분리 — P0**

MCP 서버는 모든 AI 로직을 도구 핸들러에 직접 박아넣는 대신, 재사용 가능한 코어 함수를 호출해야 한다.

권장 코어 인터페이스(= MCP 도구의 구현 대상):

```text
scan_project(path)
analyze_project(path)
list_features()
get_feature_knowledge(feature_id)
get_conflicts(feature_id?)
analyze_task_impact(task, feature_id?)
```

### 13.3 재사용성

**NFR-CORE-002 — 코어 재사용 — P0**

코어 분석 함수는 MCP 서버가 소비하며, 동일 함수를 다음 인터페이스가 재사용할 수 있도록 설계한다.

* CLI(시연 폴백/예제 실행기, 18장 참조)
* 향후 IDE 확장
* 향후 CI 검증

MCP 서버 외의 어댑터는 P0에서 필수는 아니다(CLI 폴백은 P1).

---

## 14. AI 워크플로우 요구사항

### 14.1 필수 워크플로우

PoC AI 파이프라인은 개념적으로 다음을 따른다.

```text
Raw Sources
    ↓
Parsing
    ↓
Structured Extraction
    ↓
Feature Identification
    ↓
Claim Normalization
    ↓
Evidence Grouping
    ↓
Conflict Detection
    ↓
Confidence Assignment
    ↓
Feature Knowledge Generation
```

작업 분석:

```text
Development Task
    ↓
Relevant Feature / Claims
    ↓
Evidence Traversal
    ↓
Affected Asset Identification
    ↓
Risk / Conflict Review
    ↓
Change Plan
```

### 14.2 구조화 AI 출력

**NFR-AI-001 — 기계 판독 출력 — P0**

AI 출력이 이후 처리 단계나 MCP 도구 결과로 쓰이는 경우, 자유형 산문이 아니라 구조화된 JSON/YAML 호환 출력을 요청해야 한다.

### 14.3 그라운딩

**NFR-AI-002 — 근거 그라운딩 — P0**

AI가 생성한 Claim, Conflict, Impact 권고는 가능한 경우 분석된 프로젝트 자산을 참조해야 한다.

### 14.4 환각 처리

**NFR-AI-003 — 불확실성 — P0**

근거가 부족할 때 시스템은 뒷받침되지 않은 결론을 확실한 것처럼 제시해서는 안 된다.

선호 표현:

* `Review`
* `Potential impact`
* `Insufficient evidence`
* `Confidence: LOW`

### 14.5 결정성

**NFR-AI-004 — 시연 안정성 — P1**

고정된 데모 데이터셋에 대해 프롬프트와 모델 파라미터는 안정적이고 반복 가능한 출력을 선호해야 한다.

라이브 AI 실행이 실패할 경우, 캐시된 분석 결과를 시연 폴백으로 사용할 수 있다.

---

## 15. 비기능 요구사항

### 15.1 성능

**NFR-PERF-001**

PoC는 대규모 엔터프라이즈 저장소가 아니라 소규모 데모 저장소 또는 선별된 부분집합에 최적화해야 한다.

**NFR-PERF-002**

장시간 분석 도구는 진행 상태를 결과/로그로 알려 클라이언트가 멈춘 것처럼 보이지 않게 해야 한다.

**NFR-PERF-003**

이전에 생성된 Feature Knowledge를 반복 조회할 때 불필요한 LLM 호출이 발생하지 않아야 한다.

### 15.2 신뢰성

**NFR-REL-001**

Hero 시나리오는 시연 중 수동 파일 편집 없이 엔드투엔드로 완료되어야 한다.

**NFR-REL-002**

AI 분석이 실패하면, 도구는 사람이 읽을 수 있는 실패 메시지를 반환하고 진단 세부를 로깅해야 한다.

### 15.3 유지보수성

**NFR-MAINT-001**

코드베이스는 최소한 다음을 분리해야 한다.

* MCP 서버 인터페이스
* 소스 스캔/파싱
* AI 워크플로우
* 지식 모델/저장
* 충돌 검출
* 영향 분석
* 설정

**NFR-MAINT-002**

프롬프트는 실무적으로 가능한 한 인터페이스 코드와 분리해 저장해야 한다.

### 15.4 로깅

**NFR-LOG-001**

시스템은 다음을 로깅해야 한다.

* 프로젝트 스캔 시작/종료
* 파싱 실패
* AI 요청 실패
* 지식 생성 상태
* 충돌 검출 수
* Task Impact Analysis 상태

로그는 의도적으로 시크릿을 노출해서는 안 된다.

---

## 16. 보안 및 프라이버시 요구사항

### 16.1 시크릿

**NFR-SEC-001 — 하드코딩 시크릿 금지 — P0**

API 키, 토큰, 자격 증명은 소스 코드에 하드코딩되어서는 안 된다.

환경 변수 또는 로컬 설정을 사용한다.

### 16.2 로컬 프로젝트 프라이버시

**NFR-SEC-002 — 로컬 우선 처리 — P0**

원시 프로젝트 파일은 설정된 LLM 제공자에게 명시적으로 전송되는 콘텐츠를 제외하고 로컬에 유지되어야 한다.

### 16.3 민감 데이터 인식

**NFR-SEC-003 — P1**

아키텍처는 다음을 위한 향후 삽입 지점을 제공해야 한다.

* 시크릿 필터링
* PII 필터링
* 민감 파일 제외
* 사설 엔터프라이즈 모델 엔드포인트

완전한 DLP 구현은 PoC에서 요구하지 않는다.

### 16.4 경로 검증

**NFR-SEC-004**

MCP 도구가 로컬 파일시스템 경로를 받는 경우, 백엔드는 분석 전에 경로가 존재하고 디렉터리인지 검증해야 한다.

### 16.5 MCP 전송 보안

**NFR-SEC-005 — P0**

MCP 서버는 로컬 stdio 전송으로 동작하며, 도구 결과·로그로 시크릿을 노출하지 않아야 한다.

---

## 17. 에러 처리 요구사항

### 17.1 미지원 파일

미지원 파일은 건너뛰고 무시됨(ignored)으로 기록한다.

### 17.2 파서 실패

파서 실패는 다음을 생성해야 한다.

* 파일 경로
* 오류 범주
* 경고 상태

전체 프로젝트 분석은 계속되어야 한다.

### 17.3 LLM 실패

타임아웃, 쿼터, 제공자 오류로 LLM 요청이 실패하면:

* 사용자 친화적 오류를 도구 결과로 반환
* 이전에 생성된 지식 보존
* 기술 세부 로깅
* 실무적으로 가능한 경우 재시도 허용

### 17.4 잘못된 구조화 출력

AI 출력이 기대 스키마로 파싱되지 않으면:

* 실무적으로 가능한 경우 제약 교정 프롬프트로 재시도
* 그렇지 않으면 해당 분석 단계를 실패로 표시
* 잘못된 지식을 조용히 저장하지 않음

---

## 18. 데모 데이터셋 및 시연 구성

### 18.1 선호 데이터셋

PoC는 여러 엔지니어링 산출물 유형을 가진 선별 공개 소프트웨어 프로젝트 또는 부분집합을 사용해야 한다.

권장 예:

* Spring Petclinic REST 또는 선별 부분집합

### 18.2 합성 보조 문서

데모는 교차 소스 커버리지를 높이기 위해 현실적인 합성 엔터프라이즈 산출물을 추가할 수 있다.

예:

* 요구사항 PDF
* 아키텍처 PPT/PPTX
* 매뉴얼 DOCX

### 18.3 의도된 충돌

데모 데이터셋은 최소 하나의 의도적이고 이해하기 쉬운 충돌을 포함해야 한다.

예:

```text
Requirement:
Owner telephone max length = 20

OpenAPI:
maxLength = 10

Source Code:
@Size(max = 10)
```

### 18.4 Hero Task

선호 Hero Task:

> `Add SMS verification to Owner registration.`

데이터셋은 의미 있는 Task Impact Analysis를 시연할 수 있을 만큼 관련 코드/API/설정/테스트/문서 자산을 포함해야 한다.

### 18.5 시연 클라이언트 (Claude Code) — 턴키 구성

**FR-DEMO-001 — 턴키 시연 — P0**

MCP 단독 제품이므로 "화면"은 Claude Code 세션이다. 다음을 제공해 설정 진입장벽을 제거해야 한다.

* **복붙용 MCP 설정 스니펫** (5.1의 `.mcp.json` 예시)
* **복붙용 예제 프롬프트** (Hero Task 그대로)
* **`result/` 또는 `screenshots/` 에 시연 스크린샷 필수 저장** — Claude Code가 TRACE 도구를 호출하고 충돌 경고 + Change Plan을 받는 장면

### 18.6 시연 폴백 CLI

**FR-DEMO-002 — 예제 실행기 CLI — P1**

MCP 클라이언트 설정이 실패하는 경우를 대비해, 동일 코어 함수를 호출하는 얇은 CLI(예: `trace analyze-task "..."`)를 제공한다. 이는 제품 인터페이스가 아니라 재현 가능한 예제 실행기/폴백이다(NFR-REL-001, NFR-AI-004 연계).

---

## 19. MVP 범위

### 19.1 P0 — 필수

* 로컬 프로젝트 로딩
* 소스 자산 탐색
* 핵심 텍스트/코드/설정/API/DB/테스트 산출물 파싱
* Feature 검출
* Feature 중심 지식 생성
* Claim 추출
* Evidence 연관
* 값 기반 Conflict 검출
* 소스 인용/근거 제공
* Markdown + YAML Front Matter 지식 영속화
* **MCP 서버 (도구 + 리소스)**
* 자연어 Task 입력(도구 인자)
* Task Impact Analysis
* Must Change / Likely Change / Review 분류
* Change Plan
* **Claude Code 턴키 시연 구성 + 시연 스크린샷**
* 기본 에러 처리
* 환경 기반 LLM 시크릿 관리

### 19.2 P1 — 시간 허용 시 고가치

* P0 파서 세트에 없다면 PDF 파싱
* DOCX/PPTX 파싱
* Confidence 스코어링
* Missing implementation 검출
* Undocumented behavior 검출
* 충돌 인지 Impact 분석
* 분석 진행 상황 전달
* 캐시/폴백 데모 결과
* MCP 프롬프트 템플릿
* 시연 폴백 CLI
* 기본 지식 갱신 / 재분석
* 리스크 요약

### 19.3 P2 — PoC 이후

* 시맨틱 검색
* 일반 저장소 챗
* 벡터 데이터베이스
* 지식 그래프
* 자동 Git 변경 모니터링
* 지식 드리프트 검출
* GitHub 통합
* CI 검증
* IDE 확장
* 사용자 인증 및 RBAC
* 멀티 프로젝트 워크스페이스
* 클라우드 배포
* 대규모 저장소 최적화
* 웹 UI (별도 사람 대면 화면)

### 19.4 Out of Scope

* 자동 소스 코드 수정
* 완전 자율 코딩 에이전트
* 프로덕션급 엔터프라이즈 권한
* 실시간 협업
* Windows 네이티브 데스크톱 애플리케이션
* 저장소 전체 규모 정적 분석
* 소프트웨어 동작의 완전한 정형 검증

---

## 20. 완료 정의 (Definition of Done)

다음이 모두 참일 때 PoC는 완료된 것으로 본다.

### 프로젝트 분석

* 로컬 데모 프로젝트를 로드할 수 있다
* 여러 산출물 유형이 검출된다
* 수동 개입 없이 분석이 완료된다

### Feature Knowledge

* 최소 하나의 Hero Feature가 정확히 식별된다
* Feature가 여러 소스 범주를 연결한다
* 중요한 Claim이 Evidence를 가진다
* 최소 하나의 Conflict가 검출되고 명확히 설명된다

### Task Impact

* 사용자가 Claude Code에서 Hero Task를 입력할 수 있다
* TRACE가 관련 파일/컴포넌트를 식별한다
* 영향이 Must Change / Likely Change / Review로 분리된다
* 권고에 이유나 근거가 포함된다
* Change Plan이 생성된다

### 사용성 (MCP)

* 평가자가 README의 설정 스니펫과 예제 프롬프트만으로 다음 흐름을 재현할 수 있다:

```text
Claude Code에 TRACE MCP 연결
    ↓
Analyze Project (도구 호출)
    ↓
Feature / Conflict 조회
    ↓
Hero Task 입력
    ↓
Task Impact Analysis → Change Plan
```

* 위 흐름의 **시연 스크린샷이 `result/`(또는 `screenshots/`)에 존재**한다(PROBLEM-001 해소를 보여줌).

### 엔지니어링 품질

* 하드코딩된 LLM 시크릿 없음
* 코어 로직이 MCP 인터페이스 코드와 분리됨
* 분석 실패가 로깅됨
* 생성된 지식이 영속화됨
* Hero 시나리오가 시연에서 반복 가능함

---

## 21. AI-DLC 추적성 요구사항

저장소는 프로젝트가 AI-DLC 프로세스로 개발되었다는 증거를 보존해야 한다.

권장 구조:

```text
/aidlc
  /inception
  /requirements
  /architecture
  /decisions
  /units
  /construction
  /test
```

최소한 다음을 보존해야 한다.

* Problem Statement (PROBLEM-001)
* Target Users
* Hero Scenario
* Requirements
* Scope 결정
* Architecture 결정
* Unit of Work 정의
* 프롬프트 또는 AI 협업 증거
* 테스트 증거
* 사람의 승인/리뷰 기록

이 문서의 요구사항은 실무적으로 가능한 경우 Architecture Decisions, Units of Work, 테스트에서 ID로 참조되어야 한다.

예:

```text
UOW-03 Conflict Detection
Implements:
- FR-CLAIM-001
- FR-EVIDENCE-001
- FR-CONFLICT-001
- FR-CONFLICT-OUT-001
```

---

## 22. 제안 Unit of Work 경계

다음 경계는 AI-DLC Construction 계획을 위한 권장 사항이며 필수 구현 모듈이 아니다.

### UOW-01 — 프로젝트 스캐너 & 파서

관련 요구사항:

* FR-PROJECT-001
* FR-PROJECT-002
* FR-PROJECT-003
* FR-ANALYSIS-003

### UOW-02 — Feature & Knowledge 생성

관련 요구사항:

* FR-ANALYSIS-001
* FR-KNOWLEDGE-001
* FR-KNOWLEDGE-002
* FR-KNOWLEDGE-003
* FR-STORAGE-001

### UOW-03 — Claims, Evidence & Conflict

관련 요구사항:

* FR-CLAIM-001
* FR-EVIDENCE-001
* FR-CONFIDENCE-001
* FR-CONFLICT-001
* FR-CONFLICT-OUT-001
* FR-CONFLICT-OUT-002

### UOW-04 — Task Impact Analysis

관련 요구사항:

* FR-IMPACT-001
* FR-IMPACT-002
* FR-IMPACT-003
* FR-IMPACT-004
* FR-IMPACT-005
* FR-IMPACT-006

### UOW-05 — MCP 서버 인터페이스

관련 요구사항:

* FR-STORAGE-002
* FR-MCP-001
* FR-MCP-002
* FR-MCP-003
* FR-MCP-004
* FR-CONFLICT-OUT-001
* FR-CONFLICT-OUT-002
* Section 12 MCP 인터페이스 요구사항

### UOW-06 — 통합, 신뢰성 & 시연

관련 요구사항:

* NFR-AI-003
* NFR-AI-004
* NFR-REL-001
* NFR-REL-002
* FR-DEMO-001
* FR-DEMO-002
* Section 17 에러 처리
* Section 18 데모 데이터셋
* Section 20 완료 정의

---

## 23. 미해결 결정

다음 결정은 AI-DLC Architecture/Inception 활동 중 확정될 수 있다.

1. 최종 프로젝트 이름 (`TRACE`는 본 문서의 작업명)
2. MCP 서버 구현 언어/SDK (예: Python MCP SDK vs TypeScript MCP SDK)
3. 정확한 LLM 제공자/모델
4. 정확한 파서 라이브러리 선택
5. PDF/DOCX/PPTX 지원이 P0인지 P1인지
6. 정확한 YAML 스키마
7. Confidence 계산 정책
8. Feature 검출이 완전 자동인지 데모 설정 보조인지
9. 시연 폴백을 위해 분석 결과를 캐시할지
10. 시연 폴백 CLI를 구현할지

Construction 시작 전에 핵심 미해결 결정을 기록해야 한다.

---

## 부록 A. 용어

* **Feature**: 소프트웨어 능력을 이해하거나 변경하는 데 필요한 정보를 묶는 최상위 기능 지식 컨테이너.
* **Claim**: 시스템에 대한 정규화된 검증 가능 진술.
* **Evidence**: Claim을 뒷받침·관련·반박하는 소스 기반 사실.
* **Confidence**: 가용 근거가 Claim을 얼마나 강하게 뒷받침하는지에 대한 표시.
* **Conflict**: 동일한 정규화 Claim에 연관된 근거 간 불일치.
* **Feature Knowledge**: 파일이 아니라 Feature를 중심으로 조직된, 사람·AI가 소비 가능한 지식.
* **Task Impact Analysis**: 제안된 개발 작업에 대해 어떤 프로젝트 자산이 변경·검토되어야 하는지 분석.
* **Change Plan**: 순서형·근거 기반의 권장 구현/검토 단계 집합.
* **Local Engine**: 프로젝트 파일을 스캔하고 AI 워크플로우를 실행하며 생성 지식을 관리하는 로컬 백엔드 프로세스.
* **MCP Server**: 코어 기능을 도구·리소스·프롬프트로 노출해 AI 코딩 에이전트가 소비하도록 하는 인터페이스.
* **Knowledge Artifact**: YAML Front Matter와 사람이 읽는 Markdown 본문을 담은 생성 Markdown 파일.
* **Hero Scenario**: PoC 가치를 증명하는 주요 엔드투엔드 시연 시나리오.

---

## 부록 B. Hero 시나리오 요약

```text
개발자가 Claude Code에서 낯선 시스템의 변경 작업을 시작한다
    ↓
Claude Code에 연결된 TRACE MCP 서버가 로컬 프로젝트를 분석한다 (analyze_project)
    ↓
에이전트가 Feature Knowledge를 조회한다 (get_feature_knowledge)
    ↓
TRACE가 관련 코드 / API / DB / 설정 / 테스트 / 문서를 근거와 함께 반환한다
    ↓
TRACE가 문서/구현 Conflict를 검출해 경고한다 (get_conflicts)
    ↓
개발자가 입력한다:
"Add SMS verification to Owner registration"
    ↓
에이전트가 analyze_task_impact 를 호출한다
    ↓
Must Change / Likely Change / Review + 관련 기존 충돌 경고
    ↓
TRACE가 근거 기반 Change Plan을 반환하고, 에이전트는 이를 근거로 안전하게 구현을 시작한다
```

이 시나리오는 PoC가 신뢰성 있게 시연해야 하는 최소 엔드투엔드 동작이다. 핵심은 **에이전트가 코드를 짜기 전에 TRACE에게 물어 충돌을 경고받는다**는 것이다.
