# Study A — Recoverability Construct Validation Protocol

**Status:** preregistration candidate. Freeze before confirmatory Study A data collection.

## Research question

Does the frozen pre-event RecoverNav structural score `rho` contain information about whether the physical robot can autonomously recover after a controlled route invalidation under a frozen recovery policy?

Study A does **not** test whether the RecoverNav planner reduces navigation failures. It tests whether the proposed recoverability construct is behaviorally meaningful.

## Unit of observation

One recovery probe consists of:

1. a physical robot placed/executed at a prespecified route state;
2. a pre-event map/observation snapshot;
3. a pre-event `rho` score computed without knowledge of the event realization;
4. a controlled invalidating event from the frozen event family;
5. execution of the same frozen recovery policy;
6. a binary recovery outcome.

## Primary label

`recovery_success = 1` only if, after the event, the robot autonomously reaches the prespecified recovery-valid state or goal-valid state within the frozen timeout without disallowed contact or human intervention.

Otherwise `recovery_success = 0`.

Exact timeout, terminal safety-stop, localization-loss, and contact rules must be frozen after commissioning and before confirmatory collection.

## Predictor

The primary predictor is the pre-event frozen estimator score `rho_pre_event` from `RECOVERABILITY_ESTIMATOR_V1.md`.

It is computed before the event and stored before the outcome is attached. The score function must not accept event identity, future blocked region, or recovery outcome as input.

## Scenario design

The confirmatory set must span structural variation rather than many repetitions of one map. Include prespecified instances from at least these classes where physically realizable:

- single-escape / corridor commitment;
- branching alternative-route geometry;
- multiple apparent alternatives sharing one bottleneck;
- footprint-constrained alternative;
- open region with multiple feasible alternatives;
- partial-observation case in which unknown space is not credited as free.

Scenario construction must intentionally produce both recovery successes and failures; a dataset containing only one outcome class cannot validate discrimination.

## Separation of phases

### Commissioning

Used to debug graph extraction, anchor semantics, event execution, logging, timeout values, and robot safety. Parameters may change. These observations are permanently labeled commissioning and excluded from confirmatory Study A estimates.

### Confirmatory Study A

Estimator definition, graph extraction, parameters, event family, recovery policy, endpoint, exclusions, and analysis are frozen. No estimator tuning is permitted against confirmatory labels.

## Primary construct-validity analysis

Report:

- number of valid probes and outcome counts;
- `rho` distribution by recovery outcome;
- ROC-AUC with an uncertainty interval;
- the direction and magnitude of association between `rho` and recovery outcome;
- runtime distribution for estimator evaluation;
- all high-score failures and low-score successes as counterexamples.

ROC-AUC is evidence of discrimination, not calibration and not proof of causality.

## Decision gate

Study A is considered sufficient to justify Study B only if all of the following are satisfied under the frozen confirmatory set:

1. the score has a prespecified positive association with executed recovery outcome;
2. discrimination is meaningfully above chance with uncertainty reported;
3. the result is not driven solely by ordinary minimum clearance;
4. counterexamples are understood well enough that the construct remains interpretable;
5. estimator runtime is compatible with the intended online planning architecture;
6. no future-event information leakage is identified.

The exact numeric go/no-go discrimination threshold and uncertainty criterion must be selected before confirmatory data collection, informed by commissioning but not confirmatory outcomes.

## Required negative control

Compare `rho` against at least a simple clearance-only predictor computed from the same pre-event information. RecoverNav v1 is not scientifically useful if its apparent predictive ability is merely ordinary path clearance under another name.

## Data integrity

Each probe must retain the fields required by `experiments/study_a/trial.schema.json`, plus references to the raw robot log/ROS bag where available. Raw confirmatory records are immutable. Corrections create a new processed record with provenance; they do not overwrite the raw observation.

## Claim discipline

If Study A succeeds, the maximum supported claim is that the frozen structural score contains predictive information about subsequent recovery outcomes under the tested robot, environment, event family, and recovery policy.

If Study A fails, do not proceed to a confirmatory planner-efficacy claim using v1. Revise or reject the estimator and begin a new explicitly versioned validation cycle.
