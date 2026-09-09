# Performance Test Instructions — TRACE

> 로컬 단일 프로세스·stdio MCP 서버로, 프로덕션 부하 테스트 대상이 아니다(infrastructure-design SKIP).
> 성능 관심사는 "개발자가 착수 직전 기다림 없이 답을 받는가"에 한정한다.

## 성능 관심 지표

| 지표 | 기대(데모 규모, 자산 ~12개) | 측정 |
|---|---|---|
| replay `analyze-project` 지연 | < 1초 (LLM 호출 없이 픽스처 재생) | 아래 스크립트 |
| replay `analyze-task` 지연 | < 1초 | 아래 스크립트 |
| 캐시 재사용(2회차 analyze-project, refresh 없음) | 파싱·LLM 생략, 즉시 반환(`cached: true`) | test_analyze_project_uses_cache_on_second_run |
| replay `generate_onboarding_map` 지연 (UOW-07) | < 1초 (정적 추출 + 픽스처 재생) | `trace map ./demo --refresh` |
| overview.md 캐시 재사용 (refresh 없음) | 정적 추출·LLM 생략, overview.md 로드만 | `trace map ./demo` 2회차 |
| live 모드 지연 | Claude 호출 수에 비례(Feature 수 × 스텝). 결정성은 구조화 출력+캐시로 확보 | 참고용, 부하 테스트 아님 |

## 측정 방법

```bash
export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR=$PWD/demo/replay TRACE_HOME=/tmp/trace-perf
python3 - <<'PY'
import time, os
from traceki.config import Config, LLMSettings
from traceki.engine.pipeline import analyze_project
from traceki.knowledge import KnowledgeStore
cfg = Config(llm=LLMSettings(backend="replay", replay_dir=os.environ["TRACE_REPLAY_DIR"]))
store = KnowledgeStore("/tmp/trace-perf")
t=time.perf_counter(); analyze_project("./demo", config=cfg, store=store, refresh=True)
print(f"analyze-project(cold): {time.perf_counter()-t:.3f}s")
t=time.perf_counter(); analyze_project("./demo", config=cfg, store=store)  # cache
print(f"analyze-project(cached): {time.perf_counter()-t:.3f}s")
PY
```

## 참고

- replay 픽스처 재생은 LLM 왕복이 없어 지연의 대부분이 파일 파싱(PDF/YAML/소스)이다.
- live 모드에서 지연이 문제면 Feature별 지식 생성을 병렬화할 수 있으나, 결정성·비용 관점에서
  데모 기본은 순차 실행이다. 대규모 저장소 확장은 Operations 단계 과제로 남긴다.
