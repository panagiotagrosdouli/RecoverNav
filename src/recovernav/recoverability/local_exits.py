from __future__ import annotations

from collections import deque

import numpy as np

from recovernav.environment import Cell, GridEnvironment


def local_exit_score(env: GridEnvironment, cell: Cell, radius: int = 3) -> float:
    """Structural recoverability score in [0, 1].

    The score combines the number of distinct sides of a local window that are
    reachable from ``cell`` and the fraction of local free space reachable from it.
    It is deliberately structural; it is not a probability of successful recovery.
    """
    if radius < 1:
        raise ValueError("radius must be >= 1")
    if not env.is_free(cell):
        return 0.0

    r0, c0 = cell
    h, w = env.shape
    rmin, rmax = max(0, r0 - radius), min(h - 1, r0 + radius)
    cmin, cmax = max(0, c0 - radius), min(w - 1, c0 + radius)

    def inside(p: Cell) -> bool:
        return rmin <= p[0] <= rmax and cmin <= p[1] <= cmax

    reachable: set[Cell] = {cell}
    queue: deque[Cell] = deque([cell])
    while queue:
        current = queue.popleft()
        for nxt in env.neighbors(current):
            if inside(nxt) and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    sides: set[str] = set()
    for r, c in reachable:
        if r == rmin and rmin < r0:
            sides.add("N")
        if r == rmax and rmax > r0:
            sides.add("S")
        if c == cmin and cmin < c0:
            sides.add("W")
        if c == cmax and cmax > c0:
            sides.add("E")

    local_free = 0
    for r in range(rmin, rmax + 1):
        for c in range(cmin, cmax + 1):
            if env.is_free((r, c)):
                local_free += 1

    exit_component = len(sides) / 4.0
    area_component = len(reachable) / max(local_free, 1)
    score = 0.75 * exit_component + 0.25 * area_component
    return float(np.clip(score, 0.0, 1.0))


def recoverability_heatmap(env: GridEnvironment, radius: int = 3) -> np.ndarray:
    heat = np.full(env.shape, np.nan, dtype=float)
    for r in range(env.shape[0]):
        for c in range(env.shape[1]):
            if env.is_free((r, c)):
                heat[r, c] = local_exit_score(env, (r, c), radius=radius)
    return heat
