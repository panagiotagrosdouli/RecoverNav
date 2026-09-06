from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/ros2")
    args = parser.parse_args()
    root = Path(args.results)
    files = sorted(p for p in root.glob("*.json") if p.name != "paired_summary.json")
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    if not rows:
        raise SystemExit(f"no ROS result JSON files found in {root}")

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row["planner"])].append(row)

    print("planner,runs,success_rate,mean_executed_distance,mean_replans,mean_time_to_goal")
    for planner, values in sorted(grouped.items()):
        n = len(values)
        success = sum(bool(v.get("success")) for v in values) / n
        dist = sum(float(v.get("executed_trajectory_length") or 0.0) for v in values) / n
        replans = sum(float(v.get("number_of_replans") or 0.0) for v in values) / n
        time_to_goal = sum(float(v.get("time_to_goal") or 0.0) for v in values) / n
        print(f"{planner},{n},{success:.3f},{dist:.3f},{replans:.3f},{time_to_goal:.3f}")

    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    for row in rows:
        trajectory = row.get("trajectory") or []
        if not trajectory:
            continue
        xs = [p[1] for p in trajectory]
        ys = [p[2] for p in trajectory]
        ax.plot(xs, ys, alpha=0.5, label=str(row["planner"]))
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    if unique:
        ax.legend(unique.values(), unique.keys())
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Executed ROS 2 / Gazebo trajectories")
    ax.axis("equal")
    fig.tight_layout()
    out = root / "trajectory_overlay.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(7, 4))
    ax = fig.add_subplot(111)
    names = sorted(grouped)
    ax.bar(names, [sum(v.get("number_of_replans", 0) for v in grouped[n]) / len(grouped[n]) for n in names])
    ax.set_ylabel("mean replans")
    ax.set_title("Replanning by planner")
    fig.tight_layout()
    fig.savefig(root / "replans.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
