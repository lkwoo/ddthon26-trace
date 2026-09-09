"""디렉터리 순회·경로검증·제외·바이너리 판별 (UOW-01, NFR Design P1/P2, BR-PATH/EXCLUDE).

- 경로 검증 게이트(P1): resolve → exists/is_dir, 실패 시 PathValidationError.
- 트래버설 차단: 후보 경로를 resolve 후 루트 하위 여부 확인.
- 순회(P2): os.walk(followlinks=False) + 제외 디렉터리 prune.
- 제외 규칙은 config.get_exclusions()의 git-style glob(**/name/**)을 정규식으로 컴파일해 적용.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator

from trace.common.errors import PathValidationError


def validate_root(path: str) -> Path:
    """스캔 루트를 검증·정규화한다 (NFR-SEC-004, BR-PATH-001/002).

    존재하지 않거나 디렉터리가 아니면 PathValidationError.
    """
    if not path or not str(path).strip():
        raise PathValidationError("스캔 경로가 비어 있습니다.")
    root = Path(path).resolve()
    if not root.exists():
        raise PathValidationError("경로가 존재하지 않습니다.")
    if not root.is_dir():
        raise PathValidationError("경로가 디렉터리가 아닙니다.")
    return root


def is_within_root(candidate: Path, root: Path) -> bool:
    """candidate(심볼릭 포함)가 resolve 후 root 하위인지 (트래버설/탈출 차단, BR-PATH-002/003)."""
    try:
        resolved = candidate.resolve()
    except OSError:
        return False
    try:
        resolved.relative_to(root)
        return True
    except ValueError:
        return False


def _glob_to_regex(pattern: str) -> str:
    """git-style glob(**, *, ?)를 POSIX 상대경로용 정규식 조각으로 변환."""
    out: list[str] = []
    i, n = 0, len(pattern)
    while i < n:
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return "".join(out)


def _dir_form(pattern: str) -> str:
    """디렉터리 prune 용: 후행 /** 또는 /* 를 제거한 패턴."""
    for suf in ("/**", "/*"):
        if pattern.endswith(suf):
            return pattern[: -len(suf)]
    return pattern


class ExclusionMatcher:
    """제외 glob 패턴을 컴파일해 디렉터리/파일 매칭 (BR-EXCLUDE-001)."""

    def __init__(self, patterns: list[str]) -> None:
        self._file_res = [re.compile("^" + _glob_to_regex(p) + "$") for p in patterns]
        self._dir_res = [re.compile("^" + _glob_to_regex(_dir_form(p)) + "$") for p in patterns]

    def is_excluded_dir(self, rel_posix: str) -> bool:
        return any(r.match(rel_posix) for r in self._dir_res)

    def is_excluded_file(self, rel_posix: str) -> bool:
        return any(r.match(rel_posix) for r in self._file_res)


def is_binary(path: Path, sniff_bytes: int = 4096) -> bool:
    """앞부분에 널바이트가 있으면 바이너리로 판정 (BR-EXCLUDE-002). 읽기 실패 시 True(안전측)."""
    try:
        with path.open("rb") as f:
            chunk = f.read(sniff_bytes)
    except OSError:
        return True
    return b"\x00" in chunk


def walk_files(root: Path, matcher: ExclusionMatcher) -> Iterator[Path]:
    """루트 하위 파일을 결정적 순서로 순회한다 (제외 디렉터리 prune, 심볼릭 미추적)."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        # 제외 디렉터리 prune (하위 순회 생략) — 결정적 순서 유지
        kept: list[str] = []
        for d in sorted(dirnames):
            child = current / d
            rel = child.resolve().relative_to(root).as_posix() if is_within_root(child, root) else None
            if rel is None:
                continue  # 루트 밖 심볼릭 디렉터리 — 따라가지 않음
            if matcher.is_excluded_dir(rel):
                continue
            kept.append(d)
        dirnames[:] = kept

        for fname in sorted(filenames):
            child = current / fname
            if child.is_symlink() and not is_within_root(child, root):
                continue  # 루트 밖 심볼릭 파일
            try:
                rel = child.relative_to(root).as_posix()
            except ValueError:
                continue
            if matcher.is_excluded_file(rel):
                continue
            yield child


__all__ = [
    "validate_root",
    "is_within_root",
    "is_binary",
    "walk_files",
    "ExclusionMatcher",
]
