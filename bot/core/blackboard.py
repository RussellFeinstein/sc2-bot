"""Shared mutable state passed between all bot modules each step.

Modules read from and write to the Blackboard instead of calling each other directly.
This keeps coupling low and makes the decision flow explicit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import auto, Enum


class MacroAction(Enum):
    """Finite strategic action space.

    The ML decision layer selects one of these each decision cycle.
    Scripted execution modules interpret the active action.
    """
    DRONE_GREED = auto()          # Keep droning; minimal military spend
    STANDARD_MACRO = auto()       # Balanced drone + military growth
    PRESSURE_PUSH = auto()        # Build army; attack before opponent peaks
    FAST_EXPAND = auto()          # Take third/fourth base ahead of schedule
    TECH_TO_ROACH = auto()        # Pivot economy toward Roach production
    TECH_TO_LING_BANE = auto()    # Pivot toward Zergling/Baneling composition
    TECH_TO_MUTA = auto()         # Pivot toward Mutalisk air harassment
    TECH_TO_ULTRA = auto()        # Late-game Ultralisk transition
    DEFENSIVE_HOLD = auto()       # Spine crawlers + queens; survive, keep droning
    ALL_IN = auto()               # Spend everything; attack immediately
    SEND_SCOUT = auto()           # Priority scouting; pause other actions
    HOLD_AND_WAIT = auto()        # Preserve army; wait for upgrade or reinforcement timing


@dataclass
class Blackboard:
    """Mutable shared state for the current game step."""
    current_action: MacroAction = MacroAction.STANDARD_MACRO
    scouting_complete: bool = False
    enemy_opening_label: str = "unknown"
    enemy_attack_imminent: bool = False
    army_value_minerals: int = 0
    enemy_army_value_estimate: int = 0
    bases_taken: int = 1
    supply_used: int = 12
    drone_count: int = 12
    notes: list[str] = field(default_factory=list)

    def add_note(self, note: str) -> None:
        self.notes.append(note)

    def clear_notes(self) -> None:
        self.notes.clear()
