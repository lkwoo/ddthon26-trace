"""demo/ 데이터셋에서 실제 Claude로 Feature를 추출해 파일로 저장하는 러너 (--live).

run_demo.py 의 FakeLLM 과 달리 **진짜 Anthropic 클라이언트**로 전체 파이프라인을 구동한다:
  scan → identify_features → extract_claims → 지식 저장 → 결정적 충돌 검출

- API 키: 프로세스 환경변수 ANTHROPIC_API_KEY 에서 읽는다(late lookup). 이 스크립트는
  편의를 위해 리포 루트의 .env 파일이 있으면 거기서 KEY=VALUE 를 읽어 os.environ 에 주입한다
  (.env 는 gitignore 대상 — 키가 코드/로그/터미널에 노출되지 않는다).
- 분석 대상: demo/ 데이터셋(run_demo 와 동일하게 run_demo.py·scenario·tools·__pycache__·.trace 제외)을
  임시 디렉터리에 복사해 분석한 뒤, 생성된 .trace/ 를 demo/.trace/ 로 복사한다.
  → 결과 산출물 경로:  demo/.trace/knowledge/features/<id>.md

실행:  python demo/tools/extract_features_live.py
결과는 실제 LLM 출력이라 **비결정적**이다(Feature 수·claim 문구가 실행마다 다를 수 있음).
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
except Exception:  # pragma: no cover
    pass

_DEMO_DIR = _REPO_ROOT / "demo"
_ENV_FILE = _REPO_ROOT / ".env"


def _load_dotenv(path: Path) -> None:
    """.env 의 KEY=VALUE 를 os.environ 에 주입(이미 설정된 값은 유지). 값은 출력하지 않는다."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    _load_dotenv(_ENV_FILE)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("✗ ANTHROPIC_API_KEY 가 환경/`.env` 에 없습니다. "
              ".env 에 ANTHROPIC_API_KEY=sk-ant-... 를 넣고 다시 실행하세요.")
        return 2

    from trace.engine.analyze import analyze_project, list_features
    from trace.knowledge.store import KnowledgeStore

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "demo"
        shutil.copytree(_DEMO_DIR, work, ignore=shutil.ignore_patterns(
            "run_demo.py", "scenario", "tools", "__pycache__", ".trace"))
        work_str = str(work)

        print("실제 Claude 로 demo/ 분석 중… (비결정적, 네트워크 호출)")
        res = analyze_project(work_str)  # llm 미지정 → 실제 AnthropicClient
        print(res.summary)
        print(f"자산 {res.data['assets_count']}개 / "
              f"Feature {len(res.data['features'])}개 / "
              f"충돌 {res.data['conflicts_count']}건\n")

        for f in list_features(path=work_str).data["features"]:
            print(f"  - {f['id']}: {f['title']} (충돌 {f['conflicts_count']}건)")

        if res.warnings:
            print("\n경고:")
            for w in res.warnings:
                print(f"  - [{w.code}] {w.message} (source={w.source})")

        # 생성된 .trace/ 를 demo/ 로 복사해 산출물을 남긴다
        src_trace = work / ".trace"
        dst_trace = _DEMO_DIR / ".trace"
        if src_trace.exists():
            if dst_trace.exists():
                shutil.rmtree(dst_trace)
            shutil.copytree(src_trace, dst_trace)
            fdir = KnowledgeStore(str(_DEMO_DIR)).features_dir()
            print(f"\n✓ Feature 지식 저장 위치: {fdir}")
            for p in sorted(fdir.glob("*.md")):
                print(f"  - {p.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
