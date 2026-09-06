from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from recovernav.environment import Cell, GridEnvironment
from recovernav.planners.astar import PlanResult, astar
from recovernav.planners.recoverability_astar import recoverability_astar


class NavigationState(Enum):
    IDLE = auto()
    PLANNING = auto()
    MOVING = auto()
    PATH_BLOCKED = auto()
    REPLANNING = auto()
    GOAL_REACHED = auto()
    FAILED = auto()


@dataclass
class Robot:
    env: GridEnvironment
    position: Cell
    goal: Cell
    planner: str = "baseline"
    lambda_recovery: float = 2.0
    recovery_radius: int = 3
    state: NavigationState = NavigationState.IDLE
    current_path: list[Cell] = field(default_factory=list)
    trajectory: list[Cell] = field(default_factory=list)
    replans: int = 0
    planning_time: float = 0.0
    replanning_time: float = 0.0
    expanded_nodes: int = 0
    _path_index: int = 0

    def _plan_result(self) -> PlanResult:
        if self.planner == "baseline":
            return astar(self.env, self.position, self.goal)
        if self.planner == "recovernav":
            return recoverability_astar(
                self.env,
                self.position,
                self.goal,
                lambda_recovery=self.lambda_recovery,
                radius=self.recovery_radius,
            )
        raise ValueError(f"unknown planner: {self.planner}")

    def plan(self, replanning: bool = False) -> bool:
        self.state = NavigationState.REPLANNING if replanning else NavigationState.PLANNING
        result = self._plan_result()
        self.expanded_nodes += result.expanded_nodes
        if replanning:
            self.replanning_time += result.planning_time
            self.replans += 1
        else:
            self.planning_time += result.planning_time
        if not result.success:
            self.current_path = []
            self.state = NavigationState.FAILED
            return False
        self.current_path = result.path
        self._path_index = 0
        if not self.trajectory:
            self.trajectory.append(self.position)
        self.state = NavigationState.MOVING
        return True

    def remaining_path(self) -> list[Cell]:
        return self.current_path[self._path_index :]

    def path_blocked(self) -> bool:
        return not self.env.path_is_valid(self.remaining_path())

    def step(self) -> NavigationState:
        if self.position == self.goal:
            self.state = NavigationState.GOAL_REACHED
            return self.state
        if self.state in {NavigationState.IDLE, NavigationState.PLANNING}:
            if not self.plan():
                return self.state
        if self.path_blocked():
            self.state = NavigationState.PATH_BLOCKED
            if not self.plan(replanning=True):
                return self.state
        if self._path_index + 1 >= len(self.current_path):
            self.state = NavigationState.FAILED
            return self.state
        nxt = self.current_path[self._path_index + 1]
        if not self.env.is_free(nxt):
            self.state = NavigationState.PATH_BLOCKED
            if not self.plan(replanning=True):
                return self.state
            return self.step()
        self.position = nxt
        self._path_index += 1
        self.trajectory.append(self.position)
        if self.position == self.goal:
            self.state = NavigationState.GOAL_REACHED
        else:
            self.state = NavigationState.MOVING
        return self.state
