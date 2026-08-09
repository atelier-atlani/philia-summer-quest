import os
import sqlite3
from pathlib import Path

_ROOT = Path(__file__).parent.parent
# Chemin configurable via DB_PATH (persistance sur disque monté Render).
# Sans la variable, comportement inchangé : data/philia.db à la racine.
_DB_PATH = Path(os.getenv("DB_PATH", str(_ROOT / "data" / "philia.db")))
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Plusieurs familles écrivent désormais dans la même base (une ligne joueurs
# par partie). WAL laisse les lectures se poursuivre pendant une écriture, et
# busy_timeout fait patienter un écrivain concurrent au lieu de lever
# immédiatement "database is locked".
_ATTENTE_VERROU_S = 10.0

# Migrations déjà appliquées dans ce process, par chemin de base. Les tests
# réassignent _DB_PATH : mémoriser un simple booléen ferait sauter les
# migrations sur la base suivante.
_migrations_faites: set[str] = set()


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
    _migrations_faites.add(str(_DB_PATH))


def _garantir_migrations() -> None:
    """Applique les migrations à une base DÉJÀ existante, une fois par process.

    create_db() ne s'exécute que si le fichier est absent : sur un disque
    persistant (Render), une base créée par une version antérieure ne verrait
    jamais les migrations suivantes, et le code planterait sur une colonne
    manquante. Les migrations étant idempotentes (PRAGMA table_info), les
    rejouer au démarrage est sans risque.
    """
    if str(_DB_PATH) in _migrations_faites:
        return
    with sqlite3.connect(_DB_PATH, timeout=_ATTENTE_VERROU_S) as conn:
        _appliquer_migrations(conn)
        conn.commit()
    _migrations_faites.add(str(_DB_PATH))


def _appliquer_migrations(conn: sqlite3.Connection) -> None:
    """
    Applique les migrations ALTER TABLE via PRAGMA table_info().
    Idempotent. Toutes les futures migrations Sprint 4+ s'ajoutent ici.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(joueurs)")}
    if not cols:
        # Table absente : base vide ou schéma jamais appliqué. C'est le travail
        # de create_db(), pas celui d'une migration — rien à altérer ici.
        return

    # Sprint 3 T7 — filet de sécurité (déjà dans schema.sql)
    if "cles_obtenues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cles_obtenues TEXT DEFAULT '{}'")
    if "cristaux_obtenus" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cristaux_obtenus TEXT DEFAULT '{}'")

    # Sprint 3 T8.1
    if "planches_bd_vues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN planches_bd_vues TEXT DEFAULT '{}'")

    # Sprint 3 T8.5 — D19bis
    if "prenom" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN prenom TEXT")

    # Isolation des parties — une ligne joueurs par famille, identifiée par un
    # partie_id opaque porté par l'URL. SQLite ne sait pas ajouter une colonne
    # UNIQUE par ALTER TABLE : l'unicité passe donc par un index dédié.
    if "partie_id" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN partie_id TEXT")
    # Backfill des lignes antérieures à la colonne : sans identifiant, une
    # partie serait inatteignable. randomblob() est réévalué à chaque ligne,
    # chacune reçoit donc bien un identifiant distinct.
    conn.execute(
        "UPDATE joueurs SET partie_id = lower(hex(randomblob(9))) WHERE partie_id IS NULL"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_joueurs_partie_id ON joueurs(partie_id)"
    )


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion à la base (la crée si absente, la migre si besoin)."""
    if not _DB_PATH.exists():
        create_db()
    else:
        _garantir_migrations()
    conn = sqlite3.connect(_DB_PATH, timeout=_ATTENTE_VERROU_S)
    conn.row_factory = sqlite3.Row
    # WAL est une propriété persistante de la base ; busy_timeout est propre à
    # la connexion et doit donc être posé à chaque fois.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(f"PRAGMA busy_timeout={int(_ATTENTE_VERROU_S * 1000)}")
    return conn
