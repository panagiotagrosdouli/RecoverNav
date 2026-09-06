from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from typing import Callable

from recovernav.environment import Cell, GridEnvironment

StepPenalty = Callable[[Cell], float]


@dataclass(frozen=True)
class PlanResult:
    path: list[Cell]
    cost: float
    expanded_nodes: int
    planning_time: float
    success: bool


def _heuristic(a: Cell, b: Cell) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(env: GridEnvironment, start: Cell, goal: Cell, step_penalty: StepPenalty | None = None) -> PlanResult:
    t0 = time.perf_counter()
    if not env.is_free(start) or not env.is_free(goal):
        return PlanResult([], math.inf, 0, time.perf_counter() - t0, False)
    frontier: list[tuple[float, int, Cell]] = [(float(_heuristic(start, goal)), 0, start)]
    came_from: dict[Cell, Cell | None] = {start: None}
    g_score: dict[Cell, float] = {start: 0.0}
    tie = 0
    expanded = 0
    while frontier:
        _, _, current = heapq.heappop(frontier)
        expanded += 1
        if current == goal:
            path: list[Cell] = []
            node: Cell | None = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return PlanResult(path, g_score[goal], expanded, time.perf_counter() - t0, True)
        for nxt in env.neighbors(current):
            penalty = 0.0 if step_penalty is None else max(0.0, float(step_penalty(nxt)))
            tentative = g_score[current] + 1.0 + penalty
            if tentative < g_score.get(nxt, math.inf):
                g_score[nxt] = tentative
                came_from[nxt] = current
                tie += 1
                heapq.heappush(frontier, (tentative + _heuristic(nxt, goal), tie, nxt))
    return PlanResult([], math.inf, expanded, time.perf_counter() - t0, False)
