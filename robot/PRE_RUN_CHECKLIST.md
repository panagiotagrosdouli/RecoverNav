# Physical Robot Pre-Run Checklist

A Study A physical commissioning trial must not start until every applicable item is checked on the actual platform.

## Identity and provenance

- [ ] `platform_id` assigned and recorded.
- [ ] RecoverNav Git commit recorded.
- [ ] Frozen config hash recorded.
- [ ] UTC clock verified.
- [ ] Raw-data destination has sufficient free space.

## Robot

- [ ] Battery adequate for the planned block of trials.
- [ ] Wheels/drive respond normally.
- [ ] Physical footprint matches the frozen configuration.
- [ ] Emergency stop tested immediately before trials.
- [ ] Human safety operator present and knows stop procedure.

## Sensing and localization

- [ ] Verified obstacle-sensing topic from `TOPIC_BINDINGS.md` is live and geometrically plausible.
- [ ] Verified odometry topic from `TOPIC_BINDINGS.md` is live and changes consistently with physical motion.
- [ ] TF tree is connected for the verified global, odometry, base, and sensor frames.
- [ ] Map is the intended experimental map.
- [ ] Localization is initialized and visually/quantitatively checked.
- [ ] Unknown-space handling matches the frozen estimator rule.

## Navigation

- [ ] Nav2 lifecycle nodes are active on the discovered physical stack.
- [ ] Verified global and local costmap streams update from physical sensing.
- [ ] Baseline navigation can execute the route without the invalidating event.
- [ ] Verified global-plan stream records the candidate route before event activation.

## Event apparatus

- [ ] Event apparatus is physically safe and repeatable.
- [ ] Trigger rule is planner-independent and frozen for this scenario.
- [ ] Event is not observable by the planner before its prescribed activation.
- [ ] Event timestamp can be recovered from a retained event/log source.

## Logging

- [ ] `robot/validate_physical_stack.sh` passes with the machine-local verified topic bindings.
- [ ] `robot/run_physical_trial.sh` starts successfully.
- [ ] Every required topic is verified live; missing topics block the run rather than being replaced by guessed defaults.
- [ ] Trial ID is unique.
- [ ] Raw bag path is retained for `raw_log_ref`.

## Trial validity

After the run, do not assign `recovery_success` from memory. Determine it using the frozen endpoint rule and retained logs. Safety intervention is always recorded even if the robot later reaches the goal.
