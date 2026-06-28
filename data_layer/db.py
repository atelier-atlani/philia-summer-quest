import sqlite3
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_DB_PATH = _ROOT / "data" / "philia.db"
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db_path() -> Path:
    return _DB_PATH


def create_db() -> None:
    """Crée data/philia.db, applique le schéma de base et les migrations."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(_DB_PATH) as conn:
        conn.executescript(schema)
        _appliquer_migrations(conn)
        conn.commit()


def _appliquer_migrations(conn: sqlite3.Connection) -> None:
    """
    Applique les migrations ALTER TABLE via PRAGMA table_info().
    Idempotent. Toutes les futures migrations Sprint 4+ s'ajoutent ici.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(joueurs)")}

    # Sprint 3 T7 — filet de sécurité (déjà dans schema.sql)
    if "cles_obtenues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cles_obtenues TEXT DEFAULT '{}'")
    if "cristaux_obtenus" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cristaux_obtenus TEXT DEFAULT '{}'")

    # Sprint 3 T8.1
    if "planches_bd_vues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN planches_bd_vues TEXT DEFAULT '{}'")


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion à la base (la crée si absente)."""
    if not _DB_PATH.exists():
        create_db()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
