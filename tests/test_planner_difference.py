from recovernav.planners.astar import astar
from recovernav.planners.recoverability_astar import recoverability_astar
from recovernav.scenarios import make_scenario


def test_recovernav_can_choose_different_path():
    s = make_scenario("two_routes")
    baseline = astar(s.environment, s.start, s.goal)
    recover = recoverability_astar(
        s.environment,
        s.start,
        s.goal,
        lambda_recovery=2.5,
        radius=3,
    )
    assert baseline.success and recover.success
    assert baseline.path != recover.path
    assert s.environment.path_is_valid(recover.path)
