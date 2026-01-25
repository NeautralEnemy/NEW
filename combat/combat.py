"""Combat utilities for melee attacks."""
from __future__ import annotations

from ursina import time

from config import MELEE_COOLDOWN, MELEE_DAMAGE, MELEE_RANGE


class CombatSystem:
    def __init__(self) -> None:
        self.last_attack = 0.0

    def can_attack(self) -> bool:
        return time.time() - self.last_attack >= MELEE_COOLDOWN

    def attack(self, player, enemies) -> None:
        if not self.can_attack():
            return
        hit = player.raycast_forward(distance=MELEE_RANGE)
        if hit and hit.entity in enemies:
            enemies[hit.entity].take_damage(MELEE_DAMAGE)
        self.last_attack = time.time()
