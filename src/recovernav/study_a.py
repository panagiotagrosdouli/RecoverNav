"""Study A construct-validation primitives.

Study A asks whether a pre-event structural score contains information about an
executed post-invalidation recovery outcome. This module keeps scenario data,
estimator output, and outcome labels separate so future-event information cannot
leak into score computation.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass

import networkx as nx

from .recoverability import EstimatorConfig, route_recoverability

Node = Hashable


@dataclass(frozen=True)
class StudyAScenario:
    scenario_id: str
    route: tuple[Node, ...]
    anchors_by_state: Mapping[Node, tuple[Node, ...]]


@dataclass(frozen=True)
class StudyAObservation:
    trial_id: str
    scenario_id: str
    rho_pre_event: float
    recovery_success: bool
    estimator_runtime_ms: float | None = None

    def as_record(self) -> dict[str, object]:
        return asdict(self)


def score_pre_event_scenario(
    graph: nx.Graph,
    scenario: StudyAScenario,
    config: EstimatorConfig,
) -> float:
    """Compute the frozen pre-event route score without outcome/event inputs."""

    return route_recoverability(
        graph=graph,
        route=scenario.route,
        anchors_by_state=scenario.anchors_by_state,
        config=config,
    )


def attach_executed_outcome(
    *,
    trial_id: str,
    scenario: StudyAScenario,
    rho_pre_event: float,
    recovery_success: bool,
    estimator_runtime_ms: float | None = None,
) -> StudyAObservation:
    """Join a previously computed score to a later executed recovery label."""

    if not 0.0 <= rho_pre_event <= 1.0:
        raise ValueError("rho_pre_event must be in [0, 1]")
    if estimator_runtime_ms is not None and estimator_runtime_ms < 0:
        raise ValueError("estimator_runtime_ms must be non-negative")
    return StudyAObservation(
        trial_id=trial_id,
        scenario_id=scenario.scenario_id,
        rho_pre_event=rho_pre_event,
        recovery_success=recovery_success,
        estimator_runtime_ms=estimator_runtime_ms,
    )


def empirical_auc(observations: Sequence[StudyAObservation]) -> float:
    """Compute ROC-AUC as the probability a success has a higher score than a failure.

    Ties contribute 0.5. This dependency-light implementation is intended for
    deterministic commissioning checks; publication analysis will additionally
    report uncertainty intervals from the frozen analysis pipeline.
    """

    successes = [o.rho_pre_event for o in observations if o.recovery_success]
    failures = [o.rho_pre_event for o in observations if not o.recovery_success]
    if not successes or not failures:
        raise ValueError("AUC requires at least one success and one failure")

    wins = 0.0
    comparisons = 0
    for success in successes:
        for failure in failures:
            comparisons += 1
            if success > failure:
                wins += 1.0
            elif success == failure:
                wins += 0.5
    return wins / comparisons


def records(observations: Iterable[StudyAObservation]) -> list[dict[str, object]]:
    """Return machine-readable immutable-style records for downstream persistence."""

    return [observation.as_record() for observation in observations]
