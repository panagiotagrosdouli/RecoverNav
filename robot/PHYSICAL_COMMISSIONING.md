# First Physical Commissioning Procedure

This procedure exists to obtain the first **real**, provenance-complete RecoverNav commissioning artifact. It is not a performance experiment and must not be used to claim estimator efficacy.

## 1. Discover the live robot stack

Run on the computer attached to the physical robot while the normal ROS 2/Nav2 stack is active:

```bash
bash robot/discover_physical_stack.sh data/raw/platform_discovery/$(date -u +%Y%m%dT%H%M%SZ)
```

Use the resulting files to fill `robot/PHYSICAL_PLATFORM.md` and `robot/TOPIC_BINDINGS.md`. Do not fill unknown fields by assumption.

## 2. Verify baseline robot operation

Before any invalidating event:

- manually verify emergency stop;
- verify localization and TF;
- command a short, unobstructed Nav2 goal;
- verify that raw sensor, odometry, costmap and plan streams are present;
- inspect that commanded motion and physical motion agree qualitatively;
- abort if localization jumps, sensing is stale, or control is unstable.

This baseline motion is an instrumentation check, not a trial outcome.

## 3. Freeze one commissioning scenario

Choose one physical start pose, one goal, and one repeatable obstruction placement. Record the geometry in measured coordinates or a marked floor plan. The obstruction must remain absent/unobservable until the prescribed event trigger.

The first commissioning event should prioritize repeatability and operator safety over difficulty. Do not tune the geometry to produce a desired recovery outcome.

## 4. Start provenance capture

Create a unique trial ID and run the bag recorder only after its topic bindings have been updated from live discovery. Record:

- platform ID;
- RecoverNav commit;
- config hash;
- UTC timestamp;
- scenario ID and event ID;
- raw ROS bag path;
- event trigger timestamp;
- any safety intervention.

## 5. Execute one real run

Start the robot from the frozen start state, command the frozen goal, activate the obstruction at the frozen trigger, and let the frozen recovery policy operate unless safety requires intervention.

No value is manually invented if logging fails. A logging failure makes the observation unusable and the run remains an engineering commissioning event only.

## 6. Label only from evidence

Assign `recovery_success` only after checking the frozen endpoint definition against the logs. If the operator intervened, record that fact regardless of later task completion.

## 7. Archive immutably

The raw bag and provenance files are never overwritten. Any later parsing or correction produces a derived record referencing the original raw artifact.

## Gate to Study A data collection

Do not start confirmatory Study A until several commissioning runs demonstrate that event timing, bag capture, localization, costmaps, endpoint labeling and platform metadata are repeatable and complete. Commissioning outcomes themselves are excluded from the confirmatory estimator-validity analysis.
