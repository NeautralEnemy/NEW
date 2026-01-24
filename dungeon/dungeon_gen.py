"""Procedural dungeon layout generation."""
from __future__ import annotations

import random
from typing import List, Tuple

from config import DUNGEON_SIZE, DUNGEON_STEPS, DUNGEON_ROOM_CHANCE


def generate_layout(seed: int) -> List[List[int]]:
    rng = random.Random(seed)
    grid = [[0 for _ in range(DUNGEON_SIZE)] for _ in range(DUNGEON_SIZE)]
    x = z = DUNGEON_SIZE // 2
    grid[z][x] = 1

    for _ in range(DUNGEON_STEPS):
        dx, dz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        x = max(1, min(DUNGEON_SIZE - 2, x + dx))
        z = max(1, min(DUNGEON_SIZE - 2, z + dz))
        grid[z][x] = 1
        if rng.random() < DUNGEON_ROOM_CHANCE:
            for rx in range(-1, 2):
                for rz in range(-1, 2):
                    grid[z + rz][x + rx] = 1

    return grid
