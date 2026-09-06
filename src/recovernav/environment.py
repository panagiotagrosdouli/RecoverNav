from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

Cell = tuple[int, int]


@dataclass
class GridEnvironment:
    grid: np.ndarray
    dynamic_obstacles: set[Cell] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.grid = np.asarray(self.grid, dtype=np.uint8)
        if self.grid.ndim != 2:
            raise ValueError("grid must be a 2D array")

    @property
    def shape(self) -> tuple[int, int]:
        return self.grid.shape

    def copy(self) -> "GridEnvironment":
        return GridEnvironment(self.grid.copy(), set(self.dynamic_obstacles))

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        h, w = self.grid.shape
        return 0 <= r < h and 0 <= c < w

    def is_free(self, cell: Cell) -> bool:
        if not self.in_bounds(cell):
            return False
        return self.grid[cell] == 0 and cell not in self.dynamic_obstacles

    def add_dynamic_obstacle(self, cell: Cell) -> None:
        if not self.in_bounds(cell):
            raise ValueError(f"obstacle {cell} is outside the map")
        self.dynamic_obstacles.add(cell)

    def remove_dynamic_obstacle(self, cell: Cell) -> None:
        self.dynamic_obstacles.discard(cell)

    def neighbors(self, cell: Cell) -> list[Cell]:
        r, c = cell
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [p for p in candidates if self.is_free(p)]

    def path_is_valid(self, path: Iterable[Cell]) -> bool:
        return all(self.is_free(cell) for cell in path)

    def as_occupancy(self) -> np.ndarray:
        occ = self.grid.copy()
        for cell in self.dynamic_obstacles:
            occ[cell] = 1
        return occ
