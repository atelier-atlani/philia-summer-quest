import sqlite3
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_DB_PATH = _ROOT / "data" / "philia.db"
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db_path() -> Path:
    return _DB_PATH


def create_db() -> None:
    """Crée data/philia.db et applique schema.sql (idempotent via ALTER TABLE)."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(_DB_PATH) as conn:
        for stmt in schema.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    pass  # colonne déjà présente, idempotent
                else:
                    raise
        conn.commit()


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion à la base (la crée si absente)."""
    if not _DB_PATH.exists():
        create_db()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
