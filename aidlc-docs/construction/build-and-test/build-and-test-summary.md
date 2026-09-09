# Build and Test Summary — TRACE

**단계**: CONSTRUCTION / Build and Test
**작성일**: 2026-09-09
**범위**: 전체 유닛(UOW-0F ~ UOW-06) 통합.

---

## 한눈에
```bash
pip install -e ".[dev]"     # 설치
pytest                      # 145 passed, 3 skipped
mypy                        # 신규 유닛 clean (잔여 1건: llm/client.py, UOW-0F)
python demo/run_demo.py     # 무키 결정적 Hero 데모
trace --help                # 폴백 CLI
```

## 지침 문서
| 문서 | 내용 |
|---|---|
| [build-instructions.md](build-instructions.md) | 환경·의존성·엔트리포인트·스모크 |
| [unit-test-instructions.md](unit-test-instructions.md) | 단위·PBT·mypy, 유닛↔테스트 맵 |
| [integration-test-instructions.md](integration-test-instructions.md) | Hero E2E·데모 하니스·MCP·CLI·옵트인 실 API |
| [performance-test-instructions.md](performance-test-instructions.md) | LLM 호출 최소화·캐시·순수함수 특성 |

## 검증 상태
| 항목 | 결과 |
|---|---|
| 전체 테스트 | ✅ 145 passed, 3 skipped(옵트인 llm_integration) |
| 정적 타입(mypy) | ✅ 신규 유닛 clean / ⚠ 잔여 1건(llm/client.py, 기능 무영향) |
| Hero E2E(오프라인) | ✅ 3충돌·영향·Change Plan 재현·반복 가능 |
| 데모 하니스 | ✅ `result/hero-demo-output.txt` 실행 증거 |
| 보안 위생 | ✅ 하드코딩 시크릿 없음·`.env`/`.trace` gitignore·late lookup |
| PBT | ✅ 16속성(스캐너·지식·충돌·영향 각 4) |

## 알려진 한계
- **GUI 스크린샷**: 자동화 환경에서 Claude Code GUI 캡처 불가 → 결정적 CLI 실행 증거(`result/hero-demo-output.txt`) + 캡처 절차(`result/README.md`)로 대체.
- **mypy 잔여 1건**: `trace/llm/client.py`(UOW-0F) `_sdk_client` 타입 — 기능 영향 없음, 후속 정리 대상.
- **P1/P2 범위**: DOCX/PPTX 파서·웹 UI·벡터DB·자동 소스 수정은 범위 밖(요구사항 §19).

## 다음
- Build and Test 승인 → CONSTRUCTION 완료. OPERATIONS는 현재 placeholder.
