from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    DECOUVERTE    = "decouverte"
    PRATIQUE      = "pratique"
    VALIDATION    = "validation"
    CONSOLIDATION = "consolidation"
    BILAN         = "bilan"


# Transitions autorisées entre modes (ADN Archimède, section 7)
TRANSITIONS: dict[Mode, list[Mode]] = {
    Mode.DECOUVERTE:    [Mode.PRATIQUE, Mode.BILAN],  # BILAN accessible depuis DECOUVERTE (MVP direct)
    Mode.PRATIQUE:      [Mode.VALIDATION, Mode.DECOUVERTE],
    Mode.VALIDATION:    [Mode.CONSOLIDATION, Mode.DECOUVERTE],
    Mode.CONSOLIDATION: [Mode.PRATIQUE, Mode.BILAN],
    Mode.BILAN:         [Mode.DECOUVERTE],
}

# Seul Découverte est pleinement implémenté ce sprint. Les 4 autres sont
# déclarés mais bloqués — Sprint 3 les activera.
MODES_ACTIFS: frozenset[Mode] = frozenset({
    Mode.DECOUVERTE,
    Mode.PRATIQUE,
    Mode.BILAN,
})
