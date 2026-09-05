"""Frozen RecoverNav v1 recoverability estimator.

This module implements the mathematical object in
``docs/RECOVERABILITY_ESTIMATOR_V1.md``. It does not infer future events and
must only consume robot-observable graph information available at decision time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping, Sequence

import networkx as nx

Node = Hashable


@dataclass(frozen=True)
class EstimatorConfig:
    """Parameters that define the v1 estimator semantics."""

    c_min: float
    c_ref: float
    c_capacity_ref: float

    def __post_init__(self) -> None:
        if self.c_min < 0:
            raise ValueError("c_min must be non-negative")
        if self.c_ref <= 0:
            raise ValueError("c_ref must be positive")
        if self.c_capacity_ref <= 0:
            raise ValueError("c_capacity_ref must be positive")


@dataclass(frozen=True)
class EdgeData:
    """Observed geometric information for one traversability edge."""

    u: Node
    v: Node
    clearance_m: float


@dataclass(frozen=True)
class RecoverabilityResult:
    """Raw capacity and normalized structural score for one state."""

    escape_capacity: float
    rho: float


def normalized_capacity(clearance_m: float, config: EstimatorConfig) -> float:
    """Compute u_t(e) from observed edge clearance.

    Infeasible edges have zero capacity. Feasibility is enforced again when the
    graph is built so such edges cannot accidentally provide connectivity.
    """

    margin = max(0.0, clearance_m - config.c_min)
    return min(1.0, margin / config.c_ref)


def build_capacity_graph(
    edges: Iterable[EdgeData], config: EstimatorConfig
) -> nx.Graph:
    """Build the footprint-aware capacity graph from observed feasible edges."""

    graph = nx.Graph()
    for edge in edges:
        if edge.clearance_m < config.c_min:
            continue
        graph.add_edge(
            edge.u,
            edge.v,
            capacity=normalized_capacity(edge.clearance_m, config),
            clearance_m=edge.clearance_m,
        )
    return graph


def local_escape_capacity(
    graph: nx.Graph,
    source: Node,
    anchors: Iterable[Node],
) -> float:
    """Return max-flow capacity from ``source`` to distinct recovery anchors.

    The caller is responsible for constructing the frozen local horizon and
    recovery-anchor set. Missing/unreachable anchors contribute no capacity.
    """

    if source not in graph:
        return 0.0

    valid_anchors = {anchor for anchor in anchors if anchor in graph and anchor != source}
    if not valid_anchors:
        return 0.0

    flow_graph = nx.DiGraph()
    for u, v, data in graph.edges(data=True):
        capacity = float(data.get("capacity", 0.0))
        if capacity <= 0:
            continue
        # An undirected traversability edge permits motion in both directions.
        flow_graph.add_edge(u, v, capacity=capacity)
        flow_graph.add_edge(v, u, capacity=capacity)

    sink = object()
    for anchor in valid_anchors:
        flow_graph.add_edge(anchor, sink, capacity=1.0)

    if source not in flow_graph:
        return 0.0

    value, _ = nx.maximum_flow(flow_graph, source, sink, capacity="capacity")
    return float(value)


def state_recoverability(
    graph: nx.Graph,
    source: Node,
    anchors: Iterable[Node],
    config: EstimatorConfig,
) -> RecoverabilityResult:
    """Compute C_t(v) and rho_t(v) for one route state."""

    capacity = local_escape_capacity(graph, source, anchors)
    rho = min(1.0, capacity / config.c_capacity_ref)
    return RecoverabilityResult(escape_capacity=capacity, rho=rho)


def route_recoverability(
    graph: nx.Graph,
    route: Sequence[Node],
    anchors_by_state: Mapping[Node, Iterable[Node]],
    config: EstimatorConfig,
) -> float:
    """Compute rho_t(P) as the weakest sampled state on the candidate route."""

    if not route:
        raise ValueError("route must contain at least one sampled state")

    scores = [
        state_recoverability(graph, node, anchors_by_state.get(node, ()), config).rho
        for node in route
    ]
    return min(scores)
