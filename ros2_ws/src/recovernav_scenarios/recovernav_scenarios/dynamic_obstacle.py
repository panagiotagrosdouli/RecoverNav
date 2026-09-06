from __future__ import annotations

import subprocess
from pathlib import Path

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from std_msgs.msg import Bool


class DynamicObstacle(Node):
    def __init__(self) -> None:
        super().__init__("recovernav_dynamic_obstacle")
        self.declare_parameter("scenario", "two_routes")
        self.declare_parameter("trigger_seconds", -1.0)
        self.declare_parameter("world_name", "recovernav")
        self.scenario = str(self.get_parameter("scenario").value)
        config_path = Path(get_package_share_directory("recovernav_scenarios")) / "config" / "scenarios.yaml"
        with config_path.open("r", encoding="utf-8") as stream:
            scenarios = yaml.safe_load(stream)
        if self.scenario not in scenarios:
            raise ValueError(f"unknown scenario: {self.scenario}")
        cfg = scenarios[self.scenario]
        self.xyz = tuple(float(v) for v in cfg["obstacle"])
        configured = float(self.get_parameter("trigger_seconds").value)
        self.trigger_seconds = configured if configured >= 0.0 else float(cfg["trigger_seconds"])
        self.triggered = False
        self.create_subscription(Bool, "/recovernav/trigger_obstacle", self._trigger_msg, 10)
        self.event_pub = self.create_publisher(PointStamped, "/recovernav/obstacle_event", 10)
        self.timer = self.create_timer(self.trigger_seconds, self.trigger)
        self.get_logger().info(
            f"scenario={self.scenario}; obstacle timer={self.trigger_seconds:.2f}s position={self.xyz}"
        )

    def _trigger_msg(self, msg: Bool) -> None:
        if msg.data:
            self.trigger()

    def trigger(self) -> None:
        if self.triggered:
            return
        x, y, z = self.xyz
        request = f'name: "dynamic_obstacle" position: {{x: {x}, y: {y}, z: {z}}}'
        command = [
            "gz", "service", "-s", f"/world/{self.get_parameter('world_name').value}/set_pose",
            "--reqtype", "gz.msgs.Pose", "--reptype", "gz.msgs.Boolean", "--timeout", "3000",
            "--req", request,
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            self.get_logger().error(f"Gazebo set_pose failed ({result.returncode}): {result.stderr.strip()}")
            return
        self.triggered = True
        event = PointStamped()
        event.header.stamp = self.get_clock().now().to_msg()
        event.header.frame_id = "map"
        event.point.x, event.point.y, event.point.z = x, y, z
        self.event_pub.publish(event)
        self.get_logger().info(f"DYNAMIC OBSTACLE TRIGGERED at ({x:.2f}, {y:.2f}, {z:.2f})")
        if self.timer is not None:
            self.timer.cancel()


def main() -> None:
    rclpy.init()
    node = DynamicObstacle()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
