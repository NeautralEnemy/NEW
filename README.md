# Daggerfall-Like RPG Prototype (Ursina)

## Overview
This is a minimal, playable open-world RPG prototype inspired by classic Daggerfall-style exploration. It features streamed terrain chunks, points of interest (towns and dungeon entrances), a procedural dungeon scene with simple enemies, and a basic combat loop.

## Requirements
- Python 3.11+
- Windows (tested workflow), but it should run anywhere Ursina runs.

## Setup (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
Choose one:
```bash
python main.py
```
Or double-click:
```
run.bat
```

## Controls
- **WASD**: Move
- **Shift**: Sprint
- **Space**: Jump
- **Mouse**: Look
- **Left Click**: Melee attack
- **E**: Interact (POIs, dungeon portal)
- **ESC**: Toggle pause menu / mouse lock
- **F1**: Toggle debug HUD

## How Chunk Streaming Works
- The world is split into square chunks (configurable in `config.py`).
- A chunk generation queue is processed incrementally each frame (`CHUNKS_PER_FRAME`).
- The `ChunkManager` loads chunks around the player within `VIEW_DISTANCE` and unloads far chunks.
- Each chunk builds a single mesh to keep entity counts low.

## Save / Load
- The game auto-loads `save.json` on startup (if present).
- Saving happens on quit or when you use the pause menu.
- The save includes the seed, player position, and discovered POIs.

## Known Limitations (v0.1)
- Terrain is simple and lacks detailed biome variation.
- Enemy AI is basic (direct chase).
- Dungeon generation is minimal; only a basic walk-based layout.
- No inventory or quest systems yet.

## Next Steps (v0.2 ideas)
- Add biomes and varied POI structures.
- Improve dungeon generation with rooms and keys/doors.
- Add ranged enemies and loot.
- Implement inventory, equipment, and leveling systems.
