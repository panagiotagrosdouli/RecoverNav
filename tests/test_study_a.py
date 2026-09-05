import math

import pytest

from recovernav.recoverability import EdgeData, EstimatorConfig, build_capacity_graph
from recovernav.study_a import (
    StudyAScenario,
    attach_executed_outcome,
    empirical_auc,
    score_pre_event_scenario,
)

CFG = EstimatorConfig(c_min=0.20, c_ref=0.30, c_capacity_ref=1.0)


def test_pre_event_score_api_has_no_future_event_or_outcome_argument():
    g = build_capacity_graph(
        [EdgeData("s", "a", 0.50), EdgeData("s", "b", 0.50)], CFG
    )
    scenario = StudyAScenario(
        scenario_id="branching",
        route=("s",),
        anchors_by_state={"s": ("a", "b")},
    )

    rho = score_pre_event_scenario(g, scenario, CFG)
    success = attach_executed_outcome(
        trial_id="success", scenario=scenario, rho_pre_event=rho, recovery_success=True
    )
    failure = attach_executed_outcome(
        trial_id="failure", scenario=scenario, rho_pre_event=rho, recovery_success=False
    )

    assert success.rho_pre_event == failure.rho_pre_event


def test_auc_is_one_for_perfect_ordering():
    scenario = StudyAScenario("s", ("v",), {"v": ()})
    observations = [
        attach_executed_outcome(
            trial_id="f1", scenario=scenario, rho_pre_event=0.1, recovery_success=False
        ),
        attach_executed_outcome(
            trial_id="f2", scenario=scenario, rho_pre_event=0.2, recovery_success=False
        ),
        attach_executed_outcome(
            trial_id="s1", scenario=scenario, rho_pre_event=0.8, recovery_success=True
        ),
        attach_executed_outcome(
            trial_id="s2", scenario=scenario, rho_pre_event=0.9, recovery_success=True
        ),
    ]
    assert empirical_auc(observations) == 1.0


def test_auc_counts_ties_as_half():
    scenario = StudyAScenario("s", ("v",), {"v": ()})
    observations = [
        attach_executed_outcome(
            trial_id="f", scenario=scenario, rho_pre_event=0.5, recovery_success=False
        ),
        attach_executed_outcome(
            trial_id="s", scenario=scenario, rho_pre_event=0.5, recovery_success=True
        ),
    ]
    assert math.isclose(empirical_auc(observations), 0.5)


def test_auc_rejects_single_class_data():
    scenario = StudyAScenario("s", ("v",), {"v": ()})
    observations = [
        attach_executed_outcome(
            trial_id="s", scenario=scenario, rho_pre_event=0.5, recovery_success=True
        )
    ]
    with pytest.raises(ValueError):
        empirical_auc(observations)
