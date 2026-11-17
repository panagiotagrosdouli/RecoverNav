from pathlib import Path

import pytest

from recovernav.movingai import load_movingai_map, load_movingai_scenarios


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    grid = tmp_path / "example.map"
    grid.write_text("type octile\nheight 4\nwidth 5\nmap\n.....\n.@@..\n.....\n.....\n", encoding="utf-8")
    scenarios = tmp_path / "example.scen"
    scenarios.write_text("version 1\n0 example.map 5 4 0 0 4 3 6.0\n", encoding="utf-8")
    return grid, scenarios


def test_load_published_map_and_problem(tmp_path: Path) -> None:
    grid, problems = _fixture(tmp_path)
    env = load_movingai_map(grid)
    assert env.shape == (4, 5)
    assert not env.is_free((1, 1))
    jobs = load_movingai_scenarios(grid, problems)
    assert len(jobs) == 1
    assert jobs[0].start == (0, 0)
    assert jobs[0].goal == (3, 4)
    assert jobs[0].dynamic_obstacle is None


def test_invalid_map_size_fails_closed(tmp_path: Path) -> None:
    grid, _ = _fixture(tmp_path)
    grid.write_text(grid.read_text().replace("height 4", "height 5"), encoding="utf-8")
    with pytest.raises(ValueError, match="dimensions"):
        load_movingai_map(grid)


def test_weighted_swamp_terrain_does_not_look_like_regular_floor(tmp_path: Path) -> None:
    grid, _ = _fixture(tmp_path)
    grid.write_text(grid.read_text().replace(".@@..", ".S@.."), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported MovingAI terrain"):
        load_movingai_map(grid)


def test_blocked_benchmark_endpoint_rejected(tmp_path: Path) -> None:
    grid, scen = _fixture(tmp_path)
    scen.write_text("version 1\n0 example.map 5 4 1 1 4 3 6\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blocked"):
        load_movingai_scenarios(grid, scen)
