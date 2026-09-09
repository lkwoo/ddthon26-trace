# UOW-04 (Task Impact Analysis) — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-04)
**작성일**: 2026-09-09
**결정 반영**: Q1=A,B,C,D(PBT 4속성), Q2=A(FakeLLM+llm_integration 옵트인), Q3=A(발췌 4000 상속·focus top-N=3)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면).

---

## 1. LLM 비용/토큰
| ID | 요구 |
|---|---|
| NFR-04-COST-1 | 영향 분석은 작업당 **1회** 구조화 호출(analyze_task). |
| NFR-04-COST-2 | 컨텍스트 발췌 상한 **4,000자** 상속(UOW-02/03). focus 상세는 관련도 상위 **N=3**, 그 외는 요약만. |
| NFR-04-COST-3 | 결정성 파라미터(temp=0)·max_tokens는 LLMSettings(UOW-0F). |

## 2. 성능
| ID | 요구 |
|---|---|
| NFR-04-PERF-1 | build_context/rank_by_relevance/to_impact_out는 **순수/준순수** — 무네트워크. |
| NFR-04-PERF-2 | 저장 지식(analyze_project 산출)을 재사용 — UOW-04 자체 재스캔·재추출 없음. |
| NFR-04-PERF-3 | related_conflicts는 저장된 conflicts 로드만(LLM 미호출). |

## 3. 신뢰성 (Resiliency 전면)
| ID | 요구 |
|---|---|
| NFR-04-REL-1 | analyze_task LLM 실패는 warning 강등 + 빈 ImpactOut(예외 전파 금지, BR-PIPE-002). |
| NFR-04-REL-2 | LLM 실패 시에도 related_conflicts는 저장 지식에서 채워 노출(경고 유지). |
| NFR-04-REL-3 | 저장 지식 부재 시 안내 warning("먼저 analyze_project 실행")·빈 impact(BR-PIPE-003). |
| NFR-04-REL-4 | focus 로드 중 손상 파일은 skip+warning(컨텍스트 계속). |

## 4. 보안
| ID | 요구 |
|---|---|
| NFR-04-SEC-1 | 프롬프트는 known_sources 화이트리스트 안에서만 path 지목 유도(허구 path 억제). |
| NFR-04-SEC-2 | reason/warning에 원문·시크릿·절대경로 비노출 — path는 rel_path만. |
| NFR-04-SEC-3 | 발췌 상한 준수(원문 대량 유출 방지). |

## 5. 재현성 & 테스트 (Q2=A)
| ID | 요구 |
|---|---|
| NFR-04-TST-1 | to_impact_out/rank_by_relevance는 **순수 함수** → FakeLLM 없이 결정적 단위·PBT. |
| NFR-04-TST-2 | analyze_task_impact는 FakeLLM 주입(오프라인). Hero Task는 저장 지식 픽스처+Fake 응답으로 검증. |
| NFR-04-TST-3 | 옵트인 `llm_integration`(마커 재사용): analyze_task_impact 실 API 통합 1건(env+키 시). |

## 6. PBT 속성 (Q1=A,B,C,D — 전면)
| ID | 속성 |
|---|---|
| PBT-04-A | 매핑 건전성: `path ∉ known_sources` 후보는 must/likely에 없음(항상 review) |
| PBT-04-B | 근거 부족 강등: evidence 빈 후보는 항상 review + Insufficient evidence |
| PBT-04-C | 정렬 결정성/멱등: 후보 입력 순서 셔플에도 동일 ImpactOut(카테고리별 path 정렬) |
| PBT-04-D | related_conflicts 정합: focus conflicts 수 == related_conflicts 수(누락·중복 없음) |

## 7. 유지보수성
| ID | 요구 |
|---|---|
| NFR-04-MAINT-1 | analyze_task 프롬프트는 파일 템플릿(C8) 분리. |
| NFR-04-MAINT-2 | 관련도 랭킹·매핑 규칙은 전용 함수로 국소화(확장 용이). |

## 8. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | §3 LLM/지식부재/손상 강등, 충돌은 독립 노출. |
| Property-Based Testing | **Compliant** | §6 PBT-04-A~D 4속성(순수함수 매핑 건전성 포함). |
| Security Baseline | **N/A(미적용)** | opt-out. §4 보안 NFR은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

## 9. 다음 단계 컨텍스트
- NFR Design(UOW-04): 컨텍스트 조립 패턴·매핑/강등 순수함수 배치·랭킹 규칙·PBT/통합 테스트 배치·analyze_task_impact 조립 패턴.
