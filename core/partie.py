"""core/partie.py — Identité de la partie courante (isolation multi-familles).

Une base, plusieurs familles : c'est le partie_id qui désigne QUI joue, jamais
l'ordre des lignes en base. Ce module est la seule source de cette identité.

OÙ VIT L'IDENTITÉ
    - dans l'URL (`?partie=…`), parce que la carte navigue par liens HTML qui
      rechargent la page entière et vident st.session_state ;
    - en miroir dans st.session_state, pour les reruns internes.
    Les deux se réhydratent l'une l'autre, exactement comme le jeton d'accès
    de ui/ecran_acces.py, mécanisme déjà éprouvé en vrai navigateur.

LIEN INCONNU = PARTIE ADOPTÉE (arbitrage du Décideur)
    Un partie_id absent de la base n'est pas rejeté : l'onboarding crée la
    partie SOUS cet identifiant. C'est ce qui permet de pré-générer les liens
    et de les distribuer après paiement (tunnel semi-manuel, D50). Seule la
    FORME est vérifiée, pour qu'un paramètre absurde ne devienne pas une
    partie ; l'identifiant étant opaque, le deviner n'est pas praticable.

Point d'entrée principal : partie_courante()
"""

from __future__ import annotations

import re
import secrets

import streamlit as st

PARAM_URL = "partie"
CLE_SESSION = "partie_id"

# 9 octets = 18 caractères hexadécimaux, même format que le backfill SQL de la
# migration (lower(hex(randomblob(9)))). Assez large pour être non devinable,
# assez court pour tenir dans un lien qu'un parent garde en favori.
_OCTETS_ID = 9
_FORME_VALIDE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def generer_partie_id() -> str:
    """Identifiant opaque d'une nouvelle partie."""
    return secrets.token_hex(_OCTETS_ID)


def est_bien_forme(partie_id: str | None) -> bool:
    """Vrai si la chaîne peut servir d'identifiant de partie.

    Ne dit RIEN de son existence en base : un identifiant bien formé mais
    inconnu est légitime (lien pré-généré). Ne filtre que le grotesque.
    """
    return bool(partie_id) and bool(_FORME_VALIDE.match(partie_id))


def partie_courante() -> str | None:
    """Identifiant de la partie de ce visiteur, ou None s'il n'en a pas encore.

    L'URL prime sur la session : c'est elle que le parent conserve, et c'est
    elle qui survit au rechargement complet provoqué par les liens de la carte.
    """
    depuis_url = st.query_params.get(PARAM_URL)
    if est_bien_forme(depuis_url):
        if st.session_state.get(CLE_SESSION) != depuis_url:
            st.session_state[CLE_SESSION] = depuis_url
        return depuis_url

    depuis_session = st.session_state.get(CLE_SESSION)
    if est_bien_forme(depuis_session):
        # La session sait, l'URL a été écrasée (un href sans le paramètre) :
        # on la réinscrit, sinon le prochain rechargement perdrait la partie.
        st.query_params[PARAM_URL] = depuis_session
        return depuis_session

    return None


def poser_partie_courante(partie_id: str) -> None:
    """Installe la partie dans les deux mémoires (session + URL)."""
    if not est_bien_forme(partie_id):
        raise ValueError(f"partie_id mal formé : {partie_id!r}")
    st.session_state[CLE_SESSION] = partie_id
    st.query_params[PARAM_URL] = partie_id


def partie_courante_ou_nouvelle() -> str:
    """La partie du visiteur, en en créant une s'il n'en a pas.

    Appelé au moment de créer le joueur : un visiteur arrivé par un lien
    pré-généré garde SON identifiant, un visiteur nu en reçoit un neuf.
    """
    existante = partie_courante()
    if existante:
        return existante
    nouvelle = generer_partie_id()
    poser_partie_courante(nouvelle)
    return nouvelle


def parametres_url_partie() -> dict[str, str]:
    """Query params à reporter dans les liens HTML de navigation.

    Un href="?ile=X" écrase toute la query string : sans cette réinjection, un
    clic sur la carte ferait perdre la partie et l'enfant repartirait sur une
    partie vierge.
    """
    courante = st.session_state.get(CLE_SESSION) or st.query_params.get(PARAM_URL)
    return {PARAM_URL: courante} if est_bien_forme(courante) else {}
