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

- [ ] `/scan` is live and geometrically plausible.
- [ ] `/odom` is live.
- [ ] TF tree is connected for the required frames.
- [ ] Map is the intended experimental map.
- [ ] Localization is initialized and visually/quantitatively checked.
- [ ] Unknown space handling matches the frozen estimator rule.

## Navigation

- [ ] Nav2 lifecycle nodes are active.
- [ ] Global and local costmaps update from the physical sensors.
- [ ] Baseline navigation can execute the route without the invalidating event.
- [ ] Candidate route is logged before event activation.

## Event apparatus

- [ ] Event apparatus is physically safe and repeatable.
- [ ] Trigger rule is planner-independent and frozen for this scenario.
- [ ] Event is not observable by the planner before its prescribed activation.
- [ ] Event timestamp can be recovered from logs or recorded explicitly.

## Logging

- [ ] `robot/record_study_a_bag.sh` starts successfully.
- [ ] Required ROS topics are present; missing topics are resolved rather than fabricated.
- [ ] Trial ID is unique.
- [ ] Raw bag path is retained for `raw_log_ref`.

## Trial validity

After the run, do not assign `recovery_success` from memory. Determine it using the frozen endpoint rule and retained logs. Safety intervention is always recorded even if the robot later reaches the goal.
