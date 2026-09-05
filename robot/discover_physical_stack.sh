#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <output_directory>" >&2
  exit 2
fi

OUT="$1"
mkdir -p "$OUT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

{
  echo "timestamp_utc=${STAMP}"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -srmo)"
  echo "ros_distro=${ROS_DISTRO:-UNSET}"
  echo "rmw_implementation=${RMW_IMPLEMENTATION:-UNSET}"
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "recovernav_commit=$(git rev-parse HEAD)"
  else
    echo "recovernav_commit=UNAVAILABLE"
  fi
} > "${OUT}/host_and_ros.txt"

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 command not found" >&2
  exit 3
fi

ros2 node list | sort > "${OUT}/nodes.txt"
ros2 topic list -t | sort > "${OUT}/topics_with_types.txt"
ros2 service list -t | sort > "${OUT}/services_with_types.txt"
ros2 action list -t | sort > "${OUT}/actions_with_types.txt"

# Best-effort package/version inventory. Missing packages are recorded rather
# than replaced with assumptions.
{
  for pkg in nav2_bringup nav2_bt_navigator nav2_controller nav2_planner nav2_costmap_2d nav2_amcl tf2_ros; do
    if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
      prefix="$(ros2 pkg prefix "$pkg")"
      echo "$pkg=$prefix"
    else
      echo "$pkg=NOT_FOUND"
    fi
  done
} > "${OUT}/package_presence.txt"

# Capture TF frame names from a short live sample if tf2_tools is available.
if ros2 pkg prefix tf2_tools >/dev/null 2>&1; then
  timeout 8s ros2 run tf2_tools view_frames --ros-args -p wait_time:=3.0 \
    > "${OUT}/tf2_tools_stdout.txt" 2> "${OUT}/tf2_tools_stderr.txt" || true
  for candidate in frames.pdf frames.gv; do
    if [[ -f "$candidate" ]]; then
      mv "$candidate" "$OUT/"
    fi
  done
fi

# Record parameters for likely Nav2 nodes only when those nodes actually exist.
while IFS= read -r node; do
  case "$node" in
    */planner_server|*/controller_server|*/global_costmap/global_costmap|*/local_costmap/local_costmap|*/amcl|*/bt_navigator)
      safe="$(echo "$node" | tr '/' '_' | sed 's/^_//')"
      ros2 param dump "$node" > "${OUT}/params_${safe}.yaml" 2> "${OUT}/params_${safe}.stderr" || true
      ;;
  esac
done < "${OUT}/nodes.txt"

echo "Physical ROS 2 stack discovery written to: ${OUT}"