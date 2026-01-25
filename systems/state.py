"""Global game state handling."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GameState:
    OUTSIDE_WORLD = "outside"
    DUNGEON = "dungeon"

    current: str = OUTSIDE_WORLD
