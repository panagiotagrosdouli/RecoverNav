# RecoverNav Evidence Policy

RecoverNav is a research project. Scientific claims must be traceable to real executions and auditable raw data.

## 1. Unit tests are not evidence

Toy graphs, synthetic fixtures, handcrafted numerical examples, and deterministic test scenarios exist only to verify software semantics.

They may be used to test properties such as:

- no future-event leakage;
- bottleneck behavior;
- footprint infeasibility;
- unknown-space handling;
- deterministic estimator output;
- statistical-analysis code correctness.

They must never be reported as robot performance, commissioning results, validation data, efficacy results, or empirical support for the paper hypothesis.

## 2. Simulation has a limited role

Simulation may be used for engineering commissioning, event reproducibility, integration debugging, and protocol rehearsal.

Simulation results must be explicitly labeled as simulation. They cannot substitute for the physical-robot evidence required for the central RecoverNav claim.

## 3. Study A evidence source

Confirmatory Study A evidence must come from executed recovery probes with a traceable experiment record.

Every retained observation must include at least:

- unique trial ID;
- scenario and event ID;
- software commit SHA;
- configuration hash;
- robot/platform identity;
- timestamp;
- pre-event estimator output computed before the event;
- executed recovery outcome;
- raw log reference (ROS bag or equivalent where feasible);
- exclusion/intervention/safety metadata.

No recovery outcome may be invented, inferred from geometry alone, manually assigned for convenience, or replaced by a synthetic label.

## 4. Study B evidence source

Planner-efficacy results must come from matched physical-robot trials under the frozen protocol. J0 and JR must differ only by the recoverability treatment being tested.

## 5. Raw data integrity

Raw experimental records are immutable. Corrections or derived quantities are written to processed data with provenance back to the raw record.

Never overwrite an unfavorable run. Never silently delete a failed run. Every exclusion must be retained with a prespecified reason.

## 6. Paper figures and tables

Publication-facing figures, tables, effect estimates, confidence intervals, and failure rates must be generated from provenance-tracked experimental datasets only.

Synthetic/unit-test fixtures may appear only as clearly labeled explanatory diagrams or method illustrations, never as empirical results.

## 7. Claims before data

Until physical Study A data exist, the project may claim only that it defines and tests a candidate recoverability construct.

Until confirmatory physical Study B data exist, the project must not claim that RecoverNav reduces recovery failures.

## 8. No fabricated values

Do not create placeholder experimental measurements, fake success/failure rates, fake timing values, fabricated AUC values, or invented robot results in repository data directories or publication-facing results.

If a real measurement has not yet been collected, record it as missing/not collected rather than substituting an example value.
