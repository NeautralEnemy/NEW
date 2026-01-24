"""Chunk representation and mesh generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from ursina import Entity, Mesh, color

from config import CHUNK_SIZE, TILE_SCALE, HEIGHT_SCALE, NOISE_SCALE, WATER_HEIGHT
from world.noise import fbm_noise_2d


@dataclass
class Chunk:
    cx: int
    cz: int
    seed: int
    parent: Entity
    entities: List[Entity] = field(default_factory=list)

    def build(self) -> None:
        """Build a low-entity terrain mesh for this chunk."""
        vertices: List[Tuple[float, float, float]] = []
        triangles: List[Tuple[int, int, int]] = []
        colors: List[color] = []

        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx = (self.cx * CHUNK_SIZE + x) * TILE_SCALE
                wz = (self.cz * CHUNK_SIZE + z) * TILE_SCALE
                height = self._height_at(wx, wz)

                base_index = len(vertices)
                vertices.extend([
                    (wx, height, wz),
                    (wx + TILE_SCALE, height, wz),
                    (wx + TILE_SCALE, height, wz + TILE_SCALE),
                    (wx, height, wz + TILE_SCALE),
                ])
                triangles.extend([
                    (base_index, base_index + 1, base_index + 2),
                    (base_index, base_index + 2, base_index + 3),
                ])

                tile_color = color.rgb(60, 160, 80)
                if height < WATER_HEIGHT + 0.5:
                    tile_color = color.rgb(50, 90, 180)
                elif height > HEIGHT_SCALE * 0.6:
                    tile_color = color.rgb(120, 120, 120)
                colors.extend([tile_color] * 4)

        mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors, mode='triangle')
        terrain = Entity(model=mesh, color=color.white, collider='mesh', parent=self.parent)
        self.entities.append(terrain)

    def destroy(self) -> None:
        for entity in self.entities:
            entity.disable()
            entity.delete()
        self.entities.clear()

    def _height_at(self, x: float, z: float) -> float:
        noise = fbm_noise_2d(x * NOISE_SCALE, z * NOISE_SCALE, self.seed)
        return (noise - 0.5) * 2 * HEIGHT_SCALE
