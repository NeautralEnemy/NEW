"""Points of interest generation and helpers."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ursina import Entity, color, Vec3

from config import CHUNK_SIZE, TILE_SCALE, TOWN_CHANCE, DUNGEON_CHANCE, NOISE_SCALE, HEIGHT_SCALE
from world.noise import fbm_noise_2d


@dataclass
class POI:
    name: str
    position: Vec3
    kind: str
    entity: Optional[Entity] = None


def generate_pois_for_chunk(cx: int, cz: int, seed: int) -> List[POI]:
    rng = random.Random(f"{seed}:{cx}:{cz}")
    pois: List[POI] = []

    if cx == 0 and cz == 0:
        x = (CHUNK_SIZE // 2) * TILE_SCALE
        z = (CHUNK_SIZE // 2) * TILE_SCALE
        height = terrain_height(x, z, seed)
        pois.append(POI(name="Start Town", position=Vec3(x, height, z), kind="town"))

    if (cx, cz) != (0, 0) and rng.random() < TOWN_CHANCE:
        x = (cx * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        z = (cz * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        height = terrain_height(x, z, seed)
        pois.append(POI(name=f"Town {cx},{cz}", position=Vec3(x, height, z), kind="town"))

    if rng.random() < DUNGEON_CHANCE:
        x = (cx * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        z = (cz * CHUNK_SIZE + rng.randint(2, CHUNK_SIZE - 2)) * TILE_SCALE
        height = terrain_height(x, z, seed)
        pois.append(POI(name=f"Dungeon {cx},{cz}", position=Vec3(x, height, z), kind="dungeon"))

    return pois


def spawn_poi_entities(pois: List[POI], parent: Entity, seed: int) -> None:
    for poi in pois:
        if poi.kind == "town":
            poi.entity = Entity(position=poi.position, parent=parent)
            for offset in [Vec3(0, 0, 0), Vec3(2, 0, 2), Vec3(-2, 0, -2)]:
                house_x = poi.position.x + offset.x
                house_z = poi.position.z + offset.z
                house_y = terrain_height(house_x, house_z, seed) + 0.75
                Entity(
                    model='cube',
                    color=color.rgb(160, 120, 80),
                    scale=(2, 1.5, 2),
                    position=Vec3(house_x, house_y, house_z),
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


def terrain_height(x: float, z: float, seed: int) -> float:
    noise = fbm_noise_2d(x * NOISE_SCALE, z * NOISE_SCALE, seed)
    return (noise - 0.5) * 2 * HEIGHT_SCALE
