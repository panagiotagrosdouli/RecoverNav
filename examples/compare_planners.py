from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from recovernav.execution import run_scenario
from recovernav.recoverability.local_exits import recoverability_heatmap
from recovernav.scenarios import make_scenario


def draw(ax, robot, title, metrics):
    ax.imshow(robot.env.as_occupancy(), cmap="gray_r", origin="upper", vmin=0, vmax=1)
    if robot.trajectory:
        ys, xs = zip(*robot.trajectory); ax.plot(xs, ys, linewidth=2)
    ax.scatter(robot.goal[1], robot.goal[0], marker="*", s=130)
    ax.scatter(robot.trajectory[0][1], robot.trajectory[0][0], marker="s", s=70)
    ax.set_title(f"{title}\nSuccess={metrics.success} Path={metrics.path_length} Exec={metrics.executed_distance} Replans={metrics.replans}\nMin Q={metrics.min_q:.2f} Plan={metrics.initial_planning_time*1000:.2f} ms")
    ax.set_xticks([]); ax.set_yticks([])


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--scenario", default="two_routes"); p.add_argument("--seed", type=int, default=0); p.add_argument("--lambda-recovery", type=float, default=2.5); p.add_argument("--radius", type=int, default=3); p.add_argument("--output", default="results/compare_planners.png"); p.add_argument("--show-heatmap", action="store_true"); args = p.parse_args()
    scenario = make_scenario(args.scenario, args.seed)
    baseline_robot, baseline = run_scenario(scenario, "baseline", args.lambda_recovery, args.radius)
    recover_robot, recover = run_scenario(scenario, "recovernav", args.lambda_recovery, args.radius)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); draw(axes[0], baseline_robot, "A* baseline", baseline); draw(axes[1], recover_robot, "RecoverNav", recover); fig.tight_layout(); Path(args.output).parent.mkdir(parents=True, exist_ok=True); fig.savefig(args.output, dpi=160)
    if os.environ.get("MPLBACKEND", "").lower() != "agg": plt.show()
    print("baseline", baseline.as_dict()); print("recovernav", recover.as_dict())
    if args.show_heatmap:
        heat = recoverability_heatmap(scenario.environment, args.radius); fig2, ax2 = plt.subplots(figsize=(8, 5)); image = ax2.imshow(heat, origin="upper", vmin=0, vmax=1); fig2.colorbar(image, ax=ax2, label="Q")
        for robot, label in ((baseline_robot, "baseline"), (recover_robot, "RecoverNav")):
            if robot.trajectory:
                ys, xs = zip(*robot.trajectory); ax2.plot(xs, ys, label=label)
        ax2.legend(); ax2.set_title("Recoverability heatmap"); heat_path = Path(args.output).with_name("recoverability_heatmap.png"); fig2.tight_layout(); fig2.savefig(heat_path, dpi=160)


if __name__ == "__main__": main()
