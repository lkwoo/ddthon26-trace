# UOW-06 (통합·신뢰성·시연) — Code Summary

**단계**: CONSTRUCTION / Code Generation (UOW-06, 수렴)
**작성일**: 2026-09-09
**결과**: `pytest` **145 passed, 3 skipped**(옵트인 `llm_integration`). Hero E2E·데모 하니스·폴백 CLI·README·페르소나 여정 완비.

---

## 생성/수정 파일

### 코드
| 파일 | 내용 |
|---|---|
| `trace/cli/__init__.py`·`__main__.py` **신설** | C9 폴백 CLI(`trace`): `analyze`/`features`/`knowledge`/`conflicts`/`impact` 서브커맨드 → 코어 함수 재사용, `--json`·`--path`, 오류→error_to_result 강등. |
| `demo/run_demo.py` **신설** | Hero 하니스: demo/ 스캔 → 실제 rel_path 기반 스크립트 FakeLLM(3충돌 재현) → 전 흐름 출력. **API 키 불필요·결정적**. |
| `.env.example` **갱신** | `TRACE_PROJECT_ROOT` 힌트 추가. |

### 테스트
| 파일 | 내용 |
|---|---|
| `tests/test_hero_e2e.py` **신설** | demo/ E2E(스크립트 FakeLLM): 3충돌 유형 정확·충돌 경고·Must/Likely/Review·Change Plan·2회 반복 동일(캐시 히트 무LLM). |

### 문서·시연 산출물
| 파일 | 내용 |
|---|---|
| `README.md` **갱신** | 30초 시연·`.mcp.json` 스니펫·5도구·CLI·Hero 예제 프롬프트·아키텍처·보안·페르소나 링크. |
| `result/usage-walkthrough.md` **신설** | P1/P2/P3 페르소나 여정(언제·요청·도구·증거·이점). |
| `result/hero-demo-output.txt` **신설** | `run_demo.py` 실제 콘솔 출력(결정적 실행 증거). |
| `result/README.md` **신설** | 증거 인덱스 + GUI 스크린샷 캡처 절차. |

---

## 앞 단계 결정의 반영 (전 유닛 수렴)

- **Hero E2E(DoD 앵커, US-06.1)**: demo/(Petclinic + 의도적 충돌)에서 analyze_project→list_features→
  get_feature_knowledge→get_conflicts→analyze_task_impact 전 구간 통과. **3충돌**(value_mismatch·policy_conflict·
  stale_knowledge)을 결정적으로 재현.
- **실패/폴백(US-06.2)**: 코어의 per-unit warning 강등 + 캐시 재사용(2회차 무LLM) + 폴백 CLI(C9) — 시연 견고성.
- **턴키 시연(US-06.3)**: README `.mcp.json` 복붙 스니펫·Hero 예제 프롬프트, `result/`에 실행 증거·페르소나 여정.
- **보안 위생(US-06.4)**: 소스 하드코딩 시크릿 없음(grep 확인), `.env`/`.trace` gitignore, 키 late-lookup.
- **코어/인터페이스 분리(NFR-CORE-001)**: 동일 코어 5함수를 MCP(C1)·CLI(C9)가 공유 — CLI가 이를 실증.

## 스크린샷 한계 (정직 고지)
- GUI(Claude Code) 스크린샷은 **실 API 키 + Claude Code 실행 환경**이 필요해 이 자동화 환경에서 직접 캡처 불가.
- 대체: (1) `run_demo.py`의 **결정적 CLI 실행 출력**을 `result/hero-demo-output.txt`로 실증 저장(무키),
  (2) `result/README.md`에 GUI 캡처 절차 제공 → 키 주입 후 사용자가 `result/screenshots/`에 PNG 추가.
- 평가 정합: `hero-demo-output.txt`의 3충돌·영향·Change Plan은 README 기능 서술과 일치(실행 증거↔기능 정합).

## 구현 중 결정
- **Windows 콘솔 UTF-8**: `run_demo.py`가 stdout을 UTF-8로 reconfigure(cp949 환경 한글·기호 깨짐 방지).
- **데모 격리**: 하니스는 demo/를 임시 디렉터리에 복사해 실행 — 리포에 `.trace` 생성물 오염 없음.
- **단일 진실원**: Hero E2E 테스트가 `run_demo.py`의 스크립트 빌더를 재사용(중복 제거).

## DoD
- [x] Hero E2E 수동 편집 없이 통과·반복 가능(NFR-REL-001/AI-004).
- [x] 실패 강등·캐시·폴백 CLI(FR-DEMO-002).
- [x] README `.mcp.json`·예제 프롬프트, `result/` 실행 증거·페르소나 여정(FR-DEMO-001).
- [x] 보안 위생(시크릿 비하드코딩·gitignore·late-lookup).
- [x] pytest 145 pass·3 skip.

## 다음
- Build and Test 단계(빌드·테스트 지침 문서화)로 Construction 마무리.
