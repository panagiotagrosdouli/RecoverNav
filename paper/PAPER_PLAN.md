# RecoverNav — Paper Plan

## Target paper concept

**Working title**

**RecoverNav: Predicting and Preserving Post-Invalidation Recoverability for Physical Mobile-Robot Navigation**

Alternative conservative title:

**Bottleneck-Aware Recoverability Estimation for Dynamic Indoor Mobile-Robot Navigation**

## Core paper claim

The paper should not claim generic safe navigation or novel contingency planning.

The central contribution is a two-stage empirical study:

1. validate whether a lightweight robot-observable structural score predicts post-invalidation recovery outcome;
2. after freezing that score, test whether using it for route selection reduces recovery failures on a physical mobile robot compared with an otherwise matched baseline.

## Paper research questions

### RQ1 — construct validity

Does the frozen bottleneck-aware escape-capacity estimator contain predictive information about subsequent executed recovery feasibility after an unknown-at-decision-time route invalidation?

### RQ2 — decision usefulness

Does adding the frozen estimator to the route objective reduce the prespecified post-invalidation recovery-failure rate compared with the same navigation stack without the recoverability term?

### RQ3 — cost of robustness

What path-length, task-time, planning-latency, and computational overhead is incurred by RecoverNav?

## Hypotheses

### H1A

Lower pre-event recoverability scores are associated with a higher probability of post-invalidation recovery failure under the frozen event family and recovery policy.

### H1B

RecoverNav produces a lower paired post-invalidation recovery-failure rate than J0 under the frozen physical-robot protocol.

The null hypotheses must remain valid possible outcomes.

## Contribution list for a paper

A strong first paper would contribute:

1. an operational definition of post-invalidation recoverability for indoor robot navigation;
2. a lightweight bottleneck-aware escape-capacity estimator derived only from information available at decision time;
3. a separate estimator-validation study rather than assuming the heuristic is meaningful;
4. integration into a conventional route objective with a single treatment parameter;
5. a controlled matched physical-robot experiment under reproducible route-invalidating events;
6. quantitative failure, efficiency, and compute-overhead analysis;
7. explicit negative/counterexample analysis and claim–evidence discipline.

## Required figures

### Figure 1 — Problem formulation

A simple indoor topology with two possible routes. The shorter route enters a commitment corridor; the alternative preserves more escape capacity. The dynamic blockage is not known at planning time.

### Figure 2 — Recoverability estimator

Occupancy/costmap -> footprint-aware graph -> local horizon -> recovery anchors -> capacity/max-flow -> route weakest-point score.

### Figure 3 — Study A construct validation

Distribution of pre-event score by executed recovery outcome and a discrimination/association plot with uncertainty.

### Figure 4 — Physical experiment

Robot, environment, fixed start/goal, event trigger region, and example J0/JR trajectories.

### Figure 5 — Primary paired outcome

Paired failure comparison / discordant-pair visualization with absolute risk difference and uncertainty interval.

### Figure 6 — Trade-off

Path-length or task-time overhead versus recovery outcome; optionally compute latency.

### Figure 7 — Failure cases

Representative false-positive/false-negative estimator cases and RecoverNav-vs-baseline counterexamples.

## Required tables

### Table 1 — Prior-work positioning

Columns:

- work;
- future-feasibility concept;
- unknown future invalidation;
- estimator validated against executed outcome;
- explicit contingency target;
- formal guarantee;
- physical robot;
- relation to RecoverNav.

Include ICS, Braking ICS, viability, Contingency-MPPI, SCRAMPPI, and RecoverNav.

### Table 2 — Robot and software configuration

Exact robot, sensors, compute, ROS 2, Nav2, map/localization/controller, footprint, safety limits, and Git commit.

### Table 3 — Scenario set

Start/goal, route geometry, invalidation type, trigger rule, pair/block design.

### Table 4 — Main quantitative results

Failure counts/rates, paired effect estimate, uncertainty, path/time overhead, planning latency.

## Suggested manuscript structure

1. Introduction
2. Related Work
3. Problem Formulation
4. Recoverability Estimator
5. Study A: Estimator Validation
6. RecoverNav Planner Integration
7. Study B: Physical-Robot Experimental Protocol
8. Results
9. Failure and Sensitivity Analysis
10. Discussion
11. Limitations
12. Conclusion

## Introduction logic

The introduction should make the following argument:

1. dynamic indoor navigation can invalidate a route after a robot has already committed to a difficult region;
2. existing safe/contingency frameworks establish that future feasibility matters, so this broad idea is not new;
3. however, ordinary navigation stacks often lack a lightweight, empirically validated measure of whether the currently selected route preserves recoverability against an unspecified future local invalidation;
4. RecoverNav asks whether such a measure can be predicted from currently observed structure and whether that information is decision-useful on a real robot;
5. the paper separates construct validation from planner efficacy to avoid assuming the proposed score represents real recovery.

## Related-work positioning

The manuscript must prominently discuss:

- Inevitable Collision States;
- Braking ICS / passive safety;
- viability-based safe navigation;
- safe replanning under kinodynamic/partial knowledge;
- Contingency-MPPI;
- SCRAMPPI/HJ reachability.

Do not say "unlike all previous work" unless a systematic search supports that claim.

## Study A acceptance gate

Study B confirmatory efficacy testing should not begin until:

- the estimator implementation is frozen;
- the event family and recovery label are frozen;
- held-out validation shows the estimator captures nontrivial recovery information;
- runtime is acceptable;
- obvious map-resolution/clearance artifacts are controlled;
- false-positive and false-negative cases are understood well enough to state limitations.

## Study B acceptance gate

Before confirmatory physical trials freeze:

- robot configuration;
- J0 and JR implementation;
- lambda_R;
- event triggers;
- scenario set;
- primary endpoint;
- exclusion rules;
- sample-size/power or precision target;
- randomization/counterbalancing schedule;
- statistical analysis plan;
- commit SHA and configuration hashes.

## Statistics

The primary efficacy endpoint is paired binary data. Report discordant pairs and a paired effect estimate with uncertainty. Do not rely on a single p-value.

For Study A, treat AUC/association as estimator-validity evidence, not as proof of causal planner benefit.

Secondary continuous outcomes should use paired analysis where the pairing remains valid.

## Negative-result publication path

The project can still produce a useful paper if:

- the structural estimator predicts recovery but does not improve route selection;
- it improves recovery at excessive efficiency cost;
- it fails to predict physical recovery, provided the failure is rigorously analyzed and exposes limits of structural proxies;
- the effect is scenario-dependent and the boundary conditions are characterized.

Do not design the paper so that only a positive result is publishable.

## Candidate venues

Venue choice should wait until the contribution strength and experiment scale are known. Plausible families include robotics conferences/journals focused on autonomous navigation, planning, and experimental robotics. The final venue must be selected based on actual novelty and evidence rather than prestige-first targeting.

## Submission readiness checklist

A paper is not submission-ready until all of the following are true:

- novelty review is updated;
- estimator formula and parameters are frozen;
- physical robot exists and configuration is documented;
- Study A has held-out validation evidence;
- Study B has enough prespecified physical trials;
- raw trial artifacts are retained;
- statistics are reproducible from scripts;
- every figure/table is generated from retained data;
- failure cases and limitations are included;
- no claim exceeds the claim–evidence matrix.

## Current status

**Paper concept is now defined. Method and evidence are not yet sufficient for submission.**

The next work item is implementation and adversarial unit testing of `RECOVERABILITY_ESTIMATOR_V1.md`, followed by Study A data-generation/validation infrastructure.