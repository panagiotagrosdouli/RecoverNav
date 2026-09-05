# Research Question and Hypotheses

## Primary research question

> **Does explicitly preserving recovery options during planning reduce post-invalidation navigation failures on a physical mobile robot compared with conventional navigation in dynamic, partially observed indoor environments?**

## Scientific scope

The study concerns a mobile robot executing point-to-point indoor navigation. During execution, a controlled environmental change invalidates or materially degrades the currently preferred route. The scientific question is whether a planner that accounts for future recoverability before the change occurs yields fewer unrecoverable failures than a conventional baseline.

The contribution is intentionally narrow: **recoverability-aware route choice before route invalidation**.

## Primary hypothesis

**H1:** Under matched physical-robot trials with controlled route-invalidating events, the RecoverNav planner has a lower probability of post-invalidation recovery failure than the baseline planner.

## Null hypothesis

**H0:** Under the same conditions, the probability of post-invalidation recovery failure is not lower for RecoverNav than for the baseline planner.

## Primary endpoint

For trial `i`:

```text
Y_i = 1  if the robot cannot autonomously recover and complete the task
Y_i = 0  if the robot autonomously recovers and completes the task
```

The exact timeout, intervention, collision, localization-loss, and infeasibility rules are fixed in the experiment protocol before confirmatory data collection.

## Secondary outcomes

Secondary outcomes characterize the cost of robustness and failure mechanism:

- time from route invalidation to resumed progress;
- total task completion time;
- replanning latency;
- executed path length;
- minimum obstacle clearance;
- number of replans;
- number and type of safety stops;
- human interventions;
- localization failure;
- collision/contact events;
- recoverability score at decision points.

These are secondary. They must not replace the prespecified primary endpoint after results are observed.

## Treatment definition

### Baseline: J0

Navigation using the same robot, map representation, perception stack, controller, localization stack, safety configuration, and event schedule, but **without** an explicit recoverability term in route evaluation.

### RecoverNav: JR

The same system plus an explicit recoverability/irreversibility term:

```text
J(P) = L(P) + lambda_R * R(P)
```

`R(P)` must depend only on information available to the robot at decision time. No future event information may leak into planning.

## What counts as recoverability

Recoverability is not assumed to be a probability. Initially it is an operational score representing the extent to which a robot state or planned path preserves feasible alternatives after plausible local route invalidation.

A valid recoverability estimator should ultimately satisfy three conditions:

1. **Information validity:** it uses only robot-available state at decision time.
2. **Behavioral relevance:** lower predicted recoverability is associated with worse executed recovery outcomes.
3. **Decision usefulness:** incorporating it into planning improves the prespecified primary endpoint under controlled comparison.

## Required falsification conditions

The central hypothesis must be considered unsupported if, under the frozen protocol:

- RecoverNav does not reduce primary failures;
- any apparent benefit depends on unequal controller, perception, safety, or event settings;
- the planner benefits from information unavailable to the baseline or unavailable at decision time;
- improvement appears only after post-hoc scenario or metric selection;
- physical-robot results fail to reproduce across the prespecified scenario set.

## Claims explicitly out of scope for the first study

The first study does **not** aim to establish:

- universal safety of autonomous navigation;
- optimality over all dynamic planners;
- generalization to outdoor, multi-floor, or unstructured environments;
- human-aware social navigation;
- calibrated probabilistic prediction of recovery success;
- superiority on every efficiency metric;
- efficacy based on simulation alone.

## Target scientific conclusion

A valid positive conclusion would be narrow:

> Under the prespecified physical indoor scenarios and controlled dynamic route-invalidating events, adding the tested recoverability-aware objective reduced the prespecified rate of post-invalidation recovery failures relative to the matched baseline, with quantified uncertainty and measured efficiency overhead.

Anything stronger requires additional evidence.
