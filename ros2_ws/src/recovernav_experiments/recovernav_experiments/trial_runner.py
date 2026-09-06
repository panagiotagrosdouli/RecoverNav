from __future__ import annotations

import json
import math
import time
from pathlib import Path

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from nav_msgs.msg import OccupancyGrid, Odometry, Path as NavPath
from std_msgs.msg import Bool


def path_length(path: NavPath) -> float:
    return sum(
        math.hypot(b.pose.position.x - a.pose.position.x, b.pose.position.y - a.pose.position.y)
        for a, b in zip(path.poses, path.poses[1:])
    )


class TrialRunner(BasicNavigator):
    def __init__(self) -> None:
        super().__init__(node_name="recovernav_trial_runner")
        self.declare_parameter("planner", "recovernav")
        self.declare_parameter("scenario", "two_routes")
        self.declare_parameter("seed", 0)
        self.declare_parameter("timeout_seconds", 120.0)
        self.declare_parameter("results_dir", "results/ros2")
        self.declare_parameter("commit_distance", 1.0)
        self.planner = str(self.get_parameter("planner").value)
        self.scenario = str(self.get_parameter("scenario").value)
        self.seed = int(self.get_parameter("seed").value)
        self.timeout = float(self.get_parameter("timeout_seconds").value)
        self.results_dir = Path(str(self.get_parameter("results_dir").value))
        self.commit_distance = float(self.get_parameter("commit_distance").value)
        self.trajectory: list[tuple[float, float, float]] = []
        self.plan_lengths: list[float] = []
        self.plan_times: list[float] = []
        self.q_min: float | None = None
        self.q_mean: float | None = None
        self.obstacle_requested = False
        self.obstacle_event_time: float | None = None
        self.obstacle_position: tuple[float, float, float] | None = None
        self.distance = 0.0
        self._last_xy: tuple[float, float] | None = None
        self._goal_wall: float | None = None
        self._obstacle_wall: float | None = None
        self.initial_plan_observed_latency: float | None = None
        self.post_obstacle_plan_observed_latency: float | None = None
        self.create_subscription(Odometry, "/odom", self._odom, 50)
        self.create_subscription(NavPath, "/plan", self._plan, 10)
        self.create_subscription(OccupancyGrid, "/recovernav/recoverability_grid", self._q_grid, 1)
        self.create_subscription(PointStamped, "/recovernav/obstacle_event", self._obstacle_event, 10)
        self.trigger_pub = self.create_publisher(Bool, "/recovernav/trigger_obstacle", 10)

    def _odom(self, msg: Odometry) -> None:
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.trajectory.append((stamp, x, y))
        if self._last_xy is not None:
            self.distance += math.hypot(x - self._last_xy[0], y - self._last_xy[1])
        self._last_xy = (x, y)
        if self.distance >= self.commit_distance and not self.obstacle_requested:
            self.trigger_pub.publish(Bool(data=True))
            self.obstacle_requested = True
            self.get_logger().info(
                f"Requested dynamic obstacle after {self.commit_distance:.2f} m route commitment"
            )

    def _plan(self, msg: NavPath) -> None:
        length = path_length(msg)
        if length <= 0.0:
            return
        now = time.monotonic()
        self.plan_lengths.append(length)
        self.plan_times.append(now)
        if self.initial_plan_observed_latency is None and self._goal_wall is not None:
            self.initial_plan_observed_latency = now - self._goal_wall
        if self._obstacle_wall is not None and now >= self._obstacle_wall and self.post_obstacle_plan_observed_latency is None:
            self.post_obstacle_plan_observed_latency = now - self._obstacle_wall

    def _q_grid(self, msg: OccupancyGrid) -> None:
        values = [v / 100.0 for v in msg.data if v >= 0]
        if values:
            self.q_min = min(values)
            self.q_mean = sum(values) / len(values)

    def _obstacle_event(self, msg: PointStamped) -> None:
        self.obstacle_event_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.obstacle_position = (msg.point.x, msg.point.y, msg.point.z)
        self._obstacle_wall = time.monotonic()

    def run(self) -> dict:
        initial = PoseStamped()
        initial.header.frame_id = "map"
        initial.header.stamp = self.get_clock().now().to_msg()
        initial.pose.position.x = -3.0
        initial.pose.position.y = 0.0
        initial.pose.orientation.w = 1.0
        self.setInitialPose(initial)
        self.waitUntilNav2Active(localizer="amcl")

        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.pose.position.x = 3.0
        goal.pose.position.y = 0.0
        goal.pose.orientation.w = 1.0

        start_wall = time.monotonic()
        self._goal_wall = start_wall
        self.goToPose(goal)
        timed_out = False
        while not self.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.1)
            if time.monotonic() - start_wall > self.timeout:
                timed_out = True
                self.cancelTask()
                break
        elapsed = time.monotonic() - start_wall
        result = self.getResult()
        success = (not timed_out) and result == TaskResult.SUCCEEDED
        result_name = "timeout" if timed_out else str(result)
        data = {
            "scenario": self.scenario,
            "seed": self.seed,
            "planner": self.planner,
            "success": success,
            "failure_reason": "" if success else result_name,
            "start": [-3.0, 0.0],
            "goal": [3.0, 0.0],
            "initial_path_length": self.plan_lengths[0] if self.plan_lengths else None,
            "latest_path_length": self.plan_lengths[-1] if self.plan_lengths else None,
            "executed_trajectory_length": self.distance,
            "number_of_global_plans": len(self.plan_lengths),
            "number_of_replans": max(0, len(self.plan_lengths) - 1),
            "time_to_goal": elapsed,
            "initial_plan_observed_latency": self.initial_plan_observed_latency,
            "post_obstacle_plan_observed_latency": self.post_obstacle_plan_observed_latency,
            "minimum_q_grid": self.q_min,
            "mean_q_grid": self.q_mean,
            "dynamic_obstacle_requested": self.obstacle_requested,
            "dynamic_obstacle_trigger_time": self.obstacle_event_time,
            "dynamic_obstacle_position": self.obstacle_position,
            "trajectory": self.trajectory,
            "global_plan_lengths": self.plan_lengths,
        }
        self.results_dir.mkdir(parents=True, exist_ok=True)
        out = self.results_dir / f"{self.scenario}_{self.planner}_seed{self.seed}.json"
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.get_logger().info(f"trial result written to {out}")
        return data


def main() -> None:
    rclpy.init()
    navigator = TrialRunner()
    try:
        result = navigator.run()
        print(json.dumps(result, indent=2))
    finally:
        navigator.destroyNode()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
