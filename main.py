"""Entry point for the Daggerfall-like RPG prototype."""
from __future__ import annotations

import math
import random

from panda3d.core import loadPrcFileData

from ursina import (
    Ursina,
    Entity,
    Text,
    Button,
    color,
    held_keys,
    mouse,
    application,
    time,
    Vec3,
    Sky,
    DirectionalLight,
    AmbientLight,
    window,
    destroy,
)

import config
from combat.combat import CombatSystem
from dungeon.dungeon_scene import DungeonScene
from player.player_controller import PlayerController
from systems.save_system import SaveSystem
from systems.state import GameState
from ui.hud import HUD
from world.chunk_manager import ChunkManager
from world.poi import nearest_poi


class PauseMenu(Entity):
    def __init__(self, resume_callback, new_world_callback, quit_callback):
        super().__init__(enabled=False)
        self.bg = Entity(parent=self, model='quad', scale=(0.6, 0.6), color=color.rgba(0, 0, 0, 180))
        self.resume_btn = Button(text='Resume', parent=self, scale=(0.3, 0.08), y=0.1,
                                 on_click=resume_callback)
        self.new_world_btn = Button(text='New World', parent=self, scale=(0.3, 0.08), y=0.0,
                                    on_click=new_world_callback)
        self.quit_btn = Button(text='Quit', parent=self, scale=(0.3, 0.08), y=-0.1,
                               on_click=quit_callback)

    def toggle(self):
        self.enabled = not self.enabled


class Game:
    def __init__(self, app):
        self.app = app
        self.state = GameState()
        self.save_system = SaveSystem()
        self.seed = config.SEED
        self.chunk_manager = ChunkManager(seed=self.seed)
        self.dungeon = DungeonScene()
        self.player = PlayerController()
        self.combat = CombatSystem()
        self.hud = HUD()
        self.pause_menu = PauseMenu(self.resume_game, self.new_world, self.quit_game)
        self.discovered_pois = []
        self.last_dungeon_entrance = None
        loaded = self.load_save()
        if not loaded:
            self.player.spawn_point = self.chunk_manager.spawn_point()
            self.player.position = self.player.spawn_point

        self.sky = Sky()
        self.sun = DirectionalLight()
        self.ambient = AmbientLight(color=color.rgba(120, 120, 120, 255))

        mouse.locked = True
        self.player.cursor.enabled = False

        if config.SHOW_FPS:
            Text(text='', position=(0.7, 0.45), origin=(0, 0), scale=1, name='fps_counter')

        self.chunk_manager.update(self.player.position)

    def load_save(self):
        data = self.save_system.load()
        if not data:
            return False
        self.seed = data.get('seed', self.seed)
        saved_pos = data.get('player_pos')
        if saved_pos:
            self.player.position = Vec3(*saved_pos)
        self.discovered_pois = data.get('discovered_pois', [])
        self.chunk_manager.seed = self.seed
        return True

    def save(self):
        self.save_system.save(self.seed, self.player.position, self.discovered_pois)

    def new_world(self):
        self.save_system.clear()
        self.seed = random.randint(1000, 9999)
        self.chunk_manager.parent.disable()
        destroy(self.chunk_manager.parent)
        self.chunk_manager = ChunkManager(seed=self.seed)
        self.player.spawn_point = self.chunk_manager.spawn_point()
        self.player.position = self.player.spawn_point
        self.discovered_pois = []
        self.resume_game()

    def resume_game(self):
        if self.pause_menu.enabled:
            self.pause_menu.toggle()
            mouse.locked = True
            self.player.cursor.enabled = False

    def pause_game(self):
        if not self.pause_menu.enabled:
            self.pause_menu.toggle()
            mouse.locked = False
            self.player.cursor.enabled = True

    def quit_game(self):
        self.save()
        application.quit()

    def update(self):
        if self.pause_menu.enabled:
            return

        if self.state.current == GameState.OUTSIDE_WORLD:
            self.update_outside()
        else:
            self.update_dungeon()

        self.update_hud()

    def update_outside(self):
        self.chunk_manager.update(self.player.position)
        if held_keys['left mouse']:
            self.combat.attack(self.player, {})

    def update_dungeon(self):
        for enemy in list(self.dungeon.enemies.values()):
            enemy.update(self.player)
        if held_keys['left mouse']:
            self.combat.attack(self.player, self.dungeon.enemies)
        if self.player.health <= 0:
            self.reset_player()

    def reset_player(self):
        self.player.health = config.PLAYER_MAX_HEALTH
        self.player.position = self.player.spawn_point
        self.state.current = GameState.OUTSIDE_WORLD
        self.dungeon.disable()
        self.chunk_manager.parent.enabled = True

    def handle_interaction(self):
        hit = self.player.raycast_forward(distance=3.0)
        if not hit:
            return
        poi_map = {poi.entity: poi for poi in self.chunk_manager.all_pois() if poi.entity}
        if hit.entity in poi_map:
            poi = poi_map[hit.entity]
            if poi.kind == 'dungeon':
                self.enter_dungeon(poi)
            else:
                if poi.name not in self.discovered_pois:
                    self.discovered_pois.append(poi.name)
        elif self.dungeon.portal and hit.entity == self.dungeon.portal:
            self.exit_dungeon()

    def enter_dungeon(self, poi):
        self.last_dungeon_entrance = poi.position
        self.state.current = GameState.DUNGEON
        self.chunk_manager.parent.enabled = False
        self.dungeon.build(seed=self.seed + 999)
        self.dungeon.enable()
        self.player.position = (config.DUNGEON_SIZE // 2, 2, config.DUNGEON_SIZE // 2)

    def exit_dungeon(self):
        self.state.current = GameState.OUTSIDE_WORLD
        self.dungeon.disable()
        self.chunk_manager.parent.enabled = True
        if self.last_dungeon_entrance:
            self.player.position = self.last_dungeon_entrance + (0, 2, 0)

    def update_hud(self):
        chunk_coords = self.chunk_manager.world_to_chunk(self.player.position)
        nearest = nearest_poi(self.chunk_manager.all_pois(), self.player.position)
        poi_text = "Nearest POI: --"
        if nearest:
            poi, dist = nearest
            direction = self.direction_to_poi(poi)
            poi_text = f"Nearest POI: {poi.name} ({dist:.1f}m, {direction})"
        interact_text = ""
        hit = self.player.raycast_forward(distance=3.0)
        if hit:
            if hit.entity in {poi.entity for poi in self.chunk_manager.all_pois()}:
                interact_text = "Press E to interact"
            elif self.dungeon.portal and hit.entity == self.dungeon.portal:
                interact_text = "Press E to return"
        self.hud.update(
            player=self.player,
            chunk_coords=chunk_coords,
            seed=self.seed,
            poi_text=poi_text,
            debug_lines=list(self.chunk_manager.debug_log),
            interact_text=interact_text,
        )

    def direction_to_poi(self, poi):
        delta = poi.position - self.player.position
        angle = math.degrees(math.atan2(delta.z, delta.x))
        directions = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
        index = int(((angle + 360 + 22.5) % 360) / 45)
        return directions[index]

    def input(self, key):
        if key == 'escape':
            if self.pause_menu.enabled:
                self.resume_game()
            else:
                self.pause_game()
        elif key == 'e':
            if not self.pause_menu.enabled:
                self.handle_interaction()
        elif key == 'f1':
            self.hud.toggle_debug()



def update():
    if hasattr(application, 'game_instance'):
        application.game_instance.update()


def input(key):
    if hasattr(application, 'game_instance'):
        application.game_instance.input(key)


if __name__ == '__main__':
    loadPrcFileData('', 'win-size 1536 864')
    app = Ursina()
    window.size = (int(1536), int(864))
    game = Game(app)
    application.game_instance = game
    app.run()
