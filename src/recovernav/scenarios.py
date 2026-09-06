from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from recovernav.environment import Cell, GridEnvironment


@dataclass(frozen=True)
class Scenario:
    name: str
    environment: GridEnvironment
    start: Cell
    goal: Cell
    event_step: int | None
    dynamic_obstacle: Cell | None
    seed: int = 0


def _bordered(h: int, w: int) -> np.ndarray:
    g = np.zeros((h, w), dtype=np.uint8)
    g[0, :] = g[-1, :] = 1
    g[:, 0] = g[:, -1] = 1
    return g


def _scenario_open_room(seed: int) -> Scenario:
    g = _bordered(15, 25)
    return Scenario("open_room", GridEnvironment(g), (7, 2), (7, 22), 7, (7, 13), seed)


def _scenario_corridor(seed: int) -> Scenario:
    g = np.ones((11, 25), dtype=np.uint8)
    g[5, 1:24] = 0
    g[4:7, 1] = 0
    g[4:7, 23] = 0
    return Scenario("corridor", GridEnvironment(g), (5, 1), (5, 23), 6, (5, 13), seed)


def _scenario_two_routes(seed: int) -> Scenario:
    g = np.ones((17, 31), dtype=np.uint8)
    g[8, 1:30] = 0
    g[3:7, 1:30] = 0
    g[3:9, 1:5] = 0
    g[3:9, 26:30] = 0
    return Scenario("two_routes", GridEnvironment(g), (8, 2), (8, 28), 5, (8, 16), seed)


def _scenario_bottleneck(seed: int) -> Scenario:
    g = _bordered(17, 29)
    g[2:15, 13] = 1
    g[8, 13] = 0
    g[3, 13] = 0
    g[2:6, 10:17] = 0
    return Scenario("bottleneck", GridEnvironment(g), (8, 3), (8, 25), 7, (8, 13), seed)


def _scenario_dead_end(seed: int) -> Scenario:
    g = np.ones((17, 29), dtype=np.uint8)
    g[8, 2:25] = 0
    g[5:9, 2] = 0
    g[5, 2:27] = 0
    g[5:9, 26] = 0
    return Scenario("dead_end", GridEnvironment(g), (8, 2), (8, 24), 8, (8, 16), seed)


def _scenario_multi_corridor(seed: int) -> Scenario:
    g = np.ones((19, 33), dtype=np.uint8)
    for r in (4, 9, 14):
        g[r, 1:32] = 0
    for c in (2, 10, 18, 26, 31):
        g[4:15, c] = 0
    return Scenario("multi_corridor", GridEnvironment(g), (9, 2), (9, 31), 9, (9, 18), seed)


_BUILDERS = {
    "open_room": _scenario_open_room,
    "corridor": _scenario_corridor,
    "two_routes": _scenario_two_routes,
    "bottleneck": _scenario_bottleneck,
    "dead_end": _scenario_dead_end,
    "multi_corridor": _scenario_multi_corridor,
}


def make_scenario(name: str, seed: int = 0) -> Scenario:
    if name not in _BUILDERS:
        raise KeyError(f"unknown scenario {name!r}; choose from {sorted(_BUILDERS)}")
    return _BUILDERS[name](seed)


def scenario_names() -> list[str]:
    return list(_BUILDERS)
