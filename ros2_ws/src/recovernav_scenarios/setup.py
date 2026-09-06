from setuptools import find_packages, setup

package_name = "recovernav_scenarios"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/worlds", [
            "worlds/open_world.sdf", "worlds/narrow_corridor.sdf", "worlds/two_routes.sdf",
            "worlds/bottleneck.sdf", "worlds/dead_end.sdf", "worlds/multi_corridor.sdf",
        ]),
        ("share/" + package_name + "/maps", [
            "maps/open_world.pgm", "maps/open_world.yaml", "maps/narrow_corridor.pgm", "maps/narrow_corridor.yaml",
            "maps/two_routes.pgm", "maps/two_routes.yaml", "maps/bottleneck.pgm", "maps/bottleneck.yaml",
            "maps/dead_end.pgm", "maps/dead_end.yaml", "maps/multi_corridor.pgm", "maps/multi_corridor.yaml",
        ]),
        ("share/" + package_name + "/config", ["config/scenarios.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="panagiotagrosdouli",
    maintainer_email="75089541+panagiotagrosdouli@users.noreply.github.com",
    description="RecoverNav Gazebo scenarios",
    license="Apache-2.0",
    entry_points={"console_scripts": ["dynamic_obstacle = recovernav_scenarios.dynamic_obstacle:main"]},
)
