#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <trial_id> <output_directory>" >&2
  exit 2
fi

TRIAL_ID="$1"
OUT_ROOT="$2"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT_ROOT}/${TRIAL_ID}_${STAMP}"
mkdir -p "$OUT"

# Record only topics that exist on the running physical stack. ros2 bag fails
# loudly if the integration is not operational; no synthetic fallback exists.
TOPICS=(
  /tf
  /tf_static
  /scan
  /odom
  /map
  /amcl_pose
  /cmd_vel
  /plan
  /global_costmap/costmap
  /local_costmap/costmap
)

printf '%s\n' "trial_id=${TRIAL_ID}" > "${OUT}/provenance.txt"
printf '%s\n' "timestamp_utc=${STAMP}" >> "${OUT}/provenance.txt"
printf '%s\n' "recovernav_commit=$(git rev-parse HEAD)" >> "${OUT}/provenance.txt"
printf '%s\n' "ros_distro=${ROS_DISTRO:-UNSET}" >> "${OUT}/provenance.txt"
printf '%s\n' "hostname=$(hostname)" >> "${OUT}/provenance.txt"

ros2 topic list > "${OUT}/ros2_topics.txt"
ros2 node list > "${OUT}/ros2_nodes.txt"
ros2 bag record --output "${OUT}/bag" "${TOPICS[@]}"
