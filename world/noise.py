"""Lightweight 2D value noise implementation in pure Python."""
from __future__ import annotations

import math


def _hash(x: int, z: int, seed: int) -> int:
    value = x * 374761393 + z * 668265263 + seed * 1446647
    value = (value ^ (value >> 13)) * 1274126177
    return value ^ (value >> 16)


def _value_at(x: int, z: int, seed: int) -> float:
    return (_hash(x, z, seed) & 0xFFFF) / 65535.0


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def value_noise_2d(x: float, z: float, seed: int) -> float:
    xi = math.floor(x)
    zi = math.floor(z)
    xf = x - xi
    zf = z - zi

    v00 = _value_at(xi, zi, seed)
    v10 = _value_at(xi + 1, zi, seed)
    v01 = _value_at(xi, zi + 1, seed)
    v11 = _value_at(xi + 1, zi + 1, seed)

    u = _smoothstep(xf)
    v = _smoothstep(zf)
    x1 = _lerp(v00, v10, u)
    x2 = _lerp(v01, v11, u)
    return _lerp(x1, x2, v)


def fbm_noise_2d(x: float, z: float, seed: int, octaves: int = 4) -> float:
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    max_value = 0.0
    for _ in range(octaves):
        total += value_noise_2d(x * frequency, z * frequency, seed) * amplitude
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2.0
    return total / max_value if max_value else 0.0
