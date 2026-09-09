# UOW-01 (스캐너 & 파서) — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-01)
**작성일**: 2026-09-09
**결정 반영**: Q1=A(순차), Q2=B(파일당 5MB/총량 200MB), Q3=A,B,C,D(PBT 4속성 전부), Q4=A(config 분리)
**활성 확장**: Resiliency Baseline(Blocking, 전면), Property-Based Testing(Blocking, 전면). Security Baseline=미적용.

---

## 1. 성능 / 규모 (Q1=A, Q2=B)
| ID | 요구 | 값/정책 |
|---|---|---|
| NFR-01-PERF-1 | 스캔 처리 모델 | **단일 스레드 순차** 순회·파싱. 병렬화 미도입(결정성·단순성 우선). |
| NFR-01-PERF-2 | 규모 가정 | 로컬 소·중 프로젝트(수천 파일). 명시적 시간 SLA 없음(합리적 시간 내 완료). |
| NFR-01-PERF-3 | 파일당 크기 상한 | **5MB**. 초과 시 상한까지만 읽고 truncated=True, parse_status=partial, warning. |
| NFR-01-PERF-4 | 총량 상한 | **200MB**(누적 읽은 바이트). 초과 시 이후 파일은 skipped + warning(code=`total_size_cap`), 스캔은 정상 종료. |
| NFR-01-PERF-5 | 메모리 | content eager 적재(Q4=A)이나 위 상한으로 메모리 상한 예측 가능. |

## 2. 신뢰성 (Resiliency 확장 — 전면)
| ID | 요구 |
|---|---|
| NFR-01-REL-1 | 파일 단위 실패 격리: 임의 파일 파싱 예외가 전체 스캔을 중단시키지 않음(FR-ANALYSIS-003, BR-FAIL-001). |
| NFR-01-REL-2 | 모든 부분 실패·트렁케이션·스킵 사유는 구조화 `Warning`으로 수집되어 Result에 합류(관측 가능성). |
| NFR-01-REL-3 | 무효 경로는 빠른 실패(오류 Result)로 처리하되, 존재하는 경로 내 개별 문제는 graceful degradation. |
| NFR-01-REL-4 | 빈 프로젝트(자산 0)도 오류 아님 — 정상 완료(BR-FAIL-003). |

## 3. 보안 (NFR-SEC-004 + 위생)
| ID | 요구 |
|---|---|
| NFR-01-SEC-1 | 경로 존재·디렉터리 검증 후에만 스캔(NFR-SEC-004, BR-PATH-001). |
| NFR-01-SEC-2 | realpath 정규화 + 루트 하위 강제. 루트 밖 심볼릭/트래버설 대상은 결과에 포함 금지(BR-PATH-002/003). |
| NFR-01-SEC-3 | 읽기 전용 — 대상 프로젝트 파일 수정/생성 없음(BR-SEC-002). |
| NFR-01-SEC-4 | 오류/경고 메시지에 파일 내용·시크릿·전체 절대경로 비노출(rel_path·코드만, BR-SEC-001). |

## 4. 유지보수성 (Q4=A)
| ID | 요구 |
|---|---|
| NFR-01-MAINT-1 | 스캔 설정(파일/총량 상한, 추가 제외)은 **config(C7)**에 배치(`get_scan_settings()` 또는 상수 모듈). 하드코딩 금지. |
| NFR-01-MAINT-2 | 파서 확장 지점 명확화: 유형→파서 매핑 테이블로 새 AssetType/파서 추가가 국소 변경이 되도록. |
| NFR-01-MAINT-3 | classify/parse/scanner 책임 분리(모듈 경계 = business-logic-model §1). |

## 5. PBT 속성 (Property-Based Testing — 전면, Q3=A,B,C,D)
hypothesis로 다음 4개 불변식을 검증한다(Code Generation에서 구현):
| ID | 속성 | 생성 전략(개략) |
|---|---|---|
| PBT-01-A | **분류 전결정성**: 임의 파일명/확장자에 classify가 항상 유효한 AssetType 하나 반환(예외/None 없음) | 무작위 파일명·확장자·경로 세그먼트 |
| PBT-01-B | **경로 안전성**: 트래버설(`../`)·루트 밖 심볼릭 대상이 결과 assets에 절대 미포함 | 임시 디렉터리 트리 + 탈출 링크/경로 |
| PBT-01-C | **부분 실패 격리**: 임의 부분 파일 손상 시 scan은 예외 없이 완료, 손상 파일만 failed | 무작위 바이트/권한/디코드 실패 주입 |
| PBT-01-D | **결정성/멱등**: 동일 트리 2회 스캔 → assets(순서 포함) 동일 | 무작위 파일 집합 생성 후 2회 실행 비교 |

## 6. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | NFR-01-REL-1~4가 부분실패 격리·graceful degradation·관측 가능성을 요구·구현 예정. |
| Property-Based Testing | **Compliant** | §5 PBT-01-A~D 4속성 채택(전면 정책 이행). Code Generation에서 hypothesis 테스트로 구현. |
| Security Baseline | **N/A(미적용)** | opt-out(Q8=B). 단 NFR-SEC-004 등 요구사항 자체는 §3으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

## 7. 다음 단계 컨텍스트
- NFR Design(UOW-01): 위 NFR을 구현 패턴으로 전개(설정 배치·파서 매핑·warning 코드 체계·PBT 배치).
