"""ChunkVersioner — chunk-level version management via similarity/hash matching.

Uses a deterministic MinHash signature over character shingles plus a Jaccard
similarity estimate to decide whether a new chunk corresponds to an existing
one (US-4.1). Matching is reproducible: the same content always yields the same
signature (PBT determinism target, PBT-03). Matched chunks are bumped to a new
version preserving history; unmatched chunks start at version 1 (US-4.2).
"""

from __future__ import annotations

import hashlib
import re

from knowledge_store.store.repositories import ChunkRepository
from knowledge_store.types import Chunk, MatchResult, Status, VersionResult

_WS_RE = re.compile(r"\s+")
_NUM_PERM = 64
_MERSENNE = (1 << 61) - 1


def _normalize(text: str) -> str:
    return _WS_RE.sub(" ", text.strip().lower())


def _shingles(text: str, k: int = 5) -> set[str]:
    norm = _normalize(text)
    if len(norm) <= k:
        return {norm} if norm else set()
    return {norm[i:i + k] for i in range(len(norm) - k + 1)}


def _hash_shingle(shingle: str, seed: int) -> int:
    h = hashlib.blake2b(shingle.encode("utf-8"), digest_size=8,
                        salt=seed.to_bytes(8, "little")).digest()
    return int.from_bytes(h, "little") % _MERSENNE


def minhash_signature(text: str, num_perm: int = _NUM_PERM) -> tuple[int, ...]:
    """Deterministic MinHash signature (identical text -> identical signature)."""
    shingles = _shingles(text)
    if not shingles:
        return tuple([0] * num_perm)
    sig = []
    for seed in range(num_perm):
        sig.append(min(_hash_shingle(s, seed) for s in shingles))
    return tuple(sig)


def estimate_jaccard(sig_a: tuple[int, ...], sig_b: tuple[int, ...]) -> float:
    if not sig_a or len(sig_a) != len(sig_b):
        return 0.0
    equal = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
    return equal / len(sig_a)


class ChunkVersioner:
    def __init__(self, chunk_repo: ChunkRepository, threshold: float = 0.6) -> None:
        self._repo = chunk_repo
        self.threshold = threshold

    def match(self, new_chunk: Chunk, candidates: list[Chunk]) -> MatchResult:
        """Find the best-matching existing chunk above the similarity threshold."""
        new_sig = minhash_signature(new_chunk.text)
        best_id = None
        best_sim = 0.0
        for cand in candidates:
            sim = estimate_jaccard(new_sig, minhash_signature(cand.text))
            if sim > best_sim:
                best_sim, best_id = sim, cand.id
        if best_id is not None and best_sim >= self.threshold:
            return MatchResult(status=Status.OK, matched_chunk_id=best_id, similarity=best_sim)
        return MatchResult(status=Status.NOT_FOUND, similarity=best_sim)

    def apply_version(self, new_chunk: Chunk, match: MatchResult) -> VersionResult:
        """Persist the new chunk as an updated version or a brand-new v1."""
        if match.status == Status.OK and match.matched_chunk_id:
            target_id = match.matched_chunk_id
            next_version = self._repo.latest_version(target_id) + 1
            # Re-key the incoming content onto the matched chunk's identity so
            # history accumulates on one chunk_id (US-4.2).
            versioned = Chunk(
                id=target_id, text=new_chunk.text, source_path=new_chunk.source_path,
                ordinal=new_chunk.ordinal, kind=new_chunk.kind,
                tags=new_chunk.tags, metadata=new_chunk.metadata,
            )
            self._repo.upsert_new_version(versioned, next_version)
            return VersionResult(chunk_id=target_id, version=next_version, is_new=False)
        # New chunk -> version 1.
        self._repo.upsert_new_version(new_chunk, 1)
        return VersionResult(chunk_id=new_chunk.id, version=1, is_new=True)
