"""자산 유형 분류 (UOW-01, BR-CLASSIFY, NFR Design 없음—순수 함수).

분류 우선순위 (BR-CLASSIFY-001):
  (1) 테스트 판별(경로/파일명)  → TEST      (최우선, 원 언어 무관)
  (2) 확장자 매핑              → SOURCE/SQL/MARKDOWN/PDF/CONFIG
  (3) YAML/JSON 내용 판별       → OPENAPI vs CONFIG
  (4) 그 외 텍스트             → TEXT
"""

from __future__ import annotations

import json
import re

import yaml

from trace.models.asset import AssetType

# 확장자 → 유형 (테스트 판별 이후 적용)
_SOURCE_EXTS = {
    ".java", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".kt", ".kts",
    ".rb", ".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".rs", ".php", ".scala", ".swift",
}
_CONFIG_EXTS = {".properties", ".toml", ".ini", ".cfg", ".env", ".conf"}
_MARKDOWN_EXTS = {".md", ".markdown"}
_STRUCTURED_EXTS = {".yaml", ".yml", ".json"}

_TEST_FILENAME_RE = re.compile(
    r"(^test_)|(_test\.)|([Tt]est[s]?\.)|([Tt]ests?$)",
)


def _suffix(filename: str) -> str:
    idx = filename.rfind(".")
    return filename[idx:].lower() if idx >= 0 else ""


def is_test(rel_path: str, filename: str) -> bool:
    """경로 세그먼트(/test/·/tests/) 또는 파일명 패턴으로 테스트 판별 (BR-CLASSIFY-002)."""
    posix = rel_path.replace("\\", "/").lower()
    if "/test/" in f"/{posix}/" or "/tests/" in f"/{posix}/":
        return True
    stem = filename.rsplit(".", 1)[0]
    return bool(_TEST_FILENAME_RE.search(filename) or _TEST_FILENAME_RE.search(stem))


def looks_like_openapi(text: str) -> bool:
    """YAML/JSON 텍스트 최상위에 openapi/swagger 키가 있으면 True (BR-CLASSIFY-003).

    파싱 실패 시 False(호출측이 config 로 폴백).
    """
    doc: object = None
    stripped = text.lstrip()
    try:
        if stripped.startswith("{"):
            doc = json.loads(text)
        else:
            doc = yaml.safe_load(text)
    except (yaml.YAMLError, json.JSONDecodeError, ValueError):
        return False
    if isinstance(doc, dict):
        return "openapi" in doc or "swagger" in doc
    return False


def classify(rel_path: str, filename: str, *, text: str | None = None) -> AssetType:
    """자산 유형을 결정 (항상 유효한 AssetType 하나 반환, 예외 없음 — PBT-01-A).

    text 는 YAML/JSON 의 openapi 판별에만 사용(없으면 config 로 분류).
    """
    if is_test(rel_path, filename):
        return AssetType.TEST

    ext = _suffix(filename)
    if ext in _SOURCE_EXTS:
        return AssetType.SOURCE
    if ext == ".sql":
        return AssetType.SQL
    if ext in _MARKDOWN_EXTS:
        return AssetType.MARKDOWN
    if ext == ".pdf":
        return AssetType.PDF
    if ext in _STRUCTURED_EXTS:
        if text is not None and looks_like_openapi(text):
            return AssetType.OPENAPI
        return AssetType.CONFIG
    if ext in _CONFIG_EXTS:
        return AssetType.CONFIG
    return AssetType.TEXT


__all__ = ["classify", "is_test", "looks_like_openapi"]
