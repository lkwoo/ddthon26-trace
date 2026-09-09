# UOW-03 (Claims/Evidence/Conflict) — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-03)
**작성일**: 2026-09-09
**결정 반영**: Q1=A,B,C,D(PBT 4속성), Q2=A(FakeLLM+llm_integration 옵트인), Q3=A(발췌 4000 상속)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 1. LLM 비용/토큰
| ID | 요구 |
|---|---|
| NFR-03-COST-1 | 추출은 Feature당 **1회** 구조화 호출(ExtractedClaim+Evidence 동시). |
| NFR-03-COST-2 | 입력은 관련 자산 카탈로그(발췌 **4,000자** 상속, UOW-02와 동일). |
| NFR-03-COST-3 | 결정성 파라미터(temp=0)·max_tokens는 LLMSettings(UOW-0F). |

## 2. 성능/캐시
| ID | 요구 |
|---|---|
| NFR-03-PERF-1 | `meta.stage=="complete"` 인 완본 FeatureKnowledge는 재분석 생략(LLM 미호출). |
| NFR-03-PERF-2 | 자산 불변 재실행은 캐시 히트로 전체 LLM 미호출(UOW-02 캐시와 정합). |
| NFR-03-PERF-3 | detect_conflicts/assign_confidence/classify는 순수 함수 — 무런타임 비용(네트워크 없음). |

## 3. 신뢰성 (Resiliency 전면)
| ID | 요구 |
|---|---|
| NFR-03-REL-1 | Feature별 extract 실패는 warning 강등, 그 Feature는 셸 유지, 전체 계속(BR-PIPE-002). |
| NFR-03-REL-2 | 허구 소스 Evidence는 드롭+warning(BR-EVID-004) — 잘못된 근거 방지. |
| NFR-03-REL-3 | 충돌 유형 분류 모호 시 최소 value_mismatch로 노출(누락 금지, BR-CONFLICT-005). |
| NFR-03-REL-4 | get_conflicts 로드 중 손상 파일은 skip+warning(목록 계속). |

## 4. 보안
| ID | 요구 |
|---|---|
| NFR-03-SEC-1 | 프롬프트 발췌 상한 준수(원문 대량 유출 방지). |
| NFR-03-SEC-2 | Evidence.location은 위치 표기만(원문 스니펫 대량 복사 금지). |
| NFR-03-SEC-3 | 경고/로그에 시크릿·원문·절대경로 비노출(rel_path·claim_key·code만). |

## 5. 재현성 & 테스트 (Q2=A)
| ID | 요구 |
|---|---|
| NFR-03-TST-1 | detect_conflicts/classify/assign_confidence는 **순수 함수** → FakeLLM 없이 결정적 단위·PBT. |
| NFR-03-TST-2 | 추출/파이프라인은 FakeLLM 주입(오프라인). demo 3충돌은 손수 만든 ExtractedClaim 픽스처로도 검증. |
| NFR-03-TST-3 | 옵트인 `llm_integration`(UOW-02 마커 재사용): analyze_project 실 API 통합 1건(env+키 시). |

## 6. PBT 속성 (Q1=A,B,C,D — 전면)
| ID | 속성 |
|---|---|
| PBT-03-A | 충돌 검출 건전성: distinct 정규화 값 ≤1 → Conflict 0; ≥2 → Conflict 정확히 1(해당 claim) |
| PBT-03-B | 검출 결정성/멱등: 동일 입력(+evidence 순서 셔플) 2회 → 동일 conflicts |
| PBT-03-C | 유형 분류 전결정성: classify_conflict_type 임의 입력 → 유효 ConflictType 하나(예외 없음) |
| PBT-03-D | Confidence 규칙 정합: contradicts/≥2값→LOW, 다근거·일치→HIGH, 그 외→MEDIUM |

## 7. 유지보수성
| ID | 요구 |
|---|---|
| NFR-03-MAINT-1 | 추출 프롬프트는 파일 템플릿(C8) 분리. |
| NFR-03-MAINT-2 | 충돌 분류 규칙/부재 토큰은 상수·전용 함수로 국소화(확장 용이). |

## 8. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | §3 Feature별 격리·허구근거 드롭·모호시 폴백. |
| Property-Based Testing | **Compliant** | §6 PBT-03-A~D 4속성(순수함수 검출 건전성 포함). |
| Security Baseline | **N/A(미적용)** | opt-out. §4 보안 NFR은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

## 9. 다음 단계 컨텍스트
- NFR Design(UOW-03): 결정적 검출 패턴·분류 규칙 배치·PBT/통합 테스트 배치·analyze_project 조립 패턴.
