from __future__ import annotations

from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch(context):
    scenario = LaunchConfiguration("scenario").perform(context)
    planner = LaunchConfiguration("planner").perform(context)
    use_rviz = LaunchConfiguration("rviz").perform(context).lower() == "true"
    use_gz_gui = LaunchConfiguration("gz_gui").perform(context).lower() == "true"
    if planner not in {"baseline", "recovernav"}:
        raise RuntimeError("planner must be 'baseline' or 'recovernav'")

    bringup_share = Path(get_package_share_directory("recovernav_bringup"))
    scenarios_share = Path(get_package_share_directory("recovernav_scenarios"))
    nav2_share = Path(get_package_share_directory("nav2_bringup"))
    gz_share = Path(get_package_share_directory("ros_gz_sim"))
    tb3_gazebo = Path(get_package_share_directory("turtlebot3_gazebo"))

    world = scenarios_share / "worlds" / f"{scenario}.sdf"
    map_yaml = scenarios_share / "maps" / f"{scenario}.yaml"
    if not world.exists() or not map_yaml.exists():
        raise RuntimeError(f"Unknown scenario '{scenario}'")

    urdf_file = tb3_gazebo / "urdf" / "turtlebot3_burger.urdf"
    if not urdf_file.exists():
        raise RuntimeError(f"TurtleBot3 Burger URDF not found: {urdf_file}")
    robot_description = urdf_file.read_text(encoding="utf-8")

    common_yaml = bringup_share / "config" / "nav2_common.yaml"
    planner_yaml = bringup_share / "config" / f"planner_{planner}.yaml"
    with common_yaml.open("r", encoding="utf-8") as stream:
        params = yaml.safe_load(stream)
    with planner_yaml.open("r", encoding="utf-8") as stream:
        override = yaml.safe_load(stream)
    for node_name, node_cfg in override.items():
        params.setdefault(node_name, {}).setdefault("ros__parameters", {}).update(
            node_cfg["ros__parameters"]
        )
    merged = Path("/tmp") / f"recovernav_nav2_{planner}_{scenario}.yaml"
    with merged.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(params, stream, sort_keys=False)

    gz_launch = gz_share / "launch" / "gz_sim.launch.py"
    spawn_launch = tb3_gazebo / "launch" / "spawn_turtlebot3.launch.py"
    actions = [
        SetEnvironmentVariable("TURTLEBOT3_MODEL", "burger"),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", str(tb3_gazebo / "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(gz_launch)),
            launch_arguments={"gz_args": f"-r -s -v2 {world}"}.items(),
        ),
    ]
    if use_gz_gui:
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(gz_launch)),
                launch_arguments={"gz_args": "-g -v2"}.items(),
            )
        )

    actions.extend(
        [
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                parameters=[{"use_sim_time": True, "robot_description": robot_description}],
                output="screen",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(spawn_launch)),
                launch_arguments={"x_pose": "-3.0", "y_pose": "0.0"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(nav2_share / "launch" / "bringup_launch.py")),
                launch_arguments={
                    "map": str(map_yaml),
                    "use_sim_time": "true",
                    "params_file": str(merged),
                    "autostart": "true",
                }.items(),
            ),
        ]
    )
    if use_rviz:
        actions.append(
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", str(bringup_share / "rviz" / "recovernav.rviz")],
                parameters=[{"use_sim_time": True}],
                output="screen",
            )
        )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("scenario", default_value="two_routes"),
            DeclareLaunchArgument("planner", default_value="recovernav"),
            DeclareLaunchArgument("rviz", default_value="true"),
            DeclareLaunchArgument("gz_gui", default_value="true"),
            OpaqueFunction(function=_launch),
        ]
    )
