# Performance Test Instructions — TRACE

**단계**: CONSTRUCTION / Build and Test
**작성일**: 2026-09-09

> TRACE는 로컬 stdio 단일 프로세스 도구로, 별도 부하 테스트 스위트는 범위 밖(P2). 대신 아래
> 성능 특성이 설계·코드로 보장되며 기존 테스트가 그 불변식을 검증한다.

---

## 성능 관련 NFR과 검증 지점
| 특성 | 보장 방식 | 검증 |
|---|---|---|
| LLM 호출 최소화 | Feature 식별 1회 + Feature당 지식 1회 + 추출 1회 + 작업 영향 1회 | 테스트가 FakeLLM 호출 카운트 단언 |
| 재분석 생략(캐시) | 콘텐츠 해시 캐시 + 완본 스테이지(`meta.stage=="complete"`) | test_analysis_cache, test_analyze_project, test_hero_e2e(2회차 무LLM) |
| 순수 함수 무비용 | 충돌검출·Confidence·영향매핑·랭킹은 네트워크 없음 | PBT(test_conflict/impact_properties) |
| 입력 상한 | 자산 발췌 4,000자·총량 상한·focus top-N=3 | test_features_properties(발췌 상한), 스캐너 총량 상한 |

## 측정(선택, 수동)
고정 데모 데이터셋 기준 벽시계 측정:
```bash
python -c "import time; t=time.perf_counter(); \
import subprocess,sys; subprocess.run([sys.executable,'demo/run_demo.py'],stdout=subprocess.DEVNULL); \
print('demo wall time: %.2fs' % (time.perf_counter()-t))"
```
- FakeLLM(무네트워크)이라 스캔·파싱·검출의 순수 처리 시간만 반영 → 소규모 프로젝트에서 1초 내외.
- 실 LLM 사용 시 지연은 대부분 모델 응답 시간(캐시 히트 시 0콜).

## 회귀 방지
- 캐시 히트 시 LLM 미호출을 테스트가 호출 카운트로 강제 → 성능 회귀(불필요한 재호출) 조기 검출.
