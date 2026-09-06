# RecoverNav

RecoverNav is a lightweight navigation framework for experimenting with recovery-aware path planning in dynamic environments.

It has two complementary execution layers:

- a fast deterministic Python grid simulator for algorithm development and controlled experiments;
- a ROS 2 / Nav2 / Gazebo layer for TurtleBot3 navigation with costmaps, localization, controller execution, dynamic obstacles and a real Nav2 global-planner plugin.

A conventional planner usually minimizes path cost. RecoverNav can additionally penalize states with poor local escape structure, so a route may trade a little distance for more recovery options when the environment changes.

The recoverability value `Q` is a structural score in `[0, 1]`, not a probability of successful recovery.

## Python simulator

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Animated navigation:

```bash
python examples/demo_navigation.py
```

Useful keys: `SPACE` pause/resume, `N` single step, `O` insert the scenario obstacle, `P` replan, `1` baseline A*, `2` RecoverNav, `R` reset.

Compare both planners on the same scenario:

```bash
python examples/compare_planners.py --scenario two_routes --show-heatmap
```

Run paired grid experiments:

```bash
python experiments/run_experiments.py --seeds 20
python experiments/analyze_results.py
```

## Planner objective

The Python and ROS implementations use the same basic idea:

```text
step_cost(x) = nominal_cost(x) + lambda_recovery * (1 - Q(x))
```

`Q(x)` uses local reachable free space and the diversity of reachable exit directions. Dead ends and constrained single-exit regions tend to receive lower scores; open intersections and open areas tend to receive higher scores.

The score is intentionally interpretable and is not a safety guarantee.

## ROS 2 simulation

### Requirements

Target environment:

- Ubuntu 24.04;
- ROS 2 Jazzy;
- Nav2;
- Gazebo Sim / Harmonic through `ros_gz`;
- TurtleBot3 simulation packages;
- RViz2;
- `colcon` and `rosdep`.

A typical binary installation needs packages equivalent to:

```bash
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-turtlebot3 \
  ros-jazzy-turtlebot3-simulations \
  ros-jazzy-ros-gz
```

### Build

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
colcon test
colcon test-result --verbose
```

The ROS workspace contains:

```text
recovernav_planner/       C++17 Nav2 GlobalPlanner plugin and Q implementation
recovernav_bringup/       Gazebo, TurtleBot3, Nav2 and RViz launch/configuration
recovernav_scenarios/     controlled worlds, maps and dynamic obstacle controller
recovernav_experiments/   autonomous goal execution and metrics logging
```

### Launch the simulation

RecoverNav:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch recovernav_bringup simulation.launch.py scenario:=two_routes planner:=recovernav
```

NavFn baseline:

```bash
ros2 launch recovernav_bringup simulation.launch.py scenario:=two_routes planner:=baseline
```

`planner:=baseline` and `planner:=recovernav` use the same world, map, TurtleBot3, localization, costmaps and controller. The selected global planner is the intended primary difference.

The RecoverNav planner publishes:

```text
/recovernav/recoverability_grid
```

as a `nav_msgs/msg/OccupancyGrid`, which is included in the supplied RViz configuration.

### Autonomous dynamic-obstacle demo

```bash
ros2 launch recovernav_bringup demo.launch.py scenario:=two_routes planner:=recovernav
```

or:

```bash
ros2 launch recovernav_bringup demo.launch.py scenario:=two_routes planner:=baseline
```

The demo starts the simulation, sends a navigation goal through Nav2, records odometry and global plans, and requests the scenario obstacle after the robot has executed a configurable commitment distance. The obstacle controller moves an actual Gazebo entity using the world's `set_pose` service. The global costmap can then observe that object through the TurtleBot3 laser scan and Nav2 can issue later plans from the robot's current state.

### Scenarios

The ROS layer includes:

- `open_world`;
- `narrow_corridor`;
- `two_routes`;
- `bottleneck`;
- `dead_end`;
- `multi_corridor`.

Each scenario has a Gazebo SDF world, a static occupancy map and deterministic obstacle-event configuration.

### Paired ROS experiments

From the repository root, after sourcing the workspace:

```bash
python experiments/run_ros2_experiments.py \
  --scenario two_routes \
  --planners baseline recovernav \
  --seeds 3
```

Each trial launches a fresh simulation process so robot pose, obstacle state, Nav2 state and costmaps do not leak into the next trial.

Results are written under:

```text
results/ros2/
```

Per-run JSON includes, where observable:

- scenario, seed and planner;
- success/failure;
- initial and latest global path length;
- executed trajectory length;
- number of global plans and replans;
- time to goal;
- observed first-plan latency;
- observed post-obstacle next-plan latency;
- recoverability-grid summaries;
- obstacle trigger timestamp and position;
- executed odometry trajectory.

Analyze completed trials with:

```bash
python experiments/analyze_ros2_results.py
```

This prints aggregate planner metrics and produces trajectory/replanning plots. It reports measurements rather than assuming one planner is superior.

## Repository structure

```text
src/recovernav/           lightweight Python environment, robot and planners
examples/                 Python visual and interactive demos
experiments/              Python and ROS experiment orchestration/analysis
configs/                  Python experiment configuration
ros2_ws/src/              ROS 2 planner, bringup, scenarios and trial logger
tests/                    Python navigation tests
results/                  generated outputs
```

## Current limitations

The Python layer uses a discrete grid robot. The ROS layer targets a known static map and TurtleBot3 Gazebo simulation; it does not add SLAM, semantic perception, learning, a custom local controller or physical-robot validation. Dynamic obstacle insertion is deterministic so paired runs can be compared. `Q` remains a hand-designed structural score and must not be interpreted as a calibrated recovery probability. RecoverNav makes no safety or universal-superiority claim.
