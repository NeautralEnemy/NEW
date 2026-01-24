"""Chunk streaming manager with incremental generation."""
from __future__ import annotations

from collections import deque
import math
from typing import Deque, Dict, List, Tuple

from ursina import Entity, Vec3

from config import CHUNK_SIZE, VIEW_DISTANCE, CHUNKS_PER_FRAME
from world.chunk import Chunk
from world.poi import POI, generate_pois_for_chunk, spawn_poi_entities


class ChunkManager:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.parent = Entity()
        self.loaded: Dict[Tuple[int, int], Chunk] = {}
        self.pois: Dict[Tuple[int, int], List[POI]] = {}
        self.queue: Deque[Tuple[int, int]] = deque()
        self.debug_log: Deque[str] = deque(maxlen=6)

    def update(self, player_pos: Vec3) -> None:
        center_cx, center_cz = self.world_to_chunk(player_pos)
        desired = set()
        for dz in range(-VIEW_DISTANCE, VIEW_DISTANCE + 1):
            for dx in range(-VIEW_DISTANCE, VIEW_DISTANCE + 1):
                desired.add((center_cx + dx, center_cz + dz))

        for coords in desired:
            if coords not in self.loaded and coords not in self.queue:
                self.queue.append(coords)

        to_unload = [coords for coords in self.loaded if coords not in desired]
        for coords in to_unload:
            self.unload_chunk(coords)

        for _ in range(min(CHUNKS_PER_FRAME, len(self.queue))):
            coords = self.queue.popleft()
            self.load_chunk(coords)

    def load_chunk(self, coords: Tuple[int, int]) -> None:
        cx, cz = coords
        chunk = Chunk(cx=cx, cz=cz, seed=self.seed, parent=self.parent)
        chunk.build()
        self.loaded[coords] = chunk

        pois = generate_pois_for_chunk(cx, cz, self.seed)
        self.pois[coords] = pois
        spawn_poi_entities(pois, self.parent)
        self.debug_log.append(f"Loaded chunk {coords}")

    def unload_chunk(self, coords: Tuple[int, int]) -> None:
        chunk = self.loaded.pop(coords)
        chunk.destroy()
        for poi in self.pois.get(coords, []):
            if poi.entity:
                poi.entity.disable()
                poi.entity.delete()
        self.pois.pop(coords, None)
        self.debug_log.append(f"Unloaded chunk {coords}")

    def world_to_chunk(self, pos: Vec3) -> Tuple[int, int]:
        cx = math.floor(pos.x / CHUNK_SIZE)
        cz = math.floor(pos.z / CHUNK_SIZE)
        return int(cx), int(cz)

    def all_pois(self) -> List[POI]:
        all_pois: List[POI] = []
        for pois in self.pois.values():
            all_pois.extend(pois)
        return all_pois
