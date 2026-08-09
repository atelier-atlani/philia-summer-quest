-- Philia Summer Quest — Schéma SQLite v1.0
-- 8 tables — source : philia-brief-implementer-technique-1a.md §2

CREATE TABLE IF NOT EXISTS parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    tier TEXT DEFAULT 'gratuit',
    stripe_customer_id TEXT,
    rgpd_consent INTEGER DEFAULT 0,
    rgpd_consent_date TEXT,
    date_creation TEXT
);

CREATE TABLE IF NOT EXISTS enfants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT NOT NULL,
    age INTEGER,
    classe TEXT,
    style_mentor TEXT,
    date_creation TEXT,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES parents(id)
);

CREATE TABLE IF NOT EXISTS progression_iles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    ile_id TEXT,
    niveau_elevation INTEGER DEFAULT 0,
    cristaux_obtenus TEXT,
    rite_reussi INTEGER DEFAULT 0,
    date_derniere_activite TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

CREATE TABLE IF NOT EXISTS maitrise_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    concept_id TEXT,
    ile_id TEXT,
    statut TEXT DEFAULT 'non_aborde',
    score_feynman INTEGER,
    date_validation TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

CREATE TABLE IF NOT EXISTS superpouvoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    maieutique INTEGER DEFAULT 0,
    transfert INTEGER DEFAULT 0,
    perseverance INTEGER DEFAULT 0,
    clarte INTEGER DEFAULT 0,
    creativite INTEGER DEFAULT 0,
    metacognition INTEGER DEFAULT 0,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    ile_id TEXT,
    date TEXT,
    duree_minutes INTEGER,
    concepts_travailles TEXT,
    expressions_mentor TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

CREATE TABLE IF NOT EXISTS mentor_etat (
    enfant_id INTEGER PRIMARY KEY,
    niveau_mentor INTEGER DEFAULT 1,
    elements_debloques TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

CREATE TABLE IF NOT EXISTS analogies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    concept_id TEXT,
    texte_analogie TEXT,
    date_creation TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Sprint 3 T6 — joueur MVP (single-player, avatar irréversible)
CREATE TABLE IF NOT EXISTS joueurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avatar_genre TEXT NOT NULL,
    avatar_prenom TEXT NOT NULL,
    avatar_role TEXT NOT NULL,
    date_creation TEXT NOT NULL,
    date_derniere_session TEXT
);

-- Sprint 3 T7 — récompenses du joueur (clés + cristaux)
-- Stockées en JSON sérialisé (TEXT). Lire/écrire via json.loads() / json.dumps().
-- Format cles_obtenues    : {"ile_1": "2026-07-05T14:23:00Z", ...}
-- Format cristaux_obtenus : {"ile_1": {"C1": "2026-07-05T14:23:00Z", ...}, ...}
ALTER TABLE joueurs ADD COLUMN cles_obtenues TEXT DEFAULT '{}';
ALTER TABLE joueurs ADD COLUMN cristaux_obtenus TEXT DEFAULT '{}';

-- Sprint 3 T8.1 — planches_bd_vues
-- Colonne gérée via _appliquer_migrations() dans db.py (pattern PRAGMA).
-- Format : {"ile_1_c1": "ISO8601", ...} — clé = f"{ile_id}_{planche_key}" (D-T8.1-D)

-- Sprint 3 T8.5 — prenom (prénom réel de l'enfant, D19bis)
-- Colonne gérée via _appliquer_migrations() dans db.py (pattern PRAGMA).
-- Distinct de avatar_prenom (prénom de l'avatar fictif, ex. "sassou").

-- Isolation des parties — partie_id (identifiant opaque porté par l'URL)
-- Colonne + index unique gérés via _appliquer_migrations() dans db.py.
-- UNE ligne joueurs PAR FAMILLE : c'est partie_id, jamais l'ordre des id,
-- qui désigne la partie courante.
