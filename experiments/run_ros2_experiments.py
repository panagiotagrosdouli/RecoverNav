from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path


def run_trial(scenario: str, planner: str, seed: int, timeout: float, startup: float) -> dict:
    env = os.environ.copy()
    env.setdefault("TURTLEBOT3_MODEL", "burger")
    results = Path("results/ros2")
    results.mkdir(parents=True, exist_ok=True)
    outfile = results / f"{scenario}_{planner}_seed{seed}.json"
    if outfile.exists():
        outfile.unlink()
    launch = subprocess.Popen(
        ["ros2", "launch", "recovernav_bringup", "simulation.launch.py",
         f"scenario:={scenario}", f"planner:={planner}", "rviz:=false", "gz_gui:=false"],
        env=env, start_new_session=True,
    )
    obstacle = None
    try:
        time.sleep(startup)
        obstacle = subprocess.Popen(
            ["ros2", "run", "recovernav_scenarios", "dynamic_obstacle", "--ros-args",
             "-p", "use_sim_time:=true", "-p", f"scenario:={scenario}", "-p", "trigger_seconds:=30.0"],
            env=env, start_new_session=True,
        )
        trial = subprocess.run(
            ["ros2", "run", "recovernav_experiments", "trial_runner", "--ros-args",
             "-p", "use_sim_time:=true", "-p", f"scenario:={scenario}", "-p", f"planner:={planner}",
             "-p", f"seed:={seed}", "-p", f"timeout_seconds:={timeout}"],
            env=env, timeout=timeout + 30.0, check=False,
        )
        if trial.returncode != 0 and not outfile.exists():
            return {"scenario": scenario, "planner": planner, "seed": seed, "success": False,
                    "failure_reason": f"trial_runner_exit_{trial.returncode}"}
        if not outfile.exists():
            return {"scenario": scenario, "planner": planner, "seed": seed, "success": False,
                    "failure_reason": "missing_result_file"}
        return json.loads(outfile.read_text(encoding="utf-8"))
    finally:
        for process in [obstacle, launch]:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        time.sleep(2.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="two_routes")
    parser.add_argument("--planners", nargs="+", default=["baseline", "recovernav"])
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--startup", type=float, default=15.0)
    args = parser.parse_args()
    rows = []
    for seed in range(args.seeds):
        for planner in args.planners:
            print(f"=== {args.scenario} seed={seed} planner={planner} ===", flush=True)
            rows.append(run_trial(args.scenario, planner, seed, args.timeout, args.startup))
    out = Path("results/ros2/paired_summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for row in rows:
        print(row["scenario"], row["seed"], row["planner"], row.get("success"), row.get("failure_reason", ""))


if __name__ == "__main__":
    main()
