# RecoverNav — Closest Prior-Work Deep Review

**Status:** research-development review, 2026-09-05. Novelty remains provisional until the final method and physical protocol are frozen.

## Purpose

This document tests the RecoverNav idea against the closest known scientific concepts rather than searching for supportive citations. The central question is whether RecoverNav can make a distinct, falsifiable contribution beyond established collision inevitability, viability, contingency planning, and reachability methods.

## 1. Inevitable Collision States (Fraichard & Asama, 2004)

An Inevitable Collision State (ICS) is a state from which collision eventually occurs regardless of the future trajectory. The framework explicitly reasons about robot and obstacle dynamics and was motivated in part by safe motion planning under sensing constraints in partially known environments.

### Overlap

The deep conceptual overlap is the rejection of purely immediate geometric feasibility. Both ICS reasoning and RecoverNav care about whether a current decision destroys useful future options before failure becomes unavoidable.

### Non-equivalence

RecoverNav's proposed target is not simply `collision inevitable / avoidable`. It is an executed, policy-dependent post-invalidation recovery outcome after a route-changing event. A robot can fail to recover a navigation task without being in an ICS, and an ICS framework does not by itself define the proposed empirical recovery endpoint.

### Consequence for RecoverNav

RecoverNav must not claim novelty for the generic principle "avoid states with no future escape." Its contribution, if supported, must lie in the operational recovery construct, estimator, conventional navigation integration, or physical evaluation methodology.

## 2. Contingency-MPPI (Jung, Estornell & Everett, L4DC 2025)

Contingency-MPPI embeds contingency planning inside nominal planning. Its stated motivation is that autonomous systems must account for sudden changes and retain contingency behavior. The method uses an optimization/sampling strategy and reports both simulation and mobile-robot hardware experiments.

### Overlap

This is direct prior art against any broad claim that RecoverNav is the first navigation method to preserve backup behavior during nominal motion. Both approaches modify nominal decision-making because future adverse changes may require an alternative behavior.

### Candidate distinction

RecoverNav is currently framed around a route-level, robot-information-conditioned estimate of *post-route-invalidation recovery feasibility* in a conventional indoor ROS 2/Nav2-style stack, validated first against executed recovery labels and only then used for route choice. Contingency-MPPI instead explicitly optimizes nominal and contingency control behavior.

This is only a candidate distinction. It is scientifically meaningful only if the RecoverNav estimator has a well-defined target, predicts held-out physical recovery outcomes, and yields a useful decision rule without simply recreating contingency trajectory optimization under another name.

## 3. SCRAMPPI (Srirangam, Jung, Poola & Everett, 2026)

SCRAMPPI formalizes contingency feasibility as a reach-avoid problem. It uses Hamilton–Jacobi reachability to represent a safe-set backward reachable set online and integrates the resulting constraint with MPPI. The stated requirement is that a feasible trajectory to a designated safe set should exist from points along the nominal plan. Simulation and mobile-robot hardware experiments are reported.

### Overlap

This is an especially close conceptual neighbor. It directly formalizes preserving a feasible contingency to a safe set while pursuing nominal behavior.

### Candidate distinction

RecoverNav should not attempt to compete by making a weaker version of a certified reachability constraint. A defensible alternative research question is whether an inexpensive, interpretable estimator tied to *executed route-invalidation recovery outcomes* can provide useful route-selection information in ordinary indoor navigation when full reachability/contingency optimization is impractical or mismatched to the navigation architecture.

### Required evidence

A claim of practical distinction requires measurements, not rhetoric: estimator runtime, planning overhead, information requirements, failure modes, and physical recovery outcomes. If a reachability/contingency baseline can be implemented fairly within the same problem setting, it should eventually be considered as a secondary strong baseline.

## 4. What these works already establish

RecoverNav must treat the following broad ideas as established territory:

- future feasibility can matter more than instantaneous collision freedom;
- nominal motion can be constrained by the need for a contingency/backup behavior;
- safe/backup sets can be treated using reachability concepts;
- contingency-aware methods have already been demonstrated on physical mobile robots.

Therefore none of these statements is a valid standalone novelty claim for RecoverNav.

## 5. Narrow candidate gap

The candidate gap is now deliberately narrower:

> Can a computationally lightweight, interpretable, robot-observable estimator of post-route-invalidation recovery feasibility be validated against held-out executed recovery outcomes and then improve pre-invalidation route selection in a conventional indoor mobile-robot navigation stack under matched physical trials?

This candidate gap has two separable scientific questions:

### Study A — construct/estimator validity

Does the pre-event estimator contain information about subsequent executed recovery feasibility under a frozen event family and recovery policy?

### Study B — decision usefulness

After Study A is frozen, does using that estimator for route selection reduce the prespecified recovery-infeasible failure endpoint compared with a matched baseline, at an acceptable efficiency/compute cost?

Study B is not scientifically interpretable if Study A fails.

## 6. Novelty kill conditions

The proposed contribution should be revised or abandoned if deeper review finds prior work that already combines all or nearly all of the following under comparable assumptions:

1. pre-event robot-observable recovery-feasibility estimation;
2. validation of that estimate against executed physical recovery outcomes;
3. route-level use before invalidation rather than only local emergency control;
4. dynamic/partially observed indoor navigation;
5. conventional navigation-stack integration;
6. matched physical comparison using a recovery-specific endpoint;
7. comparable computational/information assumptions.

## 7. Implications for estimator design

The first RecoverNav estimator should not be a large weighted collection of intuitive features. The initial scientific object should be an interpretable *recovery margin* with explicit semantics.

A promising first direction is bottleneck-aware alternative-route feasibility:

- represent currently known traversable space as a footprint-aware graph;
- identify commitment/bottleneck regions along a candidate route;
- for each sampled route state, determine whether a feasible retreat or alternative continuation exists without depending on the candidate failure edge/region;
- incorporate robot footprint and turning feasibility;
- summarize the route conservatively by its weakest recovery margin.

The exact formula is not frozen by this review. It must survive toy counterexamples and Study A validation before planner efficacy testing.

## 8. Baseline policy

For the primary causal comparison, the baseline should differ only in the recoverability treatment. A conventional shortest/costmap route objective is therefore appropriate for J0 if all perception, controller, localization, safety, replanning, and event settings are held fixed.

A stronger contingency/reachability method is valuable as a secondary scientific reference if it can be made comparable, but it must not replace the clean J0-vs-RecoverNav treatment comparison needed to isolate the estimator's effect.

## 9. Current conclusion

The project is scientifically plausible but novelty is not yet established. The broad recoverability/backup-options idea is demonstrably not novel. The strongest remaining path is an empirical construct-validation contribution plus a tightly controlled physical-robot route-selection study.

The next gate is therefore not implementation volume. It is to freeze an operational estimator candidate, adversarially test its semantics, and preregister Study A's validation criterion.

## Primary bibliographic anchors

- T. Fraichard and H. Asama, “Inevitable collision states — a step towards safer robots?”, *Advanced Robotics*, 18(10):1001–1024, 2004. DOI: 10.1163/1568553042674662.
- L. Jung, A. Estornell, and M. Everett, “Contingency Constrained Planning with MPPI within MPPI,” *Proceedings of L4DC*, PMLR 283:869–880, 2025.
- R. H. Srirangam, L. Jung, R. Poola, and M. Everett, “SCRAMPPI: Efficient Contingency Planning for Mobile Robot Navigation via Hamilton-Jacobi Reachability,” arXiv:2603.26995, 2026.

## Review limitations

This pass establishes close conceptual overlap from primary publication records/abstracts and available method descriptions. It is not yet a systematic review. Before publication-facing novelty language is frozen, full methods, assumptions, experiments, and cited predecessors of the closest works must be reviewed and recorded.