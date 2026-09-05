# RecoverNav — Frozen Recoverability Estimator v1

**Status:** methodological freeze candidate for Study A. Do not tune against confirmatory Study B outcomes.

## 1. Purpose

This document defines the first exact mathematical estimator to test. It is intentionally simple, interpretable, robot-observable, and falsifiable.

The estimator is **not** a probability of successful recovery and **not** a formal safety guarantee.

Its purpose is to quantify how much currently observed traversable structure remains available for alternative motion if a local route segment later becomes unusable.

---

## 2. Robot-observable traversability graph

At planning time `t`, construct a footprint-aware graph

`G_t = (V_t, E_t)`

from the currently available occupancy/costmap representation.

A vertex represents a traversable cell or graph node. An edge exists only if the robot footprint can move between its endpoints under the frozen geometric/kinematic feasibility rules.

Unknown space is **not assumed free**. The v1 estimator uses only information available at decision time.

For each edge `e`, define its clearance margin

`m_t(e) = max(0, c_t(e) - c_min)`

where:

- `c_t(e)` is the minimum obstacle clearance along the edge;
- `c_min` is the frozen minimum feasible footprint/safety clearance.

Define a bounded normalized edge capacity

`u_t(e) = min(1, m_t(e) / c_ref)`

where `c_ref > 0` is a fixed normalization constant chosen from robot geometry/commissioning and frozen before Study A validation.

Edges with `c_t(e) < c_min` are infeasible and excluded.

---

## 3. Recovery anchor set

For a candidate route state `v`, define a local horizon subgraph `G_t^H(v)` containing nodes whose shortest-path distance from `v` is at most `H` meters.

Within that subgraph, the **recovery anchor set** `S_t(v)` consists of traversable nodes satisfying both:

1. they lie outside the candidate route's immediate commitment corridor, defined as a frozen radius `r_commit` around the forward route segment; and
2. they connect to a locally distinct free-space branch/component under the frozen graph-extraction rule.

Intuition: an anchor is not merely open space next to the route; it is a reachable state that provides a structurally distinct continuation/retreat option.

The exact graph rule for branch/component extraction must be deterministic and unit-tested. It cannot depend on the future event realization or planner condition.

---

## 4. Local escape capacity

Create a super-sink node `s*` and connect every recovery anchor in `S_t(v)` to `s*` with capacity 1.

Define the local escape capacity as the maximum flow from `v` to `s*`:

`C_t(v) = MaxFlow(G_t^H(v), source=v, sink=s*, capacities=u_t)`

This quantity combines two properties without an arbitrary multi-feature weighted sum:

- **multiplicity/diversity of alternative connections**;
- **bottleneck clearance capacity** of those connections.

If no recovery anchor exists or no feasible path reaches one, `C_t(v) = 0`.

---

## 5. Normalized state recoverability score

Define

`rho_t(v) = min(1, C_t(v) / C_ref)`

where `C_ref > 0` is a fixed saturation constant frozen before validation.

Therefore

`rho_t(v) in [0, 1]`.

Interpretation:

- `rho_t(v) = 0`: no observed structurally distinct recovery capacity under the v1 definition;
- larger `rho_t(v)`: more/better observed escape capacity;
- `rho_t(v) = 1`: capacity reaches the predefined saturation reference.

Again, `rho_t(v)=0.8` does **not** mean an 80% probability of recovery.

---

## 6. Route-level recoverability

For a candidate path

`P = (v_1, ..., v_N)`

sampled at fixed spatial spacing `delta_s`, define the route recoverability margin conservatively as

`rho_t(P) = min_i rho_t(v_i)`.

The corresponding penalty is

`R_t(P) = 1 - rho_t(P)`.

This weakest-point definition is deliberately chosen instead of an average because a single commitment bottleneck can dominate post-invalidation recoverability.

---

## 7. Planner objective

The treatment planner uses

`J_R(P) = L(P) + lambda_R * R_t(P)`

where:

- `L(P)` is the exact same nominal route/path objective used by the baseline;
- `R_t(P)` is the frozen v1 recoverability penalty;
- `lambda_R >= 0` is the only treatment trade-off parameter.

The baseline is exactly

`J_0(P) = L(P)`.

No future event information may enter `G_t`, `S_t`, `C_t`, `rho_t`, or route selection.

---

## 8. Parameters that must be frozen

Before Study A validation, freeze:

- `c_min` — minimum feasible clearance;
- `c_ref` — clearance-capacity normalization;
- `H` — local graph horizon;
- `r_commit` — commitment-corridor radius;
- `C_ref` — capacity saturation reference;
- `delta_s` — route sampling spacing;
- graph resolution and connectivity;
- branch/component extraction rule;
- footprint model and inflation policy.

`lambda_R` is not part of estimator validity. Its selection belongs to planner-development/commissioning and must be frozen before confirmatory Study B.

---

## 9. Study A — construct validation

### Question

Does pre-event `rho_t(P)` or the relevant pre-event minimum state score predict later executed recovery outcome after a controlled route invalidation?

### Data

Collect trials spanning different route geometries and recovery outcomes. The estimator must be computed before the event and without future-event leakage.

### Target label

Use a frozen binary mechanistic label such as

`Z = 1` if the robot can autonomously execute the frozen recovery policy and reach the defined recovery/goal-valid state after invalidation;

`Z = 0` otherwise.

### Required analyses

At minimum report:

- score distributions for `Z=1` and `Z=0`;
- discrimination (e.g. ROC-AUC with uncertainty) as descriptive construct evidence;
- calibration only if a probabilistic mapping is explicitly fitted;
- monotonic association between lower `rho` and worse recovery outcome;
- failure examples with high `rho` but failed recovery and low `rho` but successful recovery;
- runtime cost per evaluated route/state.

Do not convert the raw score into a probability unless a separate calibrated model is trained and evaluated on held-out data.

---

## 10. Adversarial semantic tests before robot deployment

The estimator implementation must pass toy scenarios designed to expose semantic errors:

1. **single narrow corridor:** score should be low when no distinct recovery branch exists;
2. **wide open room with multiple exits:** score should be higher than the single-corridor case;
3. **two apparent exits sharing one narrow bottleneck:** score must reflect the shared bottleneck rather than counting them as fully independent;
4. **geometrically open but footprint-infeasible branch:** must not increase score;
5. **unknown-space shortcut:** must not be treated as available free space;
6. **future blocked segment:** score must be identical before the event whether that future event will or will not occur;
7. **baseline/treatment information parity:** both conditions must receive the same map and sensor information.

---

## 11. Reasons for this v1 choice

The estimator deliberately avoids:

- learned black-box features;
- an arbitrary sum of many hand-picked heuristics;
- claiming full viability or reachability certification;
- assuming knowledge of the future event;
- requiring a predefined contingency destination;
- calling a structural score a probability.

It is computationally and scientifically testable. If it fails Study A, the result is informative and the estimator should be revised before any efficacy claim.

---

## 12. Kill criteria for v1

Do not proceed to confirmatory Study B with this estimator if one or more of the following persists after commissioning:

- the score has no meaningful association with executed recovery outcome;
- graph artifacts dominate the score;
- the score changes materially under irrelevant map discretization choices;
- runtime is incompatible with the intended online planning rate;
- the branch/anchor definition cannot be made deterministic and reproducible;
- the score simply proxies ordinary path clearance without capturing alternative structure;
- estimator tuning requires looking at confirmatory planner outcomes.

---

## 13. Claim allowed if Study A succeeds

A defensible claim would be:

> Under the tested indoor geometry, sensing, robot, and event family, the frozen bottleneck-aware escape-capacity score contained predictive information about subsequent post-invalidation recovery outcomes.

It would **not** yet justify the claim that RecoverNav reduces failures. That requires Study B.
