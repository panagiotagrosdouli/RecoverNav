import math

from recovernav.recoverability import (
    EdgeData,
    EstimatorConfig,
    build_capacity_graph,
    route_recoverability,
    state_recoverability,
)

CFG = EstimatorConfig(c_min=0.20, c_ref=0.30, c_capacity_ref=1.0)


def graph(*edges: tuple[str, str, float]):
    return build_capacity_graph([EdgeData(u, v, clearance) for u, v, clearance in edges], CFG)


def test_single_corridor_without_distinct_anchor_has_zero_recoverability():
    g = graph(("s", "a", 0.50), ("a", "b", 0.50))
    result = state_recoverability(g, "s", anchors=[], config=CFG)
    assert result.escape_capacity == 0.0
    assert result.rho == 0.0


def test_open_branching_space_has_more_escape_capacity_than_single_branch():
    single = graph(("s", "a", 0.50))
    branching = graph(("s", "a", 0.50), ("s", "b", 0.50))

    one = state_recoverability(single, "s", ["a"], CFG)
    two = state_recoverability(branching, "s", ["a", "b"], CFG)

    assert two.escape_capacity > one.escape_capacity


def test_two_exits_behind_shared_bottleneck_do_not_count_as_two_independent_units():
    g = graph(
        ("s", "neck", 0.35),
        ("neck", "exit_a", 0.50),
        ("neck", "exit_b", 0.50),
    )
    result = state_recoverability(g, "s", ["exit_a", "exit_b"], CFG)

    expected_bottleneck = (0.35 - CFG.c_min) / CFG.c_ref
    assert math.isclose(result.escape_capacity, expected_bottleneck, rel_tol=1e-9)


def test_footprint_infeasible_branch_is_removed():
    g = graph(("s", "safe", 0.50), ("s", "too_narrow", 0.19))
    result = state_recoverability(g, "s", ["safe", "too_narrow"], CFG)

    assert "too_narrow" not in g
    assert math.isclose(result.escape_capacity, 1.0)


def test_future_event_cannot_change_pre_event_score_without_changing_observation():
    observed_edges = [("s", "a", 0.50), ("s", "b", 0.50)]
    g_before_future_event_a = graph(*observed_edges)
    g_before_future_event_b = graph(*observed_edges)

    score_a = state_recoverability(g_before_future_event_a, "s", ["a", "b"], CFG)
    score_b = state_recoverability(g_before_future_event_b, "s", ["a", "b"], CFG)

    assert score_a == score_b


def test_route_score_is_weakest_sampled_state():
    g = graph(
        ("p0", "a", 0.50),
        ("p0", "b", 0.50),
        ("p1", "c", 0.35),
    )
    rho = route_recoverability(
        g,
        route=["p0", "p1"],
        anchors_by_state={"p0": ["a", "b"], "p1": ["c"]},
        config=CFG,
    )

    expected = (0.35 - CFG.c_min) / CFG.c_ref
    assert math.isclose(rho, expected, rel_tol=1e-9)
