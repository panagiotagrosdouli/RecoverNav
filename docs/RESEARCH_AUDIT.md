# RecoverNav — Initial Scientific Audit

**Status:** pre-implementation research audit  
**Purpose:** decide whether the proposed research question is scientifically defensible before building the system.

## 1. Audit conclusion

RecoverNav currently has a strong *experimental intent* but its novelty cannot be claimed as simply "planning while preserving recovery options." That broad idea already overlaps substantially with established work on Inevitable Collision States (ICS), viability-based navigation, contingency-constrained planning, and recent reachability-based contingency planning.

The project therefore must make a narrower contribution and test it directly on a physical mobile robot.

The current candidate contribution is:

> **A lightweight, robot-information-conditioned recoverability estimator used for pre-invalidation route selection in partially observed indoor navigation, evaluated by whether it predicts and reduces post-invalidation recovery failure under matched physical-robot trials.**

This is a *candidate* research gap, not yet an established novelty claim. The literature review must continue until the estimator, information assumptions, intervention point, baseline, and physical protocol have been compared against the closest prior work.

## 2. What the repository already gets right

The current research specification has several good properties:

- one primary physical-robot research question;
- an explicit null and alternative hypothesis;
- a binary primary endpoint;
- a baseline/treatment comparison that attempts to isolate the recoverability term;
- a no-future-information requirement;
- matched trials;
- separation of commissioning from confirmatory data;
- predefinition of exclusions and protocol deviations;
- recognition that simulation is not efficacy evidence;
- an explicit willingness to accept a negative result.

These principles should be preserved.

## 3. Main scientific problem found

### 3.1 The broad novelty claim is too close to prior work

RecoverNav cannot claim novelty merely because it preserves an escape, backup, or recovery option while following a nominal plan.

Relevant neighboring ideas include:

1. **Inevitable Collision States (ICS):** formalizes states from which collision is unavoidable regardless of future robot trajectory, including dynamic obstacles and partially known environments.
2. **Viability-based navigation:** reasons about sets of states from which at least one admissible future trajectory remains available under constraints.
3. **Contingency-MPPI:** explicitly embeds contingency planning inside nominal planning and has simulation and mobile-robot hardware evidence.
4. **SCRAMPPI:** formulates contingency feasibility as a reach-avoid problem and uses Hamilton–Jacobi reachability to maintain feasible retreat to a safe set, with simulated and hardware experiments.
5. **Free-region/dead-end planners:** recent planners also explicitly reason about free-space topology, narrow passages, dead ends, and alternative navigation options.

Therefore, "preserve recovery options" is a research area, not by itself a new contribution.

### 3.2 Recoverability is not yet operational enough

The current definition is intentionally cautious but still insufficient for implementation. Before a planner objective is written, the project must define exactly:

- what state is being recovered *from*;
- what target set constitutes successful recovery;
- what perturbation/event family recovery is defined *against*;
- what horizon applies;
- which robot dynamics/kinematics are included;
- what information is available at decision time;
- whether the quantity is binary feasibility, a margin, a proxy, or a probability;
- how the estimator will be validated independently of planner performance.

Without these definitions, `R(P)` risks becoming an arbitrary geometric penalty whose semantic name overstates what it measures.

### 3.3 The primary endpoint currently mixes mechanisms

The existing primary failure definition can include timeout, collision, localization failure, terminal safety stop, intervention, and being trapped. These are important outcomes, but combining all of them into one primary endpoint may obscure the mechanism under study.

A localization collapse, for example, is not necessarily evidence of poor route recoverability. A collision caused by a controller fault is also mechanistically different from being trapped after route invalidation.

Before confirmatory trials, the project should define a narrow target failure attributable to loss of recovery feasibility and retain broader mission failure as a secondary/safety endpoint.

## 4. Revised research question

The original question is retained as the high-level motivation, but the testable question should become more precise:

> **Among matched indoor navigation trials in which an initially viable route is invalidated after route commitment, does selecting routes using a prevalidated recoverability estimator reduce post-invalidation recovery-infeasible failures on a physical mobile robot relative to the same navigation stack without that estimator?**

Important terms in this sentence must receive executable definitions before confirmatory data collection.

## 5. Proposed decomposition of the research programme

The central question should be answered in two linked studies rather than jumping directly to planner efficacy.

### Study A — estimator validity

**Question:** Does the proposed recoverability quantity predict executed recovery feasibility from robot-observable state?

Unit: a decision state / controlled recovery probe.

Required separation:

- estimator development data;
- calibration/tuning data if applicable;
- held-out validation states/scenarios.

A geometric proxy should be evaluated as a proxy. It must not be called a probability unless calibrated and evaluated as one.

**Gate:** Do not proceed to a confirmatory planner-efficacy claim unless the estimator shows predefined behavioral relevance on held-out recovery outcomes.

### Study B — planner efficacy

**Question:** Does using the validated estimator for route selection reduce the prespecified target failure in matched physical trials?

Comparison:

- `J0`: baseline route objective;
- `JR`: identical stack with the recoverability term/constraint.

All other settings remain matched.

This decomposition prevents a failed planner experiment from being uninterpretable: if JR fails, we can distinguish "the estimator was invalid" from "the estimator was valid but not decision-useful."

## 6. Formal recoverability target — working definition

Let the robot information state at decision time be

`z_t = (x_hat_t, M_t, Sigma_t, robot_model, limits)`

where `x_hat_t` is the estimated robot state, `M_t` is the currently observed/map representation, `Sigma_t` summarizes relevant uncertainty, and `limits` contains frozen motion/safety limits.

Let `E` be a prespecified family of local route-invalidating events that are *not revealed to the planner before sensing makes them available*.

Let `S_safe(z_t)` be a predefined set of acceptable recovery states, such as states from which the robot can resume goal-directed navigation without intervention under the frozen navigation policy.

For event realization `e`, define executed recovery feasibility:

`F(z_t, e) = 1` if a valid autonomous trajectory from the post-event state reaches `S_safe` within the frozen recovery horizon while respecting collision and motion constraints; otherwise `0`.

The first RecoverNav estimator should be written as

`r_hat(z_t) -> recoverability margin/proxy`

and **not** as a probability unless calibration evidence justifies that interpretation.

The research task is to test whether `r_hat(z_t)` has held-out association with `F`, and only then whether route selection using `r_hat` improves Study B outcomes.

## 7. Minimum viable physical experiment

The first experiment should deliberately avoid broad environmental diversity.

Use a controlled indoor route-choice layout with:

- one start region;
- one goal region;
- at least two feasible pre-event routes;
- one route containing a commitment/bottleneck region with limited post-blockage retreat or alternative exit structure;
- another route with greater recovery feasibility but potentially greater nominal path cost;
- a repeatable route-invalidating event;
- geometry/state-based event triggering;
- the same robot, localization, perception, controller, costmaps, speed limits, and safety system in both conditions.

The event must not encode planner identity and must not be known by JR before it becomes observable according to the frozen sensing model.

### Physical event mechanism

Prefer an actuated or precisely scripted obstruction over an operator deciding when to place an obstacle. If manual placement is unavoidable during commissioning, the confirmatory mechanism must still have an objective trigger and logged event timing.

### Required instrumentation

Each trial should record at minimum:

- ROS bag/state log;
- robot pose and covariance;
- local/global costmaps or equivalent map state;
- global path updates;
- velocity commands and odometry;
- event trigger and event state;
- planner condition;
- recoverability estimate at decision points for JR;
- safety/intervention events;
- trial outcome;
- software commit and configuration hash.

Synchronized video is strongly recommended for audit but should not be the sole source for primary-outcome classification.

## 8. Baseline fairness

The baseline must be a credible conventional navigation configuration, not an intentionally weak planner.

`J0` and `JR` must share:

- global map/costmap inputs;
- localization;
- controller;
- local obstacle avoidance;
- replanning trigger;
- recovery behaviors except for the treatment being tested;
- speed/acceleration limits;
- footprint/inflation;
- safety monitor;
- sensing horizon and observations.

The only intended causal difference is the recoverability-aware route decision.

## 9. Primary endpoint revision

Before confirmatory collection, define two distinct quantities.

### Primary mechanistic endpoint

`post_invalidation_recovery_infeasible_failure`

This should be `1` only when, after the predefined event, the robot cannot autonomously regain a predefined recoverable/navigation state or complete the route under the frozen recovery policy within the recovery horizon for reasons attributable to route/recovery feasibility.

### Secondary mission/safety endpoints

Keep separately:

- collision/contact;
- localization failure;
- terminal safety stop;
- human intervention;
- overall task failure;
- task timeout.

Rules for how safety interventions affect the primary endpoint must be frozen before confirmatory trials.

## 10. Major threats to validity

### Construct validity

- `r_hat` may measure corridor width or clearance rather than recoverability.
- the chosen safe set may make the conclusion tautological;
- recovery horizon may determine the label more than actual route structure.

### Internal validity

- event timing may differ between planners because paths/speeds differ;
- baseline and treatment may expose different observations before the event;
- operator behavior may leak condition identity;
- battery/localization drift may correlate with trial order;
- treatment may alter speed or path tracking indirectly rather than only route choice.

### Statistical validity

- physical trial counts may be too small for a binary endpoint;
- repeated trials in the same scenario are not independent environmental replications;
- tuning lambda on confirmatory outcomes would leak test information;
- scenario-specific effects can dominate pooled results.

### External validity

A controlled two-route indoor study supports a narrow claim. It does not establish general navigation safety, arbitrary dynamic-obstacle robustness, or transfer to outdoor/unstructured settings.

## 11. Pre-confirmatory gates

No confirmatory efficacy trial should begin until all gates are satisfied:

- [ ] closest-prior-work review completed and novelty statement revised;
- [ ] robot platform frozen;
- [ ] recoverability target and safe set formally defined;
- [ ] estimator implementation frozen;
- [ ] estimator held-out validation completed;
- [ ] baseline fairness audit passed;
- [ ] event mechanism validated for repeatability;
- [ ] primary mechanistic endpoint frozen;
- [ ] failure taxonomy frozen;
- [ ] exclusion rules frozen;
- [ ] randomization/counterbalancing schedule generated;
- [ ] sample-size/power or precision target justified;
- [ ] statistical analysis plan frozen;
- [ ] data schema and immutable raw-data procedure tested;
- [ ] safety protocol approved for the actual laboratory/platform;
- [ ] code/configuration tagged with a confirmatory-study version.

## 12. Priority order from this audit

1. Complete closest-prior-work review, especially contingency planning, reachability, ICS, viability, and real mobile-robot studies.
2. Freeze an executable definition of recovery feasibility and the event family.
3. Design Study A and validate the estimator before optimizing a planner around it.
4. Select and document the physical robot/platform.
5. Implement only the minimal estimator + baseline/treatment route-choice core.
6. Build simulation/bench tests for software commissioning, not as central efficacy evidence.
7. Integrate the frozen treatment into ROS 2/Nav2.
8. Commission the physical event mechanism and logging pipeline.
9. Freeze the confirmatory protocol, analysis plan, and sample size.
10. Run matched physical trials without outcome-driven tuning.
11. Analyze all retained trials, including counterexamples and adverse trade-offs.
12. Write the conclusion at the strength permitted by the evidence.

## 13. Current claim boundary

At this stage RecoverNav has **no efficacy result** and **no established novelty claim**. It has a prespecified research direction and experimental philosophy. The next legitimate evidence is literature-grounded novelty analysis and estimator construct validation, not a statement that recoverability-aware navigation works.
