from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import yaml

from recovernav.execution import run_scenario
from recovernav.movingai import load_movingai_scenarios
from recovernav.scenarios import make_scenario


def main() -> None:
    parser = argparse.ArgumentParser(description="Run paired RecoverNav planning benchmarks.")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    parser.add_argument("--output", default=str(ROOT / "results" / "runs.csv"))
    parser.add_argument("--movingai-map", type=Path, help="Official MovingAI .map path")
    parser.add_argument("--movingai-scen", type=Path, help="Matching MovingAI .scen tasks")
    parser.add_argument("--max-problems", type=int, default=5)
    args = parser.parse_args()

    if (args.movingai_map is None) != (args.movingai_scen is None):
        parser.error("--movingai-map and --movingai-scen must be provided together")
    if args.seeds < 1 or args.max_problems < 1:
        parser.error("--seeds and --max-problems must be positive")

    with open(args.config, encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)

    lam = float(cfg["planner"]["lambda_recovery"])
    radius = int(cfg["planner"]["recovery_radius"])
    if args.movingai_map is not None:
        # Published pathfinding instances: static occupancy, no fabricated obstacle events.
        # MovingAI assumes eight-connected octile paths, while RecoverNav is four-connected.
        # Therefore never compare these path lengths with MovingAI's published optima.
        scenarios = load_movingai_scenarios(
            args.movingai_map, args.movingai_scen, limit=args.max_problems
        )
    else:
        scenarios = [
            make_scenario(name, seed)
            for seed in range(args.seeds)
            for name in cfg["experiments"]["scenarios"]
        ]

    rows: list[dict[str, object]] = []
    for scenario in scenarios:
        for planner in ("baseline", "recovernav"):
            _, metrics = run_scenario(scenario, planner, lam, radius)
            rows.append(metrics.as_dict())

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"wrote {len(rows)} paired runs to {output}")


if __name__ == "__main__":
    main()
