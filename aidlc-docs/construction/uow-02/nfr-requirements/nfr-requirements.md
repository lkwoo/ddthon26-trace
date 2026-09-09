# UOW-02 (Feature & Knowledge) — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-02)
**작성일**: 2026-09-09
**결정 반영**: Q1=B(발췌 4,000자·max_features 무제한), Q2=A,B,C,D(PBT 4속성), Q3=B(옵트인 실API 통합 테스트), Q4=A(캐시 손상=미스 폴백)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 1. LLM 비용/토큰 (Q1=B)
| ID | 요구 | 값 |
|---|---|---|
| NFR-02-COST-1 | 자산 발췌 상한 | 자산당 excerpt **4,000자**(초과 절단, 개행 정규화 유지) |
| NFR-02-COST-2 | Feature 식별 개수 | **max_features 무제한**(모델 판단). 단 중복 제거·id 안전화·정렬은 유지(BR-IDF-004/005) |
| NFR-02-COST-3 | 결정성 파라미터 | temperature=0·seed 등은 LLMSettings에서만(UOW-0F, 하드코딩 금지) |
| NFR-02-COST-4 | max_tokens | LLMSettings 기본(4096) 사용, 필요 시 설정으로 상향 |

> 비고: Q1=B는 정밀도를 위해 넉넉한 상한을 택함. 발췌 4,000자·무제한 Feature는 데모 규모에서 실용적이며,
> 대규모에서 토큰이 커질 수 있음은 수용된 트레이드오프(로컬 도구 성격).

## 2. 성능/캐시 (NFR-PERF-003)
| ID | 요구 |
|---|---|
| NFR-02-PERF-1 | 자산 불변 시 2회차 분석은 **LLM 미호출**(캐시 히트) — FakeLLM 호출 카운트로 검증. |
| NFR-02-PERF-2 | 캐시 키는 자산 콘텐츠 해시(순서 무관·내용 민감) — BR-CACHE-001. |

## 3. 신뢰성 (Resiliency 전면)
| ID | 요구 |
|---|---|
| NFR-02-REL-1 | identify_features 검증 소진 실패 → 빈 목록 + warning(analyze 계속) — BR-FAIL-002. |
| NFR-02-REL-2 | Feature별 지식 생성 실패 격리: 한 Feature 실패가 다른 Feature·전체를 막지 않음 — BR-FAIL-001. |
| NFR-02-REL-3 | 지식 본문 LLM 실패 시 템플릿 폴백으로 저장 계속 — BR-KN-002. |
| NFR-02-REL-4 | 캐시 손상/스키마 불일치 → 미스로 간주 조용히 재분석(Q4=A). |

## 4. 보안
| ID | 요구 |
|---|---|
| NFR-02-SEC-1 | 프롬프트 발췌는 상한 내로 제한(대량 원문 유출·토큰 폭증 방지) — BR-SEC-002. |
| NFR-02-SEC-2 | 경고/로그에 자산 원문·시크릿 비노출(rel_path·feature_id·코드만) — BR-SEC-001. |
| NFR-02-SEC-3 | 저장/캐시 경로는 항상 프로젝트 루트 하위(.trace) — 트래버설 금지, BR-STORE-001. |
| NFR-02-SEC-4 | API 키는 소비 직전 env late-lookup(UOW-0F), 코드/로그/캐시에 값 미포함. |

## 5. 재현성 & 테스트 정책 (Q3=B)
| ID | 요구 |
|---|---|
| NFR-02-TST-1 | **기본 테스트는 전량 FakeLLMClient(오프라인)** — 네트워크·실키 불필요, 결정적. |
| NFR-02-TST-2 | **옵트인 실 API 통합 테스트**(Q3=B): `@pytest.mark.llm_integration`, 환경변수
  `TRACE_RUN_LLM_INTEGRATION=1` + 유효 키가 있을 때만 실행. 기본 CI에서는 skip. |
| NFR-02-TST-3 | 동일 자산·동일 FakeLLM 응답 → 동일 저장 결과(결정성). |

## 6. PBT 속성 (Q2=A,B,C,D — 전면)
| ID | 속성 |
|---|---|
| PBT-02-A | id 안전화 전결정성: 임의 title/후보 id → 항상 파일/URI 안전 id(`/\..` 없음, 비어있지 않음) |
| PBT-02-B | 캐시 해시 안정성: 자산 순서 섞어도 동일 해시; content 1바이트 변경 시 상이 |
| PBT-02-C | 카탈로그 발췌 상한: 임의 길이 content → excerpt ≤ 상한, 개행 정규화 유지 |
| PBT-02-D | 저장 round-trip: 임의 FeatureKnowledge 셸 → save→load 동일(멱등) |

## 7. 유지보수성
| ID | 요구 |
|---|---|
| NFR-02-MAINT-1 | 프롬프트 내용은 파일 템플릿(C8)로 코드와 분리 — NFR-MAINT-002. |
| NFR-02-MAINT-2 | 상한/설정은 config 계층 또는 명시 인자(하드코딩 최소화). |

## 8. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | §3 부분실패 격리·폴백·캐시 안전 폴백. |
| Property-Based Testing | **Compliant** | §6 PBT-02-A~D 4속성 채택(Code Gen 구현). |
| Security Baseline | **N/A(미적용)** | opt-out. 단 §4 보안 NFR은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

## 9. 다음 단계 컨텍스트
- NFR Design(UOW-02): 위 NFR을 구현 패턴으로 전개(카탈로그 절단·캐시 직렬화·폴백 경로·PBT/통합테스트 마커 배치).
