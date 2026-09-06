from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from recovernav.recoverability.local_exits import local_exit_score
from recovernav.robot import NavigationState, Robot
from recovernav.scenarios import Scenario


@dataclass(frozen=True)
class RunMetrics:
    scenario: str
    seed: int
    planner: str
    success: bool
    path_length: int
    executed_distance: int
    replans: int
    initial_planning_time: float
    replanning_time: float
    expanded_nodes: int
    min_q: float
    mean_q: float
    q_at_blockage: float | None
    dynamic_obstacle_position: str | None

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


def run_scenario(
    scenario: Scenario,
    planner: str,
    lambda_recovery: float = 2.0,
    recovery_radius: int = 3,
    max_steps: int = 1000,
) -> tuple[Robot, RunMetrics]:
    env = scenario.environment.copy()
    robot = Robot(
        env=env,
        position=scenario.start,
        goal=scenario.goal,
        planner=planner,
        lambda_recovery=lambda_recovery,
        recovery_radius=recovery_radius,
    )
    robot.plan()
    initial_path_length = max(len(robot.current_path) - 1, 0)
    q_values: list[float] = [local_exit_score(env, robot.position, recovery_radius)]
    q_at_blockage: float | None = None
    event_inserted = False

    for step_idx in range(max_steps):
        should_insert = (
            not event_inserted
            and scenario.event_step is not None
            and scenario.dynamic_obstacle is not None
            and step_idx == scenario.event_step
        )
        if should_insert:
            env.add_dynamic_obstacle(scenario.dynamic_obstacle)
            event_inserted = True
            if scenario.dynamic_obstacle in robot.remaining_path():
                q_at_blockage = local_exit_score(env, robot.position, recovery_radius)

        if robot.state in {NavigationState.GOAL_REACHED, NavigationState.FAILED}:
            break
        robot.step()
        q_values.append(local_exit_score(env, robot.position, recovery_radius))
    else:
        robot.state = NavigationState.FAILED

    metrics = RunMetrics(
        scenario=scenario.name,
        seed=scenario.seed,
        planner=planner,
        success=robot.state == NavigationState.GOAL_REACHED,
        path_length=initial_path_length,
        executed_distance=max(len(robot.trajectory) - 1, 0),
        replans=robot.replans,
        initial_planning_time=robot.planning_time,
        replanning_time=robot.replanning_time,
        expanded_nodes=robot.expanded_nodes,
        min_q=float(np.min(q_values)),
        mean_q=float(np.mean(q_values)),
        q_at_blockage=q_at_blockage,
        dynamic_obstacle_position=(str(scenario.dynamic_obstacle) if event_inserted else None),
    )
    return robot, metrics
