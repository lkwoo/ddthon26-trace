"""KnowledgeStore — SQLite connection, sqlite-vec loading, and schema management.

Owns the embedded database under ``<target>/.knowledge-store/`` (FR-8.2). The
sqlite-vec extension is loaded when available; otherwise the store operates in
a pure-Python fallback mode so installation stays dependency-light (NFR-4).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from knowledge_store.store import schema

DEFAULT_STORE_DIRNAME = ".knowledge-store"
_DB_FILENAME = "knowledge.db"


class KnowledgeStore:
    """Connection + schema manager for the embedded knowledge database."""

    def __init__(self, target_dir: str | Path, *, in_memory: bool = False) -> None:
        self.target_dir = Path(target_dir)
        self.store_dir = self.target_dir / DEFAULT_STORE_DIRNAME
        self._in_memory = in_memory
        self._conn: Optional[sqlite3.Connection] = None
        self._vec_enabled = False

    # -- lifecycle ---------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        """Open (once) and return the SQLite connection."""
        if self._conn is not None:
            return self._conn
        if self._in_memory:
            conn = sqlite3.connect(":memory:")
        else:
            self.store_dir.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.store_dir / _DB_FILENAME))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        self._vec_enabled = self._try_load_vec(conn)
        self._conn = conn
        return conn

    @staticmethod
    def _try_load_vec(conn: sqlite3.Connection) -> bool:
        """Attempt to load the sqlite-vec extension; return True on success."""
        try:
            import sqlite_vec  # type: ignore
        except Exception:
            return False
        try:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            return True
        except Exception:
            return False

    @property
    def vec_enabled(self) -> bool:
        return self._vec_enabled

    def init_schema(self, embedding_dimension: Optional[int] = None) -> None:
        """Create all tables. If vec is enabled and a dimension is given, create
        the vec0 virtual table; otherwise create the fallback BLOB table."""
        conn = self.connect()
        conn.executescript(schema.CORE_DDL)
        if self._vec_enabled and embedding_dimension:
            conn.execute(schema.vec_embedding_ddl(embedding_dimension))
        else:
            conn.executescript(schema.FALLBACK_EMBEDDING_DDL)
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)",
            (str(schema.SCHEMA_VERSION),),
        )
        conn.commit()

    def reindex(self) -> None:
        """Rebuild SQLite indexes/statistics (US-8.4 re-indexing support)."""
        conn = self.connect()
        conn.execute("REINDEX;")
        conn.execute("ANALYZE;")
        conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "KnowledgeStore":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()
