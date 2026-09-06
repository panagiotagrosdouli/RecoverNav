#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <trial_id> <output_directory> <topic_binding_file>" >&2
  exit 2
fi

TRIAL_ID="$1"
OUT_ROOT="$2"
BINDINGS_FILE="$3"

if [[ ! -f "$BINDINGS_FILE" ]]; then
  echo "binding file not found: $BINDINGS_FILE" >&2
  exit 3
fi

# Binding file format: one verified live ROS 2 topic per non-empty line.
# Lines beginning with # are ignored. No default topics are substituted.
mapfile -t TOPICS < <(grep -vE '^\s*(#|$)' "$BINDINGS_FILE")
if [[ ${#TOPICS[@]} -eq 0 ]]; then
  echo "binding file contains no topics" >&2
  exit 4
fi

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 command not found" >&2
  exit 5
fi

mapfile -t LIVE_TOPICS < <(ros2 topic list)
for topic in "${TOPICS[@]}"; do
  if ! printf '%s\n' "${LIVE_TOPICS[@]}" | grep -Fxq "$topic"; then
    echo "required verified topic is not live: $topic" >&2
    exit 6
  fi
done

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT_ROOT}/${TRIAL_ID}_${STAMP}"
mkdir -p "$OUT"

cp "$BINDINGS_FILE" "${OUT}/topic_bindings.txt"
printf '%s\n' "trial_id=${TRIAL_ID}" > "${OUT}/provenance.txt"
printf '%s\n' "timestamp_utc=${STAMP}" >> "${OUT}/provenance.txt"
printf '%s\n' "recovernav_commit=$(git rev-parse HEAD)" >> "${OUT}/provenance.txt"
printf '%s\n' "ros_distro=${ROS_DISTRO:-UNSET}" >> "${OUT}/provenance.txt"
printf '%s\n' "hostname=$(hostname)" >> "${OUT}/provenance.txt"

ros2 topic list -t | sort > "${OUT}/ros2_topics_with_types.txt"
ros2 node list | sort > "${OUT}/ros2_nodes.txt"

ros2 bag record --output "${OUT}/bag" "${TOPICS[@]}"
