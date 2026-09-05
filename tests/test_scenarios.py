from recovernav.recoverability import EstimatorConfig, build_capacity_graph
from recovernav.scenarios import commissioning_scenarios
from recovernav.study_a import score_pre_event_scenario
from recovernav.study_a_analysis import clearance_only_score

CFG = EstimatorConfig(c_min=0.20, c_ref=0.30, c_capacity_ref=3.0)


def test_structural_scenarios_follow_expected_order_without_clearance_advantage():
    fixtures = commissioning_scenarios()
    scored = []
    clearance_scores = []

    for fixture in fixtures:
        graph = build_capacity_graph(fixture.edges, CFG)
        rho = score_pre_event_scenario(graph, fixture.scenario, CFG)
        scored.append((fixture.expected_structural_order, rho, fixture.scenario.scenario_id))
        clearance_scores.append(
            clearance_only_score(fixture.route_clearances_m, CFG.c_min, CFG.c_ref)
        )

    # All route-level clearance controls are intentionally identical.
    assert len(set(clearance_scores)) == 1

    by_order: dict[int, list[float]] = {}
    for order, rho, _ in scored:
        by_order.setdefault(order, []).append(rho)

    assert max(by_order[0]) < min(by_order[1])
    assert max(by_order[1]) < min(by_order[2])
    assert max(by_order[2]) < min(by_order[3])


def test_partial_observation_does_not_credit_unobserved_alternative():
    fixture = next(
        f for f in commissioning_scenarios() if f.scenario.scenario_id == "partial_observation_01"
    )
    graph = build_capacity_graph(fixture.edges, CFG)
    rho = score_pre_event_scenario(graph, fixture.scenario, CFG)

    # Exactly one observed feasible branch contributes capacity.
    assert rho == 1.0 / 3.0
