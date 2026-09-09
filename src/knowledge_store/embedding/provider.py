"""EmbeddingProvider interface + local implementations (Application Design Q6).

Two implementations, both fully offline (NFR-3.1):

* ``LocalEmbeddingProvider`` — wraps a small offline model via ``fastembed`` when
  installed. No network access at inference time.
* ``HashingEmbeddingProvider`` — a deterministic, dependency-free feature-hashing
  embedding used as the default fallback so the system runs with zero model
  downloads. It is a real vector-space embedding (hashed bag-of-tokens with
  sublinear term weighting), suitable for similarity linking and search when a
  learned model is not available.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, runtime_checkable

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Abstraction over a local embedding model."""

    @property
    def dimension(self) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class HashingEmbeddingProvider:
    """Deterministic offline feature-hashing embedding (default fallback).

    Same text always maps to the same vector, so downstream relationship and
    versioning behaviour is reproducible (supports NFR-8 determinism).
    """

    def __init__(self, dimension: int = 256) -> None:
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        tokens = _tokenize(text)
        if not tokens:
            return vec
        counts: dict[str, int] = {}
        for tok in tokens:
            counts[tok] = counts.get(tok, 0) + 1
        for tok, count in counts.items():
            h = hashlib.md5(tok.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "little") % self._dim
            sign = 1.0 if h[4] & 1 else -1.0
            vec[idx] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]


class LocalEmbeddingProvider:
    """Wraps a small offline model via ``fastembed`` when available.

    Falls back to :class:`HashingEmbeddingProvider` if ``fastembed`` is not
    installed, keeping the server LLM-free and dependency-light either way.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        self._fallback = HashingEmbeddingProvider()
        self._model = None
        self._dim = self._fallback.dimension
        try:
            from fastembed import TextEmbedding  # type: ignore

            self._model = TextEmbedding(model_name=model_name)
            # Probe dimension once.
            probe = list(self._model.embed(["dimension probe"]))
            self._dim = len(probe[0])
        except Exception:
            self._model = None

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def is_learned(self) -> bool:
        return self._model is not None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._model is not None:
            return [list(map(float, v)) for v in self._model.embed(texts)]
        return self._fallback.embed(texts)


_DEFAULT: EmbeddingProvider | None = None


def get_default_provider() -> EmbeddingProvider:
    """Return a process-wide default provider (learned if available, else hashing)."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = LocalEmbeddingProvider()
    return _DEFAULT
