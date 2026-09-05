# Physical-Robot Experiment Protocol

## Purpose

This document defines the confirmatory physical-robot study for RecoverNav. It is written before efficacy data collection and should be version-frozen before confirmatory trials begin.

## 1. Experimental question

Does recoverability-aware route selection reduce post-invalidation navigation failures compared with a conventional navigation baseline on the same physical mobile robot under matched dynamic indoor trials?

## 2. Experimental unit

One complete point-to-point navigation trial on the physical robot under one predefined scenario, event realization, planner condition, and seed/configuration identifier.

## 3. Conditions

Two planner conditions are compared.

### J0 — baseline

Conventional navigation without an explicit recoverability objective.

### JR — RecoverNav

Identical navigation stack plus the frozen recoverability-aware path objective.

All non-treatment settings must be identical: robot hardware, firmware, localization, map, costmaps, controller, perception, velocity/acceleration limits, collision monitor, goal tolerance, replanning policy, timeout policy, and dynamic-event definition.

## 4. Physical platform

Before confirmatory trials, record and freeze:

- robot model and serial/asset identifier;
- computer and operating system;
- ROS 2 distribution;
- Nav2 version/commit where applicable;
- lidar/camera/odometry sensors used;
- localization method;
- controller and collision/safety configuration;
- battery operating range allowed during trials;
- software commit SHA and experiment configuration hash.

Hardware changes during the confirmatory study require a documented protocol deviation or a new study block.

## 5. Environment

The first study is restricted to controlled indoor environments that contain meaningful route-choice structure, for example:

- two alternative corridors around an obstacle or room block;
- a short route with limited retreat/escape options;
- a longer route preserving an alternative exit or branch;
- controlled door/corridor obstruction or dynamic obstacle insertion.

The environment must be measured and documented. Start/goal poses and event regions must be fixed before confirmatory analysis.

## 6. Dynamic event

Each scenario contains a predefined event capable of invalidating or materially degrading the current route.

Valid event mechanisms include:

- a corridor becomes blocked after the robot commits to a region;
- a movable obstacle is placed into a predefined route segment;
- a door closes according to a predefined trigger;
- a scripted moving obstacle occupies a critical passage.

The trigger must not depend on planner identity. Prefer geometry/state-based triggers (for example, robot crossing a fixed line or entering a fixed region) over human judgment.

The planner must not receive future knowledge of which passage will be blocked unless that information is genuinely available to both conditions through the robot's sensing system.

## 7. Pairing and order

Trials are paired by scenario and event realization. Each matched pair contains one J0 trial and one JR trial under as nearly identical initial conditions as physically possible.

Condition order should be randomized or counterbalanced within blocks to reduce temporal confounding from battery, localization drift, environmental change, operator learning, or hardware temperature.

The randomization schedule must be generated before confirmatory trials and retained with the data.

## 8. Primary endpoint

`post_invalidation_recovery_failure` is binary.

Set it to `1` if any prespecified failure condition occurs after the dynamic event and before successful goal completion. Otherwise set it to `0`.

### Primary failure conditions

A trial is a recovery failure if, after the event:

1. the robot cannot reach the goal within the frozen maximum trial/recovery time;
2. autonomous navigation enters a state from which operator intervention is required to continue;
3. the robot collides or makes disallowed physical contact;
4. the robot becomes trapped with no valid autonomous recovery under the frozen recovery policy;
5. localization failure exceeds the predefined tolerance and autonomous completion is no longer valid;
6. a safety stop becomes terminal under the frozen protocol.

Exact numerical thresholds must be filled and frozen during commissioning, before confirmatory trials.

## 9. Secondary endpoints

Record at minimum:

- `goal_reached`;
- `recovery_time_s`;
- `task_time_s`;
- `planning_latency_ms`;
- `replanning_latency_ms`;
- `executed_path_length_m`;
- `min_clearance_m`;
- `num_replans`;
- `num_recovery_actions`;
- `num_safety_stops`;
- `human_intervention`;
- `collision_or_contact`;
- `localization_failure`;
- recoverability score(s) used by JR;
- route selected before event;
- route selected after event.

## 10. Inclusion and exclusion rules

A trial is included in confirmatory analysis if the experiment begins from a valid initial state, the frozen configuration is loaded, data logging is active, and the predefined dynamic event executes as specified.

Predefine commissioning-related technical exclusions such as:

- logging process failed before the event;
- event mechanism did not execute as specified;
- unrelated human entered the controlled test area;
- hardware emergency unrelated to autonomous navigation invalidated the trial;
- wrong configuration or software commit was loaded.

Do not exclude trials because the planner performed badly. Any post-start exclusion must be recorded with a reason and retained in the manifest.

## 11. Safety

Physical experiments take precedence over data collection. The study must define:

- accessible emergency stop;
- maximum linear and angular velocity;
- controlled test perimeter;
- human supervisor location;
- minimum allowed clearance rules where applicable;
- conditions requiring immediate manual termination.

A manual safety intervention is never hidden from the dataset. If it occurs because autonomous behavior became unsafe, it contributes to the relevant failure/intervention endpoint according to the frozen rules.

## 12. Commissioning vs confirmatory data

Commissioning runs are used to debug hardware, sensing, event timing, thresholds, logging, and the experimental procedure. They must be clearly marked and excluded from confirmatory efficacy analysis.

After the protocol, code/configuration, scenarios, primary endpoint, exclusions, and analysis plan are frozen, confirmatory collection begins. Changes after that point must be documented as protocol deviations.

## 13. Sample-size planning

The confirmatory number of matched trials must be selected using an a priori power or precision analysis based on a scientifically meaningful reduction in paired failure probability, not by stopping when a desirable p-value appears.

A pilot/commissioning dataset may inform nuisance parameters or plausible event rates, but confirmatory effect claims must use a separately frozen analysis plan.

## 14. Statistical analysis principles

The primary comparison is paired because J0 and JR are tested on matched scenario/event realizations.

The final analysis plan should report at minimum:

- failure counts and rates by condition;
- paired discordant outcomes;
- an appropriate paired binary-outcome test/effect estimate;
- absolute risk difference with uncertainty interval;
- relative effect where estimable;
- scenario-level breakdown as secondary/exploratory evidence;
- sensitivity analysis for documented protocol deviations/exclusions.

Secondary continuous outcomes should be analyzed as paired measurements where the pairing remains valid. Multiple secondary metrics must not be used to redefine the primary conclusion.

## 15. Required trial artifacts

Each physical trial must retain or reference:

- unique trial ID;
- timestamp;
- planner condition;
- scenario ID;
- pair/block ID;
- software commit SHA;
- configuration hash;
- robot/platform metadata;
- map/version identifier;
- start and goal poses;
- event definition and trigger time;
- outcome record;
- ROS bag or equivalent sensor/state log where feasible;
- planner logs;
- safety/intervention log;
- optional synchronized video;
- operator notes restricted to factual deviations/events.

## 16. Evidence hierarchy

1. Unit/integration tests establish software behavior.
2. Simulation establishes commissioning and scenario feasibility.
3. Physical commissioning establishes experimental operability.
4. Frozen physical confirmatory trials establish evidence for the central efficacy claim.

Only level 4 is intended to answer the primary research question.

## 17. Stop conditions

Data collection may be stopped for safety, hardware damage risk, persistent protocol malfunction, or completion of the prespecified sample. It must not be stopped early solely because preliminary efficacy results look favorable or unfavorable unless a formal sequential design has been specified in advance.
