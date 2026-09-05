# First Real Physical Trial Workflow

This workflow creates evidence artifacts from an actual ROS 2 robot execution. It does not generate experimental outcomes without a run.

## Preconditions

1. The actual robot is identified in the physical-platform freeze record.
2. `discover_physical_stack.sh` has been run on that robot computer.
3. A machine-local verified topics file contains only topics confirmed live on that stack.
4. `validate_physical_stack.sh` passes.
5. The physical scenario and planner-independent event trigger are defined before the run.
6. The safety operator and emergency stop are ready.

## Capture

Run from the RecoverNav checkout on the robot computer:

```bash
robot/run_physical_trial.sh \
  <trial_id> \
  <scenario_id> \
  <platform_id> \
  <frozen_config_file> \
  <verified_topics_file> \
  <raw_output_root>
```

The script records the exact Git commit, SHA-256 of the frozen config and topic bindings, UTC timestamp, ROS distribution environment, host, live ROS graph snapshots, config/topic snapshots, and the ROS 2 bag.

The capture is marked complete only when the bag has a non-empty `metadata.yaml`.

## Outcome separation

The capture script deliberately does **not** ask for or assign `recovery_success`, `pre_event_rho`, event time, collision/contact, intervention, localization failure, or terminal safety stop. Those values must come from the actual run and the frozen endpoint/measurement procedures.

This separation prevents a shell command from silently turning operator expectation into an experimental label.

## Evidence admission

A completed capture is still not automatically a retained Study A observation. Before admission:

- compute/verify the pre-event estimator output from information available before event activation;
- establish event time from the retained event/log source;
- apply the frozen recovery endpoint rule to the execution;
- record all safety/intervention fields;
- create the Study A record referencing the retained bag;
- run the evidence validator against the artifact root;
- retain exclusions with their prespecified reason rather than deleting the run.

## No-result rule

If the robot has not physically executed the trial, there is no Study A observation. Missing measurements remain missing; they are never replaced by demonstration values, geometry-derived labels, or synthetic outcomes.
