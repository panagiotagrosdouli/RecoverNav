# RecoverNav

**Recoverability-aware navigation for physical mobile robots in dynamic indoor environments.**

RecoverNav is a research-first robotics project built around one falsifiable question:

> **Does explicitly preserving recovery options during planning reduce post-invalidation navigation failures on a physical mobile robot compared with conventional navigation?**

The repository is intentionally organized around the scientific method rather than around feature accumulation:

1. research question and hypotheses;
2. operational definitions;
3. minimal navigation methods;
4. frozen experimental protocol;
5. physical-robot trials;
6. raw data and provenance;
7. statistical analysis;
8. conclusions constrained by evidence.

## Primary comparison

RecoverNav begins with one controlled comparison:

- **Baseline (J0):** conventional shortest/cost-based navigation without an explicit recoverability objective.
- **RecoverNav (JR):** navigation with an additional recoverability-aware penalty designed to preserve feasible recovery options before route invalidation.

A conceptual path objective is

```text
J(P) = L(P) + lambda_R * R(P)
```

where `L(P)` is nominal path cost and `R(P)` is an operationally defined recoverability/irreversibility cost. The exact definition of `R(P)` must be validated against executed recovery outcomes before it is treated as an efficacy measure.

## Primary outcome

The primary endpoint is binary:

```text
post-invalidation recovery failure = 1
successful recovery and task completion = 0
```

Secondary outcomes include recovery time, total task time, replanning latency, path length, minimum clearance, number of replans, and human interventions.

## Physical-robot requirement

The central claim will be evaluated on a real mobile robot in controlled indoor scenarios with reproducible dynamic route-invalidating events. Simulation is used for development and commissioning only; it does not substitute for the physical-robot efficacy study.

## Repository structure

```text
docs/                 scientific specification and experimental protocol
src/recovernav/       minimal research implementation
robot/                ROS 2 / Nav2 integration for the physical robot
experiments/          scenario definitions and trial runners
analysis/             preregistered statistical analysis
configs/              frozen experiment configurations
data/
  raw/                immutable physical-trial data
  processed/          derived datasets
  manifests/          provenance and trial manifests
tests/                software and research-contract tests
```

## Scientific discipline

RecoverNav follows these rules:

- one primary research question;
- one prespecified primary endpoint;
- matched/paired baseline-vs-treatment trials where possible;
- explicit inclusion, exclusion, failure, and intervention rules;
- immutable raw data;
- no efficacy claim based only on simulation;
- no claim that the recoverability score is a calibrated probability unless calibration is demonstrated;
- protocol changes after data collection begins must be documented and versioned.

## Current status

**Phase 0 — protocol and implementation specification.**

No physical-robot efficacy result is claimed yet.

Start with:

- [`docs/RESEARCH_QUESTION.md`](docs/RESEARCH_QUESTION.md)
- [`docs/EXPERIMENT_PROTOCOL.md`](docs/EXPERIMENT_PROTOCOL.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
