from __future__ import annotations

from recovernav.environment import Cell, GridEnvironment


def degree_score(env: GridEnvironment, cell: Cell) -> float:
    if not env.is_free(cell):
        return 0.0
    return min(len(env.neighbors(cell)) / 4.0, 1.0)
