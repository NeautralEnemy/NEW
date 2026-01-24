"""HUD elements for debug and player status."""
from __future__ import annotations

from ursina import Text, color


class HUD:
    def __init__(self) -> None:
        self.health_text = Text(text="Health: 100", position=(-0.85, 0.45), scale=1.2)
        self.chunk_text = Text(text="Chunk: 0,0", position=(-0.85, 0.40), scale=1)
        self.seed_text = Text(text="Seed: 0", position=(-0.85, 0.35), scale=1)
        self.poi_text = Text(text="Nearest POI: --", position=(-0.85, 0.30), scale=1)
        self.interact_text = Text(text="", position=(0, -0.2), origin=(0, 0), color=color.azure)
        self.debug_log = Text(text="", position=(0.45, 0.45), scale=0.8)
        self.show_debug = True

    def update(self, player, chunk_coords, seed, poi_text, debug_lines, interact_text):
        self.health_text.text = f"Health: {player.health}"
        self.chunk_text.text = f"Chunk: {chunk_coords[0]},{chunk_coords[1]}"
        self.seed_text.text = f"Seed: {seed}"
        self.poi_text.text = poi_text
        self.debug_log.text = "\n".join(debug_lines) if self.show_debug else ""
        self.interact_text.text = interact_text

    def toggle_debug(self) -> None:
        self.show_debug = not self.show_debug
