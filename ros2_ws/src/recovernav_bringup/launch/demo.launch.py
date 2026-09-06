from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup = Path(get_package_share_directory("recovernav_bringup"))
    planner = LaunchConfiguration("planner")
    scenario = LaunchConfiguration("scenario")
    rviz = LaunchConfiguration("rviz")
    return LaunchDescription(
        [
            DeclareLaunchArgument("planner", default_value="recovernav"),
            DeclareLaunchArgument("scenario", default_value="two_routes"),
            DeclareLaunchArgument("rviz", default_value="true"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(bringup / "launch" / "simulation.launch.py")),
                launch_arguments={"planner": planner, "scenario": scenario, "rviz": rviz}.items(),
            ),
            TimerAction(
                period=8.0,
                actions=[
                    Node(
                        package="recovernav_scenarios",
                        executable="dynamic_obstacle",
                        parameters=[{"scenario": scenario, "use_sim_time": True}],
                        output="screen",
                    ),
                    Node(
                        package="recovernav_experiments",
                        executable="trial_runner",
                        parameters=[{"planner": planner, "scenario": scenario, "use_sim_time": True}],
                        output="screen",
                    ),
                ],
            ),
        ]
    )
