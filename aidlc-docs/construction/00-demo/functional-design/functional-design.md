# UOW-00 데모 데이터셋 — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**작성일**: 2026-09-08
**입력**: Q6(Petclinic + 의도적 충돌), unit-of-work.md(UOW-00), 요구사항 §10.5, 부록 B(Hero)
**성격**: 데이터 전제 단위 — 코드 아님. `analyze_project`의 분석 대상 입력.

## 1. 목적

Hero 시나리오(요구사항 §2, 부록 B)를 **결정적으로 재현**할 최소·현실적 데이터셋 구성.
- 다중 자산 범주(source·sql·openapi·test·PDF requirement) → 교차소스 연결 ≥3 (FR-KNOWLEDGE-003).
- 최소 1개 Hero Feature(**Owner Registration**) + 최소 1개 의도적 충돌(value_mismatch).

## 2. Hero Feature & 충돌 설계

- **Feature**: Owner Registration (Owner 등록). 관련 소스: Owner.java, OwnerRestController.java,
  schema.sql, openapi.yaml, OwnerRegistrationTests.java, owner-registration-spec.pdf.
- **의도적 value_mismatch**: 정규화 Claim `Owner.telephone.max_length`
  - 요구(PDF)=**20** vs 명세/구현(OpenAPI·SQL·Java)=**10**.
- **부가(P1) 신호**: 요구 PDF는 SMS 인증을 요구하나 구현 없음 → Hero Task 영향 분석의 근거.

## 3. replay 픽스처 계약 (`demo/replay/*.json`)

`LLMService(replay).structured(step_key)`가 읽는 사전 응답. step_key 규약(UOW-02/03/04가 사용):

| step_key | 산출 |
|---|---|
| `identify_features` | Feature 후보 목록 |
| `extract_claims.<feature_id>` | 정규화 Claim + Evidence |
| `generate_knowledge.<feature_id>` | overview·business_rules·dependencies |
| `analyze_task.<task-slug>` | Must/Likely/Review + change_plan |

> 픽스처 파일은 UOW-02/03/04 코드가 step_key/스키마를 확정하며 함께 생성·검증한다(E2E 그린 기준).
> Confidence 산정·충돌 검출은 LLM이 아닌 **결정적 코드**(UOW-03)이므로 replay 픽스처가 불필요하다.

## 4. 완료조건

- 고정 데이터셋 존재, `analyze_project(demo)`가 소비 가능(경로·파서 대상).
- Hero Feature 1개·의도적 충돌 1개 포함. PDF는 pypdf로 파싱 검증됨(20자·SMS 텍스트 확인).
