from setuptools import find_packages, setup

package_name = "recovernav_experiments"
setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="panagiotagrosdouli",
    maintainer_email="75089541+panagiotagrosdouli@users.noreply.github.com",
    description="RecoverNav ROS experiment tools",
    license="Apache-2.0",
    entry_points={"console_scripts": ["trial_runner = recovernav_experiments.trial_runner:main"]},
)
