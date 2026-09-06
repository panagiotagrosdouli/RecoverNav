import numpy as np

from recovernav.environment import GridEnvironment
from recovernav.planners.astar import astar


def test_astar_finds_valid_path():
    env = GridEnvironment(np.zeros((7, 7), dtype=np.uint8))
    result = astar(env, (1, 1), (5, 5))
    assert result.success
    assert result.path[0] == (1, 1) and result.path[-1] == (5, 5)
    assert env.path_is_valid(result.path)


def test_astar_fails_when_goal_enclosed():
    grid = np.zeros((7, 7), dtype=np.uint8)
    goal = (3, 3)
    for p in [(2, 3), (4, 3), (3, 2), (3, 4)]:
        grid[p] = 1
    result = astar(GridEnvironment(grid), (1, 1), goal)
    assert not result.success
