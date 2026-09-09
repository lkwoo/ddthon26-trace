# UOW-00 데모 데이터셋 — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-00)
**작성일**: 2026-09-09
**깊이**: Minimal — UOW-00은 실행 코드가 아닌 **정적 픽스처 데이터**. 성능·확장·가용성 등
런타임 NFR은 본질적으로 N/A. 적용되는 NFR은 Functional Design(business-rules R1~R5)에서
이미 확정됐으므로 추가 질문 없이 판정만 기록한다.

> 질문 라운드 생략 사유: 결정성(Q5=A)·발췌 범위(Q4=B)·시크릿 방침은 앞 단계에서 확정됐고,
> 데이터 단위에는 미해결 NFR 트레이드오프가 없다(모호성 없음 → NFR 규칙 Step 3 "질문은 모호할 때").

---

## 1. 적용 NFR (데이터 단위에 유효한 것)

| NFR | 요구 | 근거/출처 | 검증 방법 |
|---|---|---|---|
| **재현성/결정성** (NFR-CORE-002 계열) | 모든 픽스처는 정적, 타임스탬프·난수·환경의존 값 없음 | Q5=A, business-rules R1 | 동일 스캔 재실행 시 assets·parse 결과 동일 |
| **보안-시크릿 위생** (NFR-SEC-001) | 실제 키·비밀번호·개인정보 미포함(플레이스홀더만) | business-rules R2, 원천 §NFR-SEC | git 커밋 전 시크릿 스캔, config는 더미값 |
| **라이선스/출처** | Petclinic 발췌 조각의 출처·Apache-2.0·개변 사실 명시 | Q4=B, domain-entities S6 | `demo/README.md` 상단 고지 존재 |
| **충돌 무결성** | 의도적 충돌 3건(INV-C1~C3)이 데이터에 보존 | business-rules INV-C1~C3 | 데이터셋 무결성 테스트(아래 §3) |
| **자산 다양성** | requirement/api_spec/db_schema/source_code/config/test 각 ≥1 | business-rules R4 | 매니페스트 대조 |

## 2. N/A 판정 (데이터 단위이므로 해당 없음)
- **성능/처리량/지연** — 정적 파일, 런타임 처리 없음 → N/A (파싱 성능은 UOW-01 소관).
- **확장성/부하** — 고정 크기 데모 데이터셋 → N/A.
- **가용성/DR/failover** — 로컬 리포 파일 → N/A (RESILIENCY-02 RTO/RPO=Q11 E=N/A와 일치).
- **인증/인가** — 데이터에 액터 없음 → N/A.
- **관측/로깅** — 코드 없음 → N/A (로깅은 UOW-0F/소비 단위).

## 3. 확장(Extension) 컴플라이언스 요약 — 활성 확장만 평가
활성: **Resiliency Baseline**(Blocking, 전면), **Property-Based Testing**(Blocking, 전면). Security Baseline=미적용.

| 확장 규칙 영역 | 판정 | 근거 |
|---|---|---|
| **Resiliency** — 부분실패 허용/폴백 | **N/A** | 데이터 단위는 실행 경로 없음. 부분 파싱 실패 처리는 이를 소비하는 UOW-01의 책임. |
| **Resiliency** — 재현성(결정적 입력) | **Compliant** | Q5=A 완전 고정 → 소비 단위의 결정적 재현을 데이터가 뒷받침(§1 재현성). |
| **PBT** — 속성 기반 테스트 대상 코드 | **N/A(코드 부재)** | UOW-00에 함수 없음. 단, 아래 대체 검증으로 무결성 보장. |
| **PBT** — 대체 검증(데이터 무결성) | **Compliant(권장 이관)** | 정적 데이터에는 PBT 대신 **불변식 검증 테스트**가 적합: INV-C1~C3·R1~R5를 assert하는 테스트를 **UOW-00 Code Generation** 또는 소비 단위 테스트에 포함. |

**Blocking 판정**: 활성 확장 위반 없음 — N/A 항목은 데이터 단위 특성에 따른 정당한 비적용이며 blocking 아님.
PBT 전면 정책은 "코드 단위"에 적용되고, UOW-00은 무결성 검증 테스트로 정신을 이행한다.

## 4. 다음 단계로 넘기는 컨텍스트
- 런타임 NFR·tech stack 결정 없음 → **NFR Design(UOW-00)은 SKIP** 권장(설계할 패턴 없음).
- Code Generation(UOW-00)에서: 픽스처 파일 생성 + **데이터셋 무결성 테스트**(INV/R 규칙 assert) 포함.
