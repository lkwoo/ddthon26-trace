# TRACE — Developer Knowledge Intelligence Requirements

## 1\. 프로젝트 개요

### 1.0 문제 정의 (PROBLEM-001)

**누가:** 낯선 코드베이스에 갓 투입된 개발자, 문서와 구현의 드리프트를 쫓는 유지보수자, 변경의 파급 범위를 가늠해야 하는 기획자(PM).

**언제·얼마나 자주:** 변경 티켓을 받을 때마다(상시 발생). 예를 들어 "Owner 등록에 SMS 인증을 추가하라"는 작업 하나를 받으면, 요구사항 문서·OpenAPI 명세·소스 코드·DB 스키마·테스트를 **각각 따로 열어 수작업으로 대조**해야 한다.

**무엇이 아픈가:**

* 정보가 **파일 단위로 흩어져** 있어 "기능 단위"로 재구성되지 않는다. 하나의 기능을 이해하려면 여러 파일을 사람이 머릿속에서 이어붙여야 한다.
* 문서와 구현이 **서로 어긋나 있어도 아무도 모른 채** 개발이 진행된다. (예: 요구사항은 전화번호 최대 20자, OpenAPI·코드는 10자.)
* 그 결과 **놓친 컴포넌트와 충돌이 구현을 마친 뒤에야** 드러나 재작업·장애로 이어진다.

한마디로: **"이 작업과 무엇이 관련돼 있고, 무엇이 어긋나 있으며, 무엇을 먼저 검토·변경해야 하는가"**를 구현 착수 전에 알 방법이 없다.

### 1.1 제품 비전

TRACE는 흩어진 소프트웨어 개발 자산을 분석해 **기능(Feature) 중심의, 근거로 뒷받침되는 개발 지식**으로 재구성하는 개발자 지식 인텔리전스 시스템이다.

개발자·유지보수자·기획자가 낯선 시스템을 빠르게 이해하고, 개발 산출물 사이의 불일치를 발견하며, 계획한 변경의 영향 범위를 **구현 전에** 평가하도록 돕는다.

TRACE의 핵심 목적은 파편화된 프로젝트 자산을 **변경 인지(change-aware)·추적 가능(traceable)·검증 가능(verifiable)한 지식**으로 바꾸는 것이다. (로컬 우선 실행·웹 UI 등 전달 방식은 2장·13장 참조.)

### 1.2 핵심 가치 제안

* 파일 중심 정보를 **기능 중심 지식(Feature-centric Knowledge)**으로 전환한다.
* 중요한 지식을 **주장 → 근거 → 신뢰도 → 충돌(Claim → Evidence → Confidence → Conflict)** 구조로 연결한다.
* 요구사항·API 명세·소스 코드·DB 정의·설정·테스트 사이의 불일치를 검출한다.
* 개발 작업을 분석해 그 변경이 미칠 영향 범위를 식별한다.
* 근거 없는 LLM 추측이 아니라 **근거로 뒷받침되는 변경 권고**를 제공한다.
* 동일한 지식을 사람에게는 웹 UI로, 향후 AI 에이전트에게는 도구 인터페이스로 노출한다.

### 1.3 제품 포지셔닝

TRACE는 소스 저장소·위키·Obsidian·RAG·코딩 어시스턴트를 대체하지 않는다. **원시 개발 자산과 사람/AI 개발 워크플로우 사이에 놓이는 지식 계층**이다.

**개발 프로세스상 위치 — 구현 착수 직전(pre-implementation):** TRACE는 코드를 짜기 전에 개입해 "무엇이 관련돼 있고, 무엇이 어긋나 있으며, 무엇을 먼저 검토·변경해야 하는가"를 근거와 함께 제시한다. 온보딩·유지보수·변경 계획이라는 세 진입점은 3장에서 다룬다.

**구조적 차별 — "비슷한 것 찾기" vs "어긋난 것 찾기":** 기존 도구와의 차이는 표현이 아니라 데이터 구조에서 나온다.

| 구분 | RAG / 위키 / 코딩 어시스턴트 | TRACE |
| --- | --- | --- |
| 데이터 단위 | 유사 청크 / 파일 / 자유 텍스트 | **정규화된 Claim** (subject + predicate + value) |
| 답의 형태 | "관련 있어 보이는" 텍스트 반환 | **Claim↔Evidence 링크 + 교차 소스 값 비교** |
| 불일치 처리 | 감지하지 못하고 요약만 함 | **value_mismatch를 1급 산출물로 검출** |
| 신뢰 근거 | LLM의 자기 확신 | **근거 일치도 기반 Confidence** |

> RAG는 **'비슷한 것'**을 찾고, TRACE는 **'어긋난 것'**을 찾는다. 이 구조적 차이는 8장(Claim·Evidence·Conflict 모델)에서 설계로 구체화된다.

\---

## 2\. Project Constraints

### 2.1 Development Constraints

* Development team: 5 members
* Development period: 2 days
* Primary objective: prove the core idea through a reliable end-to-end PoC
* Secondary objective: provide a clear and intuitive demo
* Production-grade scalability is not required
* Complex authentication, organization-level authorization, and cloud infrastructure are out of scope for the PoC unless required for demonstration

### 2.2 Priority Principles

Requirements are classified as:

* **P0** — Required to prove the core product value
* **P1** — Strongly improves demo quality or evaluation score
* **P2** — Useful for production evolution but not required for the PoC
* **Out of Scope** — Explicitly excluded from the current implementation

### 2.3 Evaluation-Oriented Constraints

Implementation decisions should favor the following:

1. Clear demonstration of AI-assisted software development
2. Strong problem-solution fit
3. Differentiation from generic Wiki/RAG/chatbot systems
4. Reliable end-to-end demo behavior
5. Simple and understandable UX
6. Maintainable modular code
7. Evidence-backed AI results
8. Basic security hygiene

\---

## 3\. Target Users and Usage Contexts

### 3.1 Developer — Understand

**Primary Question**

> "Where do I need to make changes?"

**Scenario**

A developer unfamiliar with the system receives a change task → explores Feature Knowledge to understand the current system → identifies conflicts between documentation and implementation → runs Task Impact Analysis → receives an evidence-backed Change Plan.

**Expected Value**

* Faster system understanding
* Reduced manual repository exploration
* Visibility into related code, API, DB, configuration, tests, and documents
* Reduced risk of missing affected components

### 3.2 Maintainer — Maintain

**Primary Question**

> "Why did this problem happen, and what else must be fixed?"

**Scenario**

A maintainer investigates an operational issue or policy mismatch → opens the relevant Feature Knowledge → reviews code/API/DB/configuration evidence → identifies conflicts or stale knowledge → checks impacted areas → receives a Maintenance Plan including tests and documentation that should also be updated.

**Expected Value**

* Faster narrowing of root-cause candidates
* Detection of documentation/implementation drift
* Better awareness of related change scope
* Reduced recurrence caused by incomplete fixes

### 3.3 Product Manager / Planner — Plan Change

**Primary Question**

> "If this requirement changes, how far will the impact spread?"

**Scenario**

A PM evaluates a new requirement or policy change → reviews the current Feature Knowledge → identifies mismatches between documented requirements and implementation → submits the proposed change for Task Impact Analysis → receives an implementation scope, risk summary, and pre-development decision points.

**Expected Value**

* Better understanding of current behavior without manually reading code
* Earlier visibility into implementation complexity
* Better requirement-to-development communication
* Early discovery of constraints and conflicting policies

\---

## 4\. System Composition

### 4.1 Main Components

TRACE shall consist of the following logical components.

#### A. Local Web UI

A browser-based interface running on localhost.

Responsibilities:

* Display the currently loaded project
* Trigger analysis
* Show detected Features
* Render Human-friendly Knowledge
* Show Evidence, Confidence, and Conflict
* Accept development task input
* Display Task Impact Analysis and Change Plan
* Display analysis progress and failures

#### B. Local Knowledge Engine

A local backend process with direct filesystem access to the selected project.

Responsibilities:

* Scan project files
* Classify supported artifacts
* Parse and normalize content
* Run AI workflows
* Build structured knowledge
* Persist generated knowledge
* Serve results to the Web UI

#### C. AI Workflow Layer

Responsibilities:

* Feature identification
* Structured extraction
* Claim normalization
* Evidence grouping
* Confidence determination
* Conflict detection
* Feature Knowledge generation
* Task Impact Analysis
* Change Plan generation

#### D. Knowledge Storage

For the PoC, knowledge shall be stored locally.

Preferred representation:

```text
knowledge/
  features/
    <feature-id>.md
```

Each Feature Knowledge file should contain:

* YAML Front Matter for structured/machine-readable data
* Markdown body for human-readable explanation

The Web UI shall render structured YAML fields as UI components where appropriate and render the Markdown body as human-readable content.

\---

## 5\. Project Input Requirements

### 5.1 Project Selection

**FR-PROJECT-001 — Local Project Loading — P0**

The user shall be able to start TRACE with a local project directory.

Preferred PoC usage:

```bash
trace serve <project-path>
```

Example:

```bash
trace serve ./spring-petclinic-rest
```

Alternative PoC implementation:

* Start the local Web UI
* Enter a local directory path in the UI
* The Local Knowledge Engine validates and loads the directory

**Acceptance Criteria**

* A valid directory can be loaded
* Invalid or inaccessible paths return a clear error
* The Web UI displays the loaded project name and detected asset summary

### 5.2 Supported Asset Types

**FR-PROJECT-002 — Asset Discovery — P0**

The system shall discover and classify the following artifact categories where present:

* Source Code
* Markdown / text documentation
* PDF documents
* API specifications such as OpenAPI / Swagger YAML or JSON
* SQL schema or migration files
* YAML / properties / environment-style configuration
* Test source files

**P1**

* PPT/PPTX
* DOC/DOCX

For each discovered file, TRACE shall record at least:

* Path
* Artifact type
* File name
* Optional language/type metadata
* Parsing status

### 5.3 File Filtering

**FR-PROJECT-003 — Exclusion Rules — P0**

The analyzer shall exclude common non-source directories and generated artifacts by default.

Examples:

* `.git`
* `node\_modules`
* `build`
* `dist`
* `target`
* binary files
* IDE metadata
* dependency caches

Exclusion rules should be configurable through a simple configuration file or centralized constant.

\---

## 6\. Project Analysis Requirements

### 6.1 Analysis Trigger

**FR-ANALYSIS-001 — Analyze Project — P0**

The Web UI shall provide an `Analyze Project` action.

When triggered, the Local Knowledge Engine shall:

1. Scan supported files
2. Parse relevant content
3. Extract structured information
4. Identify candidate Features
5. Extract Claims and Evidence
6. Detect Conflicts
7. Generate Feature Knowledge
8. Persist results
9. Return an analysis summary

### 6.2 Analysis Progress

**FR-ANALYSIS-002 — Progress Visibility — P1**

The Web UI should display high-level progress, for example:

```text
Scanning project
Parsing sources
Extracting features
Building knowledge
Detecting conflicts
Generating feature views
```

The UI should not expose internal chain-of-thought reasoning.

### 6.3 Partial Failure

**FR-ANALYSIS-003 — Fault Tolerance — P0**

Failure to parse one file shall not terminate the entire project analysis.

The system shall:

* Mark the failed file
* Log the failure
* Continue analyzing other files where possible
* Inform the user that analysis completed with warnings

\---

## 7\. Feature-Centric Knowledge Requirements

### 7.1 Feature Definition

A **Feature** is the top-level knowledge container representing a user-visible capability, business capability, or cohesive functional behavior.

Examples:

* User Registration
* Owner Registration
* Pet Registration
* Visit Management
* Authentication

A Feature is not a single fact. It groups the knowledge required to understand or change that behavior.

A Feature may contain:

* Claims
* Evidence
* Conflicts
* Related source code
* APIs
* Database structures
* Configuration
* Tests
* Documents
* Dependencies

### 7.2 Feature Identification

**FR-KNOWLEDGE-001 — Feature Detection — P0**

The AI workflow shall identify a small set of meaningful Features from analyzed project assets.

The PoC should prioritize quality over exhaustive coverage.

**Acceptance Criteria**

For the demo project, at least one Hero Feature must be correctly identified and contain cross-source evidence from multiple artifact types.

### 7.3 Feature Knowledge View

**FR-KNOWLEDGE-002 — Feature Knowledge — P0**

For each Feature, TRACE shall generate a human-friendly knowledge view containing, where available:

* Overview
* Business Rules
* Related Source Code
* Related APIs
* Database
* Configuration
* Tests
* Known Conflicts
* Source Evidence
* Dependencies
* Optional Change Notes

### 7.4 Required Cross-Source Association

**FR-KNOWLEDGE-003 — Cross-Source Linking — P0**

For the Hero Feature, TRACE shall associate at least three different artifact categories.

Preferred demonstration:

```text
Requirement / Manual
API Specification
Source Code
Database
Configuration
Test
```

The PoC is not required to infer every relationship in the repository.

\---

## 8\. Claim, Evidence, Confidence, and Conflict Model

### 8.1 Claim

A **Claim** is the smallest normalized unit of knowledge that represents a verifiable statement about the system.

Recommended conceptual model:

```text
Subject + Predicate + Value
```

Examples:

```text
user.password + min\_length + 10
owner.telephone + max\_length + 10
POST /api/owners + authentication\_required + true
```

### 8.2 Claim Requirements

**FR-CLAIM-001 — Claim Extraction — P0**

The system shall extract normalized Claims for selected business or technical rules relevant to the Hero Feature.

Claims should be atomic.

Bad:

```text
Registration uses email, password length is 10, and verification is mandatory.
```

Good:

```text
user.email.required = true
user.password.min\_length = 10
user.email\_verification.required = true
```

### 8.3 Evidence

**FR-EVIDENCE-001 — Evidence Association — P0**

Each important Claim shall have one or more Evidence records where evidence exists.

Each Evidence record shall include:

* Source path
* Source type
* Source location when available
* Extracted value or relevant fact
* Relation to the Claim

Recommended relation types:

* `direct`
* `supporting`
* `related`
* `contradicting`

Example:

```yaml
evidence:
  - source: src/main/java/User.java
    location: line 42
    type: source\_code
    relation: direct
    extracted\_value: 10
```

### 8.4 Confidence

**FR-CONFIDENCE-001 — Confidence Level — P1**

TRACE should assign a confidence level to important Claims.

Allowed PoC values:

* `HIGH`
* `MEDIUM`
* `LOW`

Confidence should be based primarily on evidence quality and agreement, not solely on the LLM's self-reported probability.

Example interpretation:

* HIGH: multiple strong sources agree
* MEDIUM: limited evidence or partial agreement
* LOW: weak, ambiguous, or conflicting evidence with no clear effective behavior

### 8.5 Conflict

A **Conflict** exists when evidence associated with the same normalized Claim disagrees or when expected and effective behavior diverge.

**FR-CONFLICT-001 — Value Mismatch — P0**

TRACE shall detect direct value mismatches for normalized Claims.

Example:

```text
Requirement: password minimum length = 8
OpenAPI:     password minimum length = 10
Code:        password minimum length = 10
```

### 8.6 Supported Conflict Types

PoC priority:

1. `value\_mismatch` — P0
2. `missing\_implementation` — P1
3. `undocumented\_behavior` — P1
4. `structural\_mismatch` — P1

The implementation may only fully support `value\_mismatch` if time is constrained.

### 8.7 Effective vs Expected Behavior

Where possible, TRACE should distinguish:

* **Expected Behavior** — requirement or specification intent
* **Effective Behavior** — likely runtime behavior represented by code/config/test

TRACE must not automatically assume that source code is always correct.

\---

## 9\. Knowledge File Requirements

### 9.1 Storage Format

**FR-STORAGE-001 — Markdown + YAML Front Matter — P0**

Each generated Feature Knowledge artifact shall use a Markdown file with YAML Front Matter.

Example:

```markdown
---
id: feature.owner-registration
type: feature
title: Owner Registration
confidence: high

claims:
  - id: owner.telephone.max\_length
    subject: owner.telephone
    predicate: max\_length
    value: 10
    confidence: high
    conflict: true

related\_files:
  - src/main/java/.../OwnerController.java
  - src/main/java/.../Owner.java

apis:
  - method: POST
    path: /api/owners
---

# Owner Registration

## Overview

Human-readable feature description.

## Business Rules

...

## Known Conflicts

...
```

### 9.2 Data Ownership Rule

Structured facts shall preferably be represented once in canonical YAML fields.

The Markdown body should explain or contextualize those facts.

The system should avoid independently maintaining the same mutable value in multiple places where practical.

### 9.3 Human View

**FR-STORAGE-002 — Human-friendly Rendering — P0**

The Web UI shall not require users to read raw YAML.

The Viewer shall:

* Parse YAML Front Matter
* Render structured fields as cards, badges, tables, lists, or metadata
* Render the Markdown body as formatted human-readable content

Example UI metadata:

```text
HIGH CONFIDENCE
1 CONFLICT
6 RELATED SOURCES
```

### 9.4 Generated Artifact Policy

Generated Knowledge should be treated as system-generated output.

Manual editing of generated Feature Knowledge is not required for the PoC.

Future systems may support human correction or override workflows.

\---

## 10\. Conflict Detection UX Requirements

### 10.1 Conflict Summary

**FR-UI-CONFLICT-001 — Conflict Visibility — P0**

A Feature page shall prominently show the number of detected Conflicts.

Example:

```text
Owner Registration
HIGH CONFIDENCE    ⚠ 1 CONFLICT
```

### 10.2 Conflict Detail

For a detected conflict, the UI shall display:

* Claim/topic
* Conflicting values
* Sources
* Source locations where available
* Short interpretation

Example:

```text
Telephone Maximum Length

Requirement     20
OpenAPI         10
Source Code     10

Interpretation:
The API and runtime validation use 10, while the requirement document specifies 20.
```

### 10.3 Evidence Navigation

**FR-UI-CONFLICT-002 — Evidence Reference — P0**

Users shall be able to see which source files support each conflicting value.

Direct file opening is optional for the PoC.

\---

## 11\. Task Impact Analysis Requirements

### 11.1 Task Input

**FR-IMPACT-001 — Development Task Input — P0**

The Web UI shall allow the user to submit a natural-language change request.

Hero example:

> `Add SMS verification to Owner registration.`

### 11.2 Context Selection

**FR-IMPACT-002 — Knowledge-grounded Analysis — P0**

Task Impact Analysis shall use existing Feature Knowledge and Evidence as context.

The analysis must not rely only on a generic LLM prompt over the task text.

### 11.3 Impact Output

**FR-IMPACT-003 — Impact Classification — P0**

The result shall classify impact candidates using at least:

* **Must Change**
* **Likely Change**
* **Review**

Each result should include a reason.

Example:

```text
Must Change
- OwnerController.java
  Reason: Handles owner registration requests.

- openapi.yaml
  Reason: Registration API contract must include verification behavior.

Likely Change
- application.yml
  Reason: SMS provider configuration may be required.

Review
- Database schema
  Reason: Required only if verification state is persisted.
```

### 11.4 Related Existing Conflicts

**FR-IMPACT-004 — Conflict-aware Impact — P1**

If an existing Conflict is relevant to the submitted Task, TRACE should highlight it before recommending implementation changes.

Example:

```text
Existing Conflict Relevant to This Change:
Telephone length differs between requirement and implementation.
Resolve the validation policy before implementing SMS verification.
```

### 11.5 Impact Evidence

**FR-IMPACT-005 — Evidence-backed Recommendation — P0**

Recommended files or components should include a brief reason and reference to supporting knowledge where possible.

### 11.6 Change Plan

**FR-IMPACT-006 — Change Plan — P0**

TRACE shall produce a concise ordered Change Plan.

Example:

1. Resolve current telephone validation policy
2. Define SMS verification API behavior
3. Update owner registration flow
4. Add provider configuration
5. Add success/failure/timeout tests
6. Update requirement documentation

The Change Plan is advisory and shall not automatically modify source code in the PoC.

\---

## 12\. Web UI Requirements

### 12.1 Main Demo Flow

The user experience shall support this sequence:

```text
Load Project
    ↓
Analyze Project
    ↓
Detected Features
    ↓
Feature Knowledge
    ↓
Evidence / Conflict
    ↓
Enter Development Task
    ↓
Task Impact Analysis
    ↓
Change Plan
```

### 12.2 Main Screens / Views

#### View A — Project Overview

Must show:

* Project name/path
* Detected asset counts by category
* Analysis status
* Analyze/Re-analyze action

#### View B — Feature List

Must show:

* Feature title
* Short summary
* Confidence where available
* Conflict count

#### View C — Feature Detail

Must show:

* Overview
* Related assets
* Claims / business rules
* Evidence
* Confidence
* Conflicts

#### View D — Impact Analysis

Must show:

* Task input
* Related Feature
* Must Change
* Likely Change
* Review
* Risks / cautions where available
* Relevant existing conflicts
* Change Plan

### 12.3 UX Principles

**NFR-UX-001 — Explainability**

Users shall be able to understand why an AI result was produced without asking a follow-up question.

**NFR-UX-002 — Progressive Disclosure**

The default view should prioritize:

1. Feature summary
2. Conflict
3. Impact
4. Evidence

Low-level metadata should be accessible but not dominate the first screen.

**NFR-UX-003 — Demo Clarity**

A first-time evaluator should understand the basic value within approximately 30 seconds of viewing the main flow.

\---

## 13\. Local Engine Requirements

### 13.1 Local-first Execution

**NFR-LOCAL-001 — Local File Access — P0**

The Knowledge Engine shall execute locally and access project files directly from the local filesystem.

The browser itself shall not be responsible for unrestricted filesystem access.

### 13.2 UI/Engine Boundary

The UI shall invoke backend/core functions rather than embedding all AI logic directly into UI button handlers.

Recommended interfaces:

```text
scan\_project(path)
analyze\_project(path)
list\_features()
get\_feature\_knowledge(feature\_id)
get\_conflicts(feature\_id)
analyze\_task\_impact(task, feature\_id?)
```

### 13.3 Reusability

The core analysis functions should be reusable by future interfaces such as:

* CLI
* MCP server
* IDE extension
* CI validation

A future adapter is not required for P0.

\---

## 14\. AI Workflow Requirements

### 14.1 Required Workflow

The PoC AI pipeline should conceptually follow:

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

Task analysis:

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

### 14.2 Structured AI Output

**NFR-AI-001 — Machine-parseable Output — P0**

Where AI output feeds later processing stages, the system should request structured JSON/YAML-compatible output rather than free-form prose.

### 14.3 Grounding

**NFR-AI-002 — Evidence Grounding — P0**

AI-generated Claims, Conflicts, and Impact recommendations must reference analyzed project assets where possible.

### 14.4 Hallucination Handling

**NFR-AI-003 — Uncertainty — P0**

When the system lacks sufficient evidence, it shall not present unsupported conclusions as certain.

Preferred language:

* `Review`
* `Potential impact`
* `Insufficient evidence`
* `Confidence: LOW`

### 14.5 Determinism

**NFR-AI-004 — Demo Stability — P1**

For the fixed demo dataset, prompts and model parameters should favor stable and repeatable output.

The project may use cached analysis results as a demo fallback if live AI execution fails.

\---

## 15\. Non-Functional Requirements

### 15.1 Performance

**NFR-PERF-001**

The PoC should optimize for a small demonstration repository or curated subset rather than large-scale enterprise repositories.

**NFR-PERF-002**

The UI shall remain responsive while analysis runs.

**NFR-PERF-003**

Repeated viewing of previously generated Feature Knowledge should not require unnecessary LLM calls.

### 15.2 Reliability

**NFR-REL-001**

The Hero Scenario must complete end-to-end without manual file editing during the demo.

**NFR-REL-002**

If AI analysis fails, the UI shall display a readable failure message and log diagnostic details.

### 15.3 Maintainability

**NFR-MAINT-001**

The codebase should separate at least:

* UI
* Source scanning/parsing
* AI workflow
* Knowledge model/storage
* Conflict detection
* Impact analysis
* Configuration

**NFR-MAINT-002**

Prompts should be stored separately from UI code where practical.

### 15.4 Logging

**NFR-LOG-001**

The system shall log:

* Project scan start/end
* Parsing failures
* AI request failures
* Knowledge generation status
* Conflict detection count
* Task impact analysis status

Logs must not intentionally expose secrets.

\---

## 16\. Security and Privacy Requirements

### 16.1 Secrets

**NFR-SEC-001 — No Hard-coded Secrets — P0**

API keys, tokens, and credentials must not be hard-coded in source code.

Use environment variables or local configuration.

### 16.2 Local Project Privacy

**NFR-SEC-002 — Local-first Handling — P0**

Raw project files shall remain local except for content explicitly sent to the configured LLM provider.

### 16.3 Sensitive Data Awareness

**NFR-SEC-003 — P1**

The architecture should provide a future insertion point for:

* Secret filtering
* PII filtering
* Sensitive file exclusion
* Private enterprise model endpoints

Full DLP implementation is not required for the PoC.

### 16.4 Path Validation

**NFR-SEC-004**

If the Web UI accepts a local filesystem path, the backend shall validate that it exists and is a directory before analysis.

\---

## 17\. Error Handling Requirements

### 17.1 Unsupported File

Unsupported files shall be skipped and recorded as ignored.

### 17.2 Parser Failure

Parser failure shall produce:

* File path
* Error category
* Warning status

The overall project analysis should continue.

### 17.3 LLM Failure

If the LLM request fails due to timeout, quota, or provider error:

* Display a user-friendly error
* Preserve previously generated knowledge
* Log technical details
* Allow retry where practical

### 17.4 Invalid Structured Output

If AI output cannot be parsed into the expected schema:

* Retry with a constrained correction prompt where practical
* Otherwise mark the affected analysis stage as failed
* Do not silently save malformed knowledge

\---

## 18\. Demo Dataset Requirements

### 18.1 Preferred Dataset

The PoC should use a curated public software project or subset with multiple engineering artifact types.

Recommended example:

* Spring Petclinic REST or a curated subset

### 18.2 Synthetic Supporting Documents

The demo may add realistic synthetic enterprise-style artifacts to improve cross-source coverage.

Examples:

* Requirement PDF
* Architecture PPT/PPTX
* Manual DOCX

### 18.3 Intentional Conflict

The demo dataset shall include at least one intentional, easy-to-understand conflict.

Example:

```text
Requirement:
Owner telephone max length = 20

OpenAPI:
maxLength = 10

Source Code:
@Size(max = 10)
```

### 18.4 Hero Task

Preferred Hero Task:

> `Add SMS verification to Owner registration.`

The dataset shall contain enough related code/API/config/test/document assets for the system to demonstrate meaningful Task Impact Analysis.

\---

## 19\. MVP Scope

### 19.1 P0 — Required

* Local project loading
* Source asset discovery
* Parsing of core text/code/config/API/DB/test artifacts
* Feature detection
* Feature-centric Knowledge generation
* Claim extraction
* Evidence association
* Value-based Conflict Detection
* Source Citation / Evidence display
* Markdown + YAML Front Matter knowledge persistence
* Human-friendly Feature Viewer
* Natural-language Task input
* Task Impact Analysis
* Must Change / Likely Change / Review classification
* Change Plan
* Local Web UI
* Basic error handling
* Environment-based LLM secret management

### 19.2 P1 — High-value if Time Allows

* PDF parsing if not included in P0 parser set
* DOCX/PPTX parsing
* Confidence scoring
* Missing implementation detection
* Undocumented behavior detection
* Conflict-aware Impact Analysis
* Analysis progress UI
* Cached/fallback demo results
* Simple CLI launcher
* Basic knowledge refresh / re-analysis
* Risk summary

### 19.3 P2 — Post-PoC

* Semantic search
* General repository chat
* Vector database
* Knowledge graph
* Automatic Git change monitoring
* Knowledge drift detection
* GitHub integration
* CI validation
* MCP server
* IDE extension
* User authentication and RBAC
* Multi-project workspace
* Cloud deployment
* Large repository optimization

### 19.4 Out of Scope

* Automatic source code modification
* Full autonomous coding agent
* Production-grade enterprise permissions
* Real-time collaboration
* Windows-native desktop application
* Full repository-scale static analysis
* Full formal verification of software behavior

\---

## 20\. Definition of Done

The PoC is considered complete when all of the following are true.

### Project Analysis

* A local demo project can be loaded
* Multiple artifact types are detected
* Analysis completes without manual intervention

### Feature Knowledge

* At least one Hero Feature is identified correctly
* The Feature page links multiple source categories
* Important Claims have Evidence
* At least one Conflict is detected and clearly explained

### Task Impact

* A user can enter the Hero Task
* TRACE identifies relevant files/components
* Impact is separated into Must Change / Likely Change / Review
* Recommendations contain reasons or evidence
* A Change Plan is generated

### UX

* The evaluator can follow:

```text
Project → Analyze → Feature → Conflict → Task → Impact → Change Plan
```

without needing to inspect raw generated files.

### Engineering Quality

* No hard-coded LLM secrets
* Core logic is separated from UI code
* Analysis failures are logged
* Generated knowledge is persisted
* The Hero Scenario is repeatable for the demo

\---

## 21\. AI-DLC Traceability Requirements

The repository should preserve evidence that the project was developed using an AI-DLC process.

Recommended structure:

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

At minimum, the project should preserve:

* Problem Statement
* Target Users
* Hero Scenario
* Requirements
* Scope decisions
* Architecture decisions
* Unit of Work definitions
* Prompt or AI collaboration evidence
* Test evidence
* Human approval / review records

Requirements in this document should be referenced by ID in Architecture Decisions, Units of Work, and tests where practical.

Example:

```text
UOW-03 Conflict Detection
Implements:
- FR-CLAIM-001
- FR-EVIDENCE-001
- FR-CONFLICT-001
- FR-UI-CONFLICT-001
```

\---

## 22\. Suggested Unit of Work Boundaries

The following boundaries are recommendations for AI-DLC Construction planning, not mandatory implementation modules.

### UOW-01 — Project Scanner \& Parser

Related requirements:

* FR-PROJECT-001
* FR-PROJECT-002
* FR-PROJECT-003
* FR-ANALYSIS-003

### UOW-02 — Feature \& Knowledge Generation

Related requirements:

* FR-ANALYSIS-001
* FR-KNOWLEDGE-001
* FR-KNOWLEDGE-002
* FR-KNOWLEDGE-003
* FR-STORAGE-001

### UOW-03 — Claims, Evidence \& Conflict

Related requirements:

* FR-CLAIM-001
* FR-EVIDENCE-001
* FR-CONFIDENCE-001
* FR-CONFLICT-001
* FR-UI-CONFLICT-001
* FR-UI-CONFLICT-002

### UOW-04 — Task Impact Analysis

Related requirements:

* FR-IMPACT-001
* FR-IMPACT-002
* FR-IMPACT-003
* FR-IMPACT-004
* FR-IMPACT-005
* FR-IMPACT-006

### UOW-05 — Local Web UI

Related requirements:

* FR-STORAGE-002
* FR-UI-CONFLICT-001
* FR-UI-CONFLICT-002
* Section 12 Web UI Requirements

### UOW-06 — Integration, Reliability \& Demo

Related requirements:

* NFR-AI-003
* NFR-AI-004
* NFR-REL-001
* NFR-REL-002
* Section 17 Error Handling
* Section 18 Demo Dataset
* Section 20 Definition of Done

\---

## 23\. Open Decisions

The following decisions may be finalized during AI-DLC Architecture/Inception activities:

1. Final project name (`TRACE` is used as the working name in this document)
2. Streamlit vs separate FastAPI + Web Frontend
3. Exact LLM provider/model
4. Exact parser library choices
5. Whether PDF/DOCX/PPTX support is P0 or P1
6. Exact YAML schema
7. Confidence calculation policy
8. Whether Feature detection is fully automatic or assisted by demo configuration
9. Whether analysis results are cached for demo fallback
10. Whether a minimal CLI wrapper is implemented

Critical unresolved decisions must be recorded before Construction begins.

\---

## Appendix A. Terminology

* **Feature**: A top-level functional knowledge container used to group information needed to understand or change a software capability.
* **Claim**: A normalized, verifiable statement about the system.
* **Evidence**: A source-backed fact supporting, relating to, or contradicting a Claim.
* **Confidence**: An indication of how strongly the available evidence supports a Claim.
* **Conflict**: A disagreement or mismatch between evidence associated with the same normalized Claim.
* **Feature Knowledge**: Human- and AI-consumable knowledge organized around a Feature rather than a file.
* **Task Impact Analysis**: Analysis of what project assets may need to change or be reviewed for a proposed development task.
* **Change Plan**: An ordered, evidence-informed set of recommended implementation/review steps.
* **Local Engine**: The local backend process that scans project files, runs AI workflows, and manages generated knowledge.
* **Knowledge Artifact**: A generated Markdown file containing YAML Front Matter and a human-readable Markdown body.
* **Hero Scenario**: The primary end-to-end demo scenario used to prove the PoC value.

\---

## Appendix B. Hero Scenario Summary

```text
A developer unfamiliar with the system receives a change task
    ↓
TRACE analyzes the local project
    ↓
The developer opens Feature Knowledge
    ↓
TRACE shows related code / API / DB / config / tests / documents
    ↓
TRACE shows Evidence and detects a documentation/implementation Conflict
    ↓
The developer submits:
"Add SMS verification to Owner registration"
    ↓
TRACE performs Task Impact Analysis
    ↓
Must Change / Likely Change / Review
    ↓
TRACE generates an evidence-backed Change Plan
```

This scenario is the minimum end-to-end behavior that the PoC must reliably demonstrate.

