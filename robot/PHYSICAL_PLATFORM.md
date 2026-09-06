# RecoverNav Physical Robot Platform

**Status:** platform-selection gate. No empirical trial is valid until the concrete hardware fields below are filled from the robot actually used.

RecoverNav targets a real differential-drive indoor mobile robot running ROS 2 and Nav2. This document intentionally does **not** invent a robot model, sensor, footprint, compute unit, or performance specification.

## Required hardware freeze

Before the first commissioning run, record from the physical robot:

- `platform_id` — stable experiment identifier;
- manufacturer and exact model;
- drive type and wheel geometry;
- measured footprint polygon / effective collision radius;
- onboard or companion compute model;
- operating system version;
- ROS 2 distribution;
- Nav2 version / source commit where applicable;
- lidar exact model, mounting pose, scan rate and configured range;
- IMU exact model if used;
- wheel odometry source;
- localization method and map source;
- emergency-stop mechanism;
- battery/power constraints relevant to repeatability.

## Measurement rule

Dimensions used by RecoverNav (`c_min`, footprint, inflation and related geometry) must come from the actual robot/configuration or a documented manufacturer specification verified against the platform. They must not be chosen to make the estimator produce desirable scores.

## Software boundary

The physical integration must expose robot-observable information only:

- occupancy/costmap available at planning time;
- current localization estimate;
- robot footprint and frozen feasibility limits;
- candidate route geometry.

The future invalidating event, future obstacle location, and eventual recovery outcome are forbidden estimator inputs.

## First physical milestone

A milestone is complete only when the robot can produce one provenance-complete commissioning record plus its raw ROS bag. This is an instrumentation milestone, **not** evidence that RecoverNav works.
