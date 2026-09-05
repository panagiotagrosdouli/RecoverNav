# RecoverNav Roadmap

## Principle

Every implementation task must trace to the primary research question. Features that do not improve experimental validity, robot execution, recoverability estimation, or evidence quality are deferred.

## Phase 0 — Research specification

- [x] Define one primary research question.
- [x] Define H0/H1.
- [x] Define the primary endpoint.
- [x] Define baseline and treatment at a conceptual level.
- [x] Draft the physical-robot experiment protocol.
- [ ] Freeze numerical failure thresholds after commissioning.
- [ ] Choose and document the physical robot platform.
- [ ] Choose the first physical test environment and measure it.

**Exit criterion:** an independent reader can understand exactly what evidence would support or falsify the central claim.

## Phase 1 — Minimal research core

Implement only what is necessary for the comparison:

- [ ] typed environment/state representation;
- [ ] baseline route objective `J0`;
- [ ] recoverability estimator `R`;
- [ ] treatment route objective `JR`;
- [ ] deterministic configuration and logging;
- [ ] tests for treatment isolation and no future-information leakage.

**Exit criterion:** given the same state, both planners differ only by the recoverability treatment and produce fully auditable outputs.

## Phase 2 — Recoverability validation

Before using `R` as a scientific explanatory variable:

- [ ] define candidate recoverability features;
- [ ] create controlled recovery probes;
- [ ] execute recovery outcomes in simulation and then on the robot;
- [ ] test association between `R` and observed recovery feasibility;
- [ ] reject/revise estimators that lack behavioral relevance;
- [ ] freeze the estimator before confirmatory efficacy trials.

**Exit criterion:** the recoverability quantity has empirical behavioral validity beyond geometric intuition.

## Phase 3 — ROS 2 / Nav2 robot integration

- [ ] create ROS 2 package structure;
- [ ] integrate baseline and RecoverNav global planning under identical Nav2 settings;
- [ ] add event-state and trial-state logging;
- [ ] record software/configuration hashes;
- [ ] add safety configuration and emergency-stop procedure;
- [ ] verify deterministic experiment startup.

**Exit criterion:** the real robot can execute baseline and treatment trials from the same launch interface and produce complete artifacts.

## Phase 4 — Scenario commissioning

- [ ] implement at least three distinct route-choice scenarios;
- [ ] implement reproducible route-invalidating events;
- [ ] validate sensing and event detection;
- [ ] tune only prespecified operational thresholds;
- [ ] mark all runs as commissioning;
- [ ] estimate nuisance rates needed for sample-size planning.

**Exit criterion:** event execution, data capture, and failure adjudication work reliably without changing the scientific question.

## Phase 5 — Freeze

Create a tagged release containing:

- [ ] planner code;
- [ ] recoverability estimator;
- [ ] robot configuration;
- [ ] scenario definitions;
- [ ] event triggers;
- [ ] failure thresholds;
- [ ] inclusion/exclusion rules;
- [ ] randomization schedule;
- [ ] sample-size justification;
- [ ] statistical analysis plan.

**Exit criterion:** no confirmatory outcome has yet been inspected under a mutable protocol.

## Phase 6 — Physical confirmatory study

- [ ] execute matched J0/JR trial pairs;
- [ ] preserve immutable raw data;
- [ ] record all exclusions and interventions;
- [ ] monitor only safety/data integrity during collection;
- [ ] complete the prespecified sample unless a protocol stop condition is met.

**Exit criterion:** confirmatory dataset is complete and locked.

## Phase 7 — Analysis

- [ ] run the frozen primary paired analysis;
- [ ] estimate absolute treatment effect with uncertainty;
- [ ] analyze secondary efficiency/safety outcomes;
- [ ] inspect scenario heterogeneity as secondary evidence;
- [ ] run prespecified sensitivity analyses;
- [ ] generate reproducible tables and figures from raw-data manifests.

**Exit criterion:** every reported number can be regenerated from retained artifacts.

## Phase 8 — Scientific output

- [ ] write results without exceeding evidence;
- [ ] publish code/configuration/protocol;
- [ ] publish allowable raw/processed data or an auditable substitute;
- [ ] document negative and failure cases;
- [ ] prepare manuscript/thesis chapter.

## Deferred until after the primary study

Do not add these before the main question is answered unless they are strictly necessary for the experiment:

- learning-based planners;
- multi-robot coordination;
- social navigation;
- web dashboards;
- large UI layers;
- security research modules;
- broad mapping extensions;
- multiple unrelated planning algorithms;
- autonomous claims outside the controlled indoor scope.
