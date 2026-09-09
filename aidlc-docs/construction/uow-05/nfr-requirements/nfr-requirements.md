# UOW-05 (MCP 서버 인터페이스) — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements (UOW-05)
**작성일**: 2026-09-09
**결정 반영**: Q1=A(MCPServer 데코레이터·stdio·mcp>=2.0), Q2=A(cwd+TRACE_PROJECT_ROOT), Q3=A(오류→구조화 Result), Q4=A(P1 프롬프트 포함)
**Functional Design**: SKIP(얇은 어댑터). **활성 확장**: Resiliency Baseline(Blocking), PBT(해당 시).

---

## 1. 인터페이스 (FR-MCP-001, US-05.1)
| ID | 요구 |
|---|---|
| NFR-05-IF-1 | 5 MCP 도구 노출: `analyze_project`, `list_features`, `get_feature_knowledge`, `get_conflicts`, `analyze_task_impact` — 코어함수 1:1. |
| NFR-05-IF-2 | 입력 스키마는 타입힌트로 선언(MCPServer가 스키마 생성). 필수/선택 인자 명확. |
| NFR-05-IF-3 | 결과는 구조화(JSON)로 반환 — Result 직렬화(§4). |

## 2. 전송/기동 (FR-MCP-004, US-05.3)
| ID | 요구 |
|---|---|
| NFR-05-RUN-1 | stdio 전송(`run("stdio")`). 기준 클라이언트 Claude Code. |
| NFR-05-RUN-2 | 엔트리포인트 `trace-mcp = trace.mcp_server.__main__:main`(pyproject 기정의). |
| NFR-05-RUN-3 | 프로젝트 루트=서버 cwd 기본, `TRACE_PROJECT_ROOT` 환경변수로 오버라이드(Q2). |

## 3. 신뢰성 (Resiliency 전면, Q3)
| ID | 요구 |
|---|---|
| NFR-05-REL-1 | 각 도구 핸들러는 코어 호출을 try/except로 감싸 예외를 `error_to_result`(구조화 오류 Result)로 변환 — **서버 크래시 없음**. |
| NFR-05-REL-2 | 코어는 이미 부분 실패를 warnings로 강등(UOW-01~04) — 어댑터는 그 Result를 그대로 직렬화. |
| NFR-05-REL-3 | 리소스 조회 실패(손상/부재)는 오류 메시지 반환(전파 금지). |

## 4. 사용성/직렬화 (NFR-MCP-UX-002, US-05.1-AC3)
| ID | 요구 |
|---|---|
| NFR-05-UX-1 | Result 직렬화 순서 = summary → data → conflicts → impact → evidence → warnings → meta (핵심 우선). |
| NFR-05-UX-2 | 도구 응답은 사람이 읽는 summary + 구조화 필드 동시 제공(점진적 노출). |
| NFR-05-UX-3 | 지식 본문은 리소스(`trace://feature/<id>`)로, 구조화 필드는 도구 결과로 분리(US-05.2). |

## 5. 보안
| ID | 요구 |
|---|---|
| NFR-05-SEC-1 | 로컬 stdio 단일 프로세스 — 원격 노출 없음. API 키는 late lookup(UOW-0F). |
| NFR-05-SEC-2 | 리소스 URI는 `trace://feature/<id>`만 허용(경로 이탈 차단, KnowledgeStore 방어 재사용). |
| NFR-05-SEC-3 | 오류 메시지에 절대경로·시크릿 비노출(sanitize_error 재사용). |

## 6. 재현성 & 테스트
| ID | 요구 |
|---|---|
| NFR-05-TST-1 | 도구 등록 목록·직렬화·오류 매핑은 오프라인 단위 테스트(실 LLM·네트워크 없음). |
| NFR-05-TST-2 | 서버 객체 생성·도구/리소스/프롬프트 등록 스모크(구성 검증). LLM 호출 도구는 FakeLLM 주입 경로 유지. |
| NFR-05-TST-3 | mcp 미설치 환경 대비: 서버 모듈 임포트는 지연(엔트리포인트 실행 시에만) — 코어·테스트는 mcp 불필요. |

## 7. 유지보수성
| ID | 요구 |
|---|---|
| NFR-05-MAINT-1 | 도구 핸들러는 얇게(입력→코어→직렬화). 비즈니스 로직 금지(코어에 위임). |
| NFR-05-MAINT-2 | Result→dict 직렬화는 단일 헬퍼(serialize_result)로 국소화. |

## 8. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | §3 도구 오류 격리·무크래시·리소스 실패 강등. |
| Property-Based Testing | **N/A** | 어댑터 계층은 순수 불변식 로직 부재(직렬화 예제 기반 단위로 충분). |
| Security Baseline | **N/A(미적용)** | opt-out. §5 보안 NFR은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

## 9. 기술 결정 요약(→ tech-stack-decisions)
- `mcp>=2.0` 상향(설치 2.x, `MCPServer`), 신규 코어 래퍼 2개(list_features/get_feature_knowledge), serialize_result 헬퍼.

## 10. 다음 단계 컨텍스트
- NFR Design(UOW-05): 서버 구성·도구 배선 패턴·직렬화 헬퍼·오류 매핑·리소스/프롬프트 등록·테스트 배치.
