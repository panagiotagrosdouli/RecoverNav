from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from recovernav.robot import NavigationState, Robot
from recovernav.scenarios import make_scenario


def draw(ax, robot: Robot, title: str) -> None:
    ax.clear()
    ax.imshow(robot.env.as_occupancy(), cmap="gray_r", origin="upper", vmin=0, vmax=1)
    if robot.current_path:
        ys, xs = zip(*robot.current_path); ax.plot(xs, ys, linewidth=2, label="planned path")
    if robot.trajectory:
        ys, xs = zip(*robot.trajectory); ax.plot(xs, ys, linewidth=2, label="executed")
    ax.scatter(robot.goal[1], robot.goal[0], marker="*", s=140, label="goal")
    ax.scatter(robot.position[1], robot.position[0], marker="o", s=90, label="robot")
    ax.set_title(f"{title} — {robot.state.name.replace('_', ' ')}")
    ax.set_xticks([]); ax.set_yticks([]); ax.legend(loc="upper right")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--planner", choices=["baseline", "recovernav"], default="baseline")
    parser.add_argument("--scenario", default="two_routes")
    parser.add_argument("--lambda-recovery", type=float, default=2.5)
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--output", default="results/demo_navigation.png")
    args = parser.parse_args()
    scenario = make_scenario(args.scenario, seed=0)
    robot = Robot(scenario.environment.copy(), scenario.start, scenario.goal, planner=args.planner, lambda_recovery=args.lambda_recovery, recovery_radius=args.radius)
    robot.plan()
    fig, ax = plt.subplots(figsize=(10, 5))
    inserted = False; paused = False; steps = 0; event_phase = 0

    def tick(_frame: int, force: bool = False) -> None:
        nonlocal inserted, paused, steps, event_phase
        if (paused and not force) or robot.state in {NavigationState.GOAL_REACHED, NavigationState.FAILED}:
            draw(ax, robot, args.planner); return
        if not inserted and scenario.event_step is not None and steps == scenario.event_step:
            if scenario.dynamic_obstacle is not None: robot.env.add_dynamic_obstacle(scenario.dynamic_obstacle)
            inserted = True
            if robot.path_blocked():
                event_phase = 1; draw(ax, robot, f"{args.planner} — PATH BLOCKED"); return
        if event_phase == 1:
            event_phase = 2; draw(ax, robot, f"{args.planner} — REPLANNING"); return
        robot.step(); event_phase = 0; steps += 1; draw(ax, robot, args.planner)

    def on_key(event) -> None:
        nonlocal paused, inserted, steps, robot, event_phase
        if event.key == " ": paused = not paused
        elif event.key == "n": paused = True; tick(0, force=True)
        elif event.key == "o" and scenario.dynamic_obstacle is not None: robot.env.add_dynamic_obstacle(scenario.dynamic_obstacle); inserted = True
        elif event.key == "p": robot.plan(replanning=True)
        elif event.key == "1": robot.planner = "baseline"; robot.plan(replanning=True)
        elif event.key == "2": robot.planner = "recovernav"; robot.plan(replanning=True)
        elif event.key == "r":
            robot = Robot(scenario.environment.copy(), scenario.start, scenario.goal, planner=args.planner, lambda_recovery=args.lambda_recovery, recovery_radius=args.radius)
            robot.plan(); inserted = False; steps = 0; event_phase = 0

    fig.canvas.mpl_connect("key_press_event", on_key)
    if args.headless or os.environ.get("MPLBACKEND", "").lower() == "agg":
        for _ in range(1000):
            if robot.state in {NavigationState.GOAL_REACHED, NavigationState.FAILED}: break
            tick(0)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        draw(ax, robot, args.planner); fig.tight_layout(); fig.savefig(args.output, dpi=150)
        print(f"state={robot.state.name} replans={robot.replans} steps={steps} output={args.output}")
    else:
        FuncAnimation(fig, tick, interval=220, cache_frame_data=False); plt.show()


if __name__ == "__main__": main()
