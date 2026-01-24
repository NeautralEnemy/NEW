"""Save/load utilities."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from config import SAVE_FILE


class SaveSystem:
    def __init__(self) -> None:
        self.path = Path(SAVE_FILE)

    def save(self, seed: int, player_pos, discovered_pois: List[str]) -> None:
        data = {
            "seed": seed,
            "player_pos": [player_pos.x, player_pos.y, player_pos.z],
            "discovered_pois": discovered_pois,
        }
        self.path.write_text(json.dumps(data, indent=2))

    def load(self):
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text())

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
