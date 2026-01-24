"""Points of interest generation and helpers."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ursina import Entity, color, Vec3

from config import CHUNK_SIZE, TILE_SCALE, TOWN_CHANCE, DUNGEON_CHANCE


@dataclass
class POI:
    name: str
    position: Vec3
    kind: str
    entity: Optional[Entity] = None


def generate_pois_for_chunk(cx: int, cz: int, seed: int) -> List[POI]:
    rng = random.Random(f"{seed}:{cx}:{cz}")
    pois: List[POI] = []

    if rng.random() < TOWN_CHANCE:
        x = (cx * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        z = (cz * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        pois.append(POI(name=f"Town {cx},{cz}", position=Vec3(x, 0, z), kind="town"))

    if rng.random() < DUNGEON_CHANCE:
        x = (cx * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        z = (cz * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        pois.append(POI(name=f"Dungeon {cx},{cz}", position=Vec3(x, 0, z), kind="dungeon"))

    return pois


def spawn_poi_entities(pois: List[POI], parent: Entity) -> None:
    for poi in pois:
        if poi.kind == "town":
            poi.entity = Entity(position=poi.position, parent=parent)
            for offset in [Vec3(0, 0, 0), Vec3(2, 0, 2), Vec3(-2, 0, -2)]:
                Entity(
                    model='cube',
                    color=color.rgb(160, 120, 80),
                    scale=(2, 1.5, 2),
                    position=poi.position + offset,
                    parent=poi.entity,
                    collider='box',
                )
        elif poi.kind == "dungeon":
            poi.entity = Entity(
                model='cube',
                color=color.rgb(120, 80, 180),
                scale=(2, 3, 0.5),
                position=poi.position + Vec3(0, 1.5, 0),
                parent=parent,
                collider='box',
            )


def nearest_poi(pois: List[POI], position: Vec3) -> Optional[Tuple[POI, float]]:
    best = None
    best_dist = math.inf
    for poi in pois:
        dist = (poi.position - position).length()
        if dist < best_dist:
            best = poi
            best_dist = dist
    if best is None:
        return None
    return best, best_dist
