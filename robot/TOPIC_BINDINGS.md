# Physical ROS 2 Topic Bindings

**Status:** unresolved until `robot/discover_physical_stack.sh` is run on the real robot.

RecoverNav must bind to topics and frames discovered from the live physical stack. Do not copy names from a tutorial unless they are verified on the actual robot.

## Required bindings

Record the exact live names and message types for:

| Role | Live name | Message type | Verified |
|---|---|---|---|
| laser / obstacle sensing | TBD | TBD | no |
| wheel/filtered odometry | TBD | TBD | no |
| map | TBD | TBD | no |
| localization pose | TBD | TBD | no |
| velocity command | TBD | TBD | no |
| global plan | TBD | TBD | no |
| global costmap | TBD | TBD | no |
| local costmap | TBD | TBD | no |

## Required frames

| Role | Live frame | Verified |
|---|---|---|
| global/map | TBD | no |
| odometry | TBD | no |
| robot base | TBD | no |
| lidar/sensor | TBD | no |

## Verification rule

A binding becomes `Verified: yes` only after all of the following hold on the physical robot:

1. the topic/frame exists in live discovery output;
2. the message type is recorded;
3. the stream is observed during robot motion or sensing as applicable;
4. the binding is captured in the commissioning provenance bundle.

Missing required information blocks commissioning. RecoverNav must fail closed rather than substitute guessed defaults.
