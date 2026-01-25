"""First-person controller wrapper for Ursina."""
from __future__ import annotations

from ursina import Entity, Vec3, time, held_keys, mouse, raycast, color
from ursina.prefabs.first_person_controller import FirstPersonController

from config import MOVE_SPEED, SPRINT_MULTIPLIER, JUMP_HEIGHT, GRAVITY, MOUSE_SENSITIVITY, PLAYER_MAX_HEALTH


class PlayerController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = MOVE_SPEED
        self.jump_height = JUMP_HEIGHT
        self.gravity = GRAVITY
        self.cursor.enabled = False
        self.mouse_sensitivity = Vec3(MOUSE_SENSITIVITY, MOUSE_SENSITIVITY, 0)
        self.health = PLAYER_MAX_HEALTH
        self.spawn_point = Vec3(0, 6, 0)
        self.position = self.spawn_point

    def update(self) -> None:
        self.speed = MOVE_SPEED * (SPRINT_MULTIPLIER if held_keys['shift'] else 1.0)
        super().update()

    def toggle_mouse(self) -> None:
        mouse.locked = not mouse.locked
        self.cursor.enabled = not mouse.locked

    def raycast_forward(self, distance: float = 3.0):
        return raycast(self.camera_pivot.world_position, self.camera_pivot.forward, distance=distance,
                       ignore=[self, ], debug=False)
