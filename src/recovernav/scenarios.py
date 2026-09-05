"""Deterministic graph scenarios for Study A commissioning.

These scenarios are synthetic unit/commissioning fixtures. They are not efficacy
evidence and must never be reported as physical-robot results.
"""

from __future__ import annotations

from dataclasses import dataclass

from .recoverability import EdgeData
from .study_a import StudyAScenario


@dataclass(frozen=True)
class GraphScenarioFixture:
    scenario: StudyAScenario
    edges: tuple[EdgeData, ...]
    route_clearances_m: tuple[float, ...]
    expected_structural_order: int


def commissioning_scenarios() -> tuple[GraphScenarioFixture, ...]:
    """Return ordered fixtures spanning low to high structural recoverability."""

    return (
        GraphScenarioFixture(
            scenario=StudyAScenario("corridor_commitment_01", ("s",), {"s": ()}),
            edges=(EdgeData("s", "fwd", 0.50),),
            route_clearances_m=(0.50,),
            expected_structural_order=0,
        ),
        GraphScenarioFixture(
            scenario=StudyAScenario("footprint_constraint_01", ("s",), {"s": ("narrow",)}),
            edges=(EdgeData("s", "narrow", 0.19),),
            route_clearances_m=(0.50,),
            expected_structural_order=0,
        ),
        GraphScenarioFixture(
            scenario=StudyAScenario("shared_bottleneck_01", ("s",), {"s": ("a", "b")}),
            edges=(
                EdgeData("s", "neck", 0.35),
                EdgeData("neck", "a", 0.50),
                EdgeData("neck", "b", 0.50),
            ),
            route_clearances_m=(0.50,),
            expected_structural_order=1,
        ),
        GraphScenarioFixture(
            scenario=StudyAScenario("branching_alternatives_01", ("s",), {"s": ("a", "b")}),
            edges=(EdgeData("s", "a", 0.50), EdgeData("s", "b", 0.50)),
            route_clearances_m=(0.50,),
            expected_structural_order=2,
        ),
        GraphScenarioFixture(
            scenario=StudyAScenario(
                "partial_observation_01", ("s",), {"s": ("observed_branch",)}
            ),
            edges=(EdgeData("s", "observed_branch", 0.50),),
            route_clearances_m=(0.50,),
            expected_structural_order=1,
        ),
        GraphScenarioFixture(
            scenario=StudyAScenario("open_alternatives_01", ("s",), {"s": ("a", "b", "c")}),
            edges=(
                EdgeData("s", "a", 0.50),
                EdgeData("s", "b", 0.50),
                EdgeData("s", "c", 0.50),
            ),
            route_clearances_m=(0.50,),
            expected_structural_order=3,
        ),
    )
