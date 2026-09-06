# RecoverNav

RecoverNav is a lightweight navigation framework for experimenting with recovery-aware path planning in dynamic 2D environments.

A conventional planner usually minimizes path cost. RecoverNav can additionally penalize states with poor local escape structure, so a route may trade a little distance for more recovery options when the environment changes.

## What it does

- deterministic 2D grid environments with rooms, corridors, bottlenecks and alternative routes;
- step-by-step robot execution;
- standard A* baseline;
- recoverability-aware A*;
- dynamic obstacle insertion and route invalidation;
- replanning from the robot's current position;
- animated and side-by-side visual demos;
- recoverability heatmaps;
- paired batch experiments and CSV metrics;
- automated tests.

The recoverability value `Q` is a structural score in `[0, 1]`, not a probability of successful recovery. The default score combines the number of reachable sides of a local window with reachable local free-space coverage. Dead ends and single-exit regions tend to receive lower values; open intersections and open areas tend to receive higher values.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development:

```bash
pip install -e '.[dev]'
pytest
```

## Quick start

Animated navigation:

```bash
python examples/demo_navigation.py
```

Useful keys: `SPACE` pause/resume, `N` single step, `O` insert the scenario obstacle, `P` replan, `1` baseline A*, `2` RecoverNav, `R` reset.

Compare both planners on exactly the same scenario:

```bash
python examples/compare_planners.py --scenario two_routes --show-heatmap
```

Run paired experiments:

```bash
python experiments/run_experiments.py --seeds 20
python experiments/analyze_results.py
```

The experiment runner writes `results/runs.csv`; the analysis script writes `results/summary.csv` and plots.

## Planner objective

Baseline A* uses unit step cost. RecoverNav adds a structural recovery penalty:

```text
step_cost(x) = 1 + lambda_recovery * (1 - Q(x))
```

`Q(x)` is computed from local free-space connectivity. It is intentionally interpretable and can be replaced by alternative structural metrics later.

## Built-in scenarios

`open_room`, `corridor`, `two_routes`, `bottleneck`, `dead_end`, and `multi_corridor`.

Dynamic events are deterministic for a given scenario/seed. Baseline and RecoverNav always receive the same map, start, goal, event and seed in paired experiments.

## Repository structure

```text
src/recovernav/          environment, robot, execution and planners
examples/                visual and interactive demos
experiments/             batch runner and result analysis
configs/                 algorithm and experiment configuration
tests/                   navigation and research-engineering tests
results/                 generated outputs
```

## Current limitations

RecoverNav currently uses a discrete grid robot, known maps, deterministic obstacle events and a hand-designed local structural recoverability score. It does not model realistic robot dynamics, perception uncertainty or physical-robot control, and it makes no safety or superiority claim.
