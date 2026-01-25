"""Simple enemy AI."""
from __future__ import annotations

from dataclasses import dataclass

from ursina import Entity, Vec3, color, time, destroy

from config import ENEMY_SPEED, ENEMY_DAMAGE, ENEMY_ATTACK_COOLDOWN, ENEMY_HEALTH


@dataclass
class Enemy:
    entity: Entity
    health: int = ENEMY_HEALTH
    last_attack: float = 0.0

    def update(self, player) -> None:
        direction = (player.position - self.entity.position)
        distance = direction.length()
        if distance > 0.1:
            self.entity.position += direction.normalized() * ENEMY_SPEED * time.dt
        if distance < 1.6 and time.time() - self.last_attack > ENEMY_ATTACK_COOLDOWN:
            player.health = max(0, player.health - ENEMY_DAMAGE)
            self.last_attack = time.time()

    def take_damage(self, amount: int) -> None:
        self.health -= amount
        if self.health <= 0:
            self.entity.disable()
            destroy(self.entity)
