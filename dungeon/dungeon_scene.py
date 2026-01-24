"""Dungeon scene handling."""
from __future__ import annotations

import random
from typing import Dict, List

from ursina import Entity, Vec3, color

from config import ENEMY_SPAWN_MIN, ENEMY_SPAWN_MAX
from dungeon.dungeon_gen import generate_layout
from enemies.enemy import Enemy


class DungeonScene:
    def __init__(self) -> None:
        self.parent = Entity(enabled=False)
        self.layout = []
        self.enemies: Dict[Entity, Enemy] = {}
        self.portal = None
        self.seed = 0

    def build(self, seed: int) -> None:
        self.clear()
        self.seed = seed
        self.layout = generate_layout(seed)
        size = len(self.layout)

        for z in range(size):
            for x in range(size):
                if self.layout[z][x] == 1:
                    Entity(
                        model='cube',
                        scale=(1, 0.2, 1),
                        position=Vec3(x, 0, z),
                        color=color.rgb(90, 90, 100),
                        parent=self.parent,
                        collider='box',
                    )
                else:
                    Entity(
                        model='cube',
                        scale=(1, 2, 1),
                        position=Vec3(x, 1, z),
                        color=color.rgb(40, 40, 50),
                        parent=self.parent,
                        collider='box',
                    )

        self.portal = Entity(
            model='cube',
            scale=(1.5, 2, 0.5),
            position=Vec3(size // 2, 1, size // 2),
            color=color.rgb(120, 220, 200),
            parent=self.parent,
            collider='box',
        )

        rng = random.Random(seed)
        for _ in range(rng.randint(ENEMY_SPAWN_MIN, ENEMY_SPAWN_MAX)):
            pos = Vec3(rng.randint(2, size - 3), 1, rng.randint(2, size - 3))
            ent = Entity(model='cube', color=color.red, position=pos, scale=1, parent=self.parent, collider='box')
            self.enemies[ent] = Enemy(entity=ent)

    def clear(self) -> None:
        for entity in list(self.enemies.keys()):
            entity.disable()
            entity.delete()
        self.enemies.clear()
        if self.portal:
            self.portal.disable()
            self.portal.delete()
            self.portal = None
        for child in list(self.parent.children):
            child.disable()
            child.delete()
        self.layout = []

    def enable(self) -> None:
        self.parent.enabled = True

    def disable(self) -> None:
        self.parent.enabled = False
