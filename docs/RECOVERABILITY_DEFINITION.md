# RecoverNav — Recoverability Construct Specification

**Status:** working scientific specification; must be frozen before confirmatory experiments.

## 1. Why this document exists

`recoverability` must not be a label attached to an arbitrary path penalty. This document separates the real-world construct we care about from the estimator used by the planner.

## 2. Target construct

At decision time `t`, the robot has an information state

```text
z_t = (x_hat_t, M_t, Sigma_t, q_t, robot_model, motion_limits)
```

where:

- `x_hat_t`: estimated robot pose/state;
- `M_t`: information currently available in map/costmap/perception representation;
- `Sigma_t`: relevant localization/perception uncertainty summary, if used;
- `q_t`: navigation mode / route context needed by the frozen policy;
- `robot_model`: footprint and kinematic model;
- `motion_limits`: frozen velocity, acceleration and safety constraints.

No variable may contain privileged knowledge of a future obstruction.

## 3. Event family

Let `E` be a prespecified family of local environmental changes that can invalidate the currently preferred route.

For the first study, keep `E` narrow and physically reproducible. Candidate events:

- blockage of a corridor segment after a geometry-based commitment trigger;
- closure of a doorway/passage after the robot crosses a fixed trigger region.

The final event mechanism and distribution are frozen before estimator validation and confirmatory planner evaluation.

## 4. Recovery target set

Define `S_rec` as the set of states satisfying all of the following under the frozen robot/navigation policy:

1. collision and safety constraints are satisfied;
2. localization remains valid under a prespecified criterion;
3. the robot is not dependent on human intervention;
4. a valid goal-directed navigation continuation exists under the robot's currently available information and frozen planning/recovery policy.

This definition must be converted into executable checks. If condition 4 cannot be measured reliably, a narrower operational target set must be adopted.

## 5. Executed recovery feasibility label

For an information state `z_t` and event realization `e in E`, define

```text
F(z_t, e) = 1
```

if, after event `e`, autonomous execution reaches `S_rec` within recovery horizon `H_rec` without violating frozen safety/failure constraints.

Otherwise:

```text
F(z_t, e) = 0
```

`H_rec` must be selected during commissioning for scientific/operational reasons and frozen before held-out validation.

## 6. What RecoverNav estimates

The first implementation should output a **recoverability proxy or margin**:

```text
r_hat(z_t) = f(robot-observable geometry, topology, robot constraints, uncertainty if justified)
```

It is not initially a probability.

Potential components are hypotheses, not requirements:

- number/quality of reachable alternative branches;
- retreat path feasibility;
- bottleneck/commitment structure;
- minimum clearance relative to robot footprint;
- turning feasibility;
- reachable safe-region size;
- distance/cost to a recoverable state;
- sensitivity of alternatives to local blockage;
- sensing visibility relevant to detecting an invalidation before commitment.

Each included component needs an ablation or scientific justification. Avoid a large weighted score with many unidentifiable parameters.

## 7. Preferred first estimator design

Start with the smallest interpretable estimator capable of failing clearly.

A preferred structure is to compute, on the currently known traversability graph/free-space representation:

1. candidate route states at a fixed spatial sampling interval;
2. alternative connected exits/branches reachable without crossing the immediately preceding commitment bottleneck;
3. footprint-aware clearance/turn feasibility for those alternatives;
4. cost to return to a predefined recovery region;
5. a path-level summary using a conservative statistic such as the minimum recovery margin along a candidate route.

The exact formula must be chosen only after literature comparison and toy counterexample testing.

## 8. Required properties

### P1 — information validity

`r_hat(z_t)` uses only information available at decision time.

### P2 — deterministic semantics

For fixed input state/configuration, the estimator returns the same value unless stochastic behavior is explicitly modeled and seeded.

### P3 — monotonic sanity checks

Where all else is equal, deliberately removing a feasible alternative should not improve the estimated recovery margin.

### P4 — robot awareness

Changing footprint/turning constraints in a way that makes an escape physically infeasible must not leave the estimator claiming identical recoverability if those constraints are part of the construct.

### P5 — held-out behavioral relevance

Estimator values must be associated with executed `F(z_t,e)` on held-out recovery probes according to a prespecified validation metric.

### P6 — no semantic inflation

A heuristic/margin remains described as such. Only a separately calibrated and validated probabilistic model may be called a probability of recovery.

## 9. Study A validation protocol

Before testing planner efficacy:

1. construct controlled recovery-probe states spanning high/low expected feasibility;
2. sample event realizations from the frozen event family;
3. execute recovery under the same frozen robot policy;
4. record `F` and all estimator inputs without post-event leakage;
5. separate development/tuning from held-out validation scenarios;
6. evaluate discrimination/association and calibration only if probabilistic output is attempted;
7. inspect false-high cases (`r_hat` predicts good recovery but execution fails) as the most safety-relevant estimator error;
8. retain all counterexamples.

The pass criterion must be chosen before examining held-out results.

## 10. Planner integration after validation

Only after Study A passes its predefined gate should the estimator enter route choice.

Baseline:

```text
J0(P) = L(P)
```

Treatment candidate:

```text
JR(P) = L(P) + lambda_R * C_R(P)
```

where `C_R(P)` is derived monotonically from the validated recoverability margin.

An alternative hard-constraint formulation may be scientifically preferable if the literature review and estimator semantics justify it:

```text
minimize L(P)
subject to r_hat(z along P) >= tau_R
```

Do not choose penalty vs constraint based on which produces better confirmatory results. Select and freeze it during development.

## 11. Falsification examples

The construct/estimator is challenged if:

- a narrow corridor with no viable retreat receives a high score merely because geometric clearance is locally large;
- a route with an alternative branch receives a high score even though the robot cannot turn into it;
- the estimator relies on the future blocked passage identity;
- high scores do not predict held-out executed recovery;
- the score is only a disguised path-length or clearance metric;
- performance disappears when tested outside the exact geometry used to tune weights.

## 12. Claim boundary

Until Study A is completed, RecoverNav may say:

> "We define and investigate a candidate recoverability proxy."

It may not say:

> "RecoverNav predicts recovery probability," "guarantees recoverability," or "reduces recovery failures."

Those statements require separate evidence.
