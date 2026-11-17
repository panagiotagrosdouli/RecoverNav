"""Import published Moving AI Lab 2D grid-pathfinding benchmark instances.

The source format supports octile motion. RecoverNav uses four-connected motion,
so published optimal lengths are *not* directly comparable to our results.
This adapter rejects weighted/swamp/water terrain instead of inventing costs.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from recovernav.environment import GridEnvironment
from recovernav.scenarios import Scenario


def load_movingai_map(path: str | Path) -> GridEnvironment:
    """Load a unit-cost MovingAI .map with strict geometry validation."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if len(lines) < 5 or lines[0].strip() != "type octile":
        raise ValueError("Expected a MovingAI 'type octile' map")
    try:
        height = int(lines[1].removeprefix("height "))
        width = int(lines[2].removeprefix("width "))
    except ValueError as exc:
        raise ValueError("Invalid MovingAI map dimensions") from exc
    if not lines[1].startswith("height ") or not lines[2].startswith("width "):
        raise ValueError("Invalid MovingAI map dimension header")
    if height < 1 or width < 1 or lines[3].strip() != "map":
        raise ValueError("Invalid MovingAI map header")
    if len(lines) != 4 + height or any(len(row) != width for row in lines[4:]):
        raise ValueError("MovingAI grid does not match declared dimensions")
    allowed = {".", "G", "@", "O", "T"}
    if any(char not in allowed for row in lines[4:] for char in row):
        raise ValueError("Unsupported MovingAI terrain: S/W or unknown tile requires a separate cost model")
    grid = np.asarray([[0 if cell in (".", "G") else 1 for cell in row] for row in lines[4:]], dtype=np.uint8)
    return GridEnvironment(grid)


def load_movingai_scenarios(
    map_path: str | Path, scen_path: str | Path, *, limit: int = 10
) -> list[Scenario]:
    """Load published static pathfinding tasks; do not synthesize moving obstacles."""
    if limit < 1:
        raise ValueError("limit must be at least one")
    map_path = Path(map_path)
    env = load_movingai_map(map_path)
    lines = Path(scen_path).read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() not in ("version 1", "version 1.0"):
        raise ValueError("Unsupported MovingAI scenario format")
    scenarios: list[Scenario] = []
    height, width = env.shape
    for index, line in enumerate(lines[1:]):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 9:
            raise ValueError(f"Invalid MovingAI scenario row {index + 2}: expected 9 columns")
        _, source_map, declared_width, declared_height, sx, sy, gx, gy, _ = fields
        if Path(source_map).name != map_path.name:
            raise ValueError(f"Scenario row {index + 2} belongs to another map: {source_map}")
        if (int(declared_height), int(declared_width)) != (height, width):
            raise ValueError(f"Scenario row {index + 2} map dimensions mismatch")
        start = (int(sy), int(sx))
        goal = (int(gy), int(gx))
        if not env.is_free(start) or not env.is_free(goal):
            raise ValueError(f"Scenario row {index + 2} contains a blocked or invalid endpoint")
        scenarios.append(
            Scenario(
                name=f"movingai/{map_path.stem}/{index}",
                environment=env,
                start=start,
                goal=goal,
                event_step=None,
                dynamic_obstacle=None,
                seed=index,
            )
        )
        if len(scenarios) >= limit:
            break
    if not scenarios:
        raise ValueError("No MovingAI benchmark instances loaded")
    return scenarios
