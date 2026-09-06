from __future__ import annotations

from recovernav.environment import Cell, GridEnvironment
from recovernav.planners.astar import PlanResult, astar
from recovernav.recoverability.local_exits import local_exit_score


def recoverability_astar(env: GridEnvironment, start: Cell, goal: Cell, lambda_recovery: float = 2.0, radius: int = 3) -> PlanResult:
    if lambda_recovery < 0:
        raise ValueError("lambda_recovery must be non-negative")
    def penalty(cell: Cell) -> float:
        return lambda_recovery * (1.0 - local_exit_score(env, cell, radius=radius))
    return astar(env, start, goal, step_penalty=penalty)
