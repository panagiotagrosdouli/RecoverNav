#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <trial_id> <scenario_id> <platform_id> <config_file> <verified_topics_file> <output_root>" >&2
}

[[ $# -eq 6 ]] || { usage; exit 2; }

TRIAL_ID="$1"
SCENARIO_ID="$2"
PLATFORM_ID="$3"
CONFIG_FILE="$4"
TOPICS_FILE="$5"
OUTPUT_ROOT="$6"

[[ -n "$TRIAL_ID" && -n "$SCENARIO_ID" && -n "$PLATFORM_ID" ]] || {
  echo "trial_id, scenario_id and platform_id must be non-empty" >&2
  exit 2
}
[[ -f "$CONFIG_FILE" ]] || { echo "missing config file: $CONFIG_FILE" >&2; exit 2; }
[[ -f "$TOPICS_FILE" ]] || { echo "missing verified topics file: $TOPICS_FILE" >&2; exit 2; }
command -v ros2 >/dev/null || { echo "ros2 not found" >&2; exit 1; }
command -v git >/dev/null || { echo "git not found" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum not found" >&2; exit 1; }

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/validate_physical_stack.sh" "$TOPICS_FILE"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TRIAL_DIR="${OUTPUT_ROOT}/${TRIAL_ID}_${STAMP}"
BAG_DIR="${TRIAL_DIR}/bag"
mkdir -p "$TRIAL_DIR"

SOFTWARE_COMMIT="$(git rev-parse HEAD)"
CONFIG_HASH="$(sha256sum "$CONFIG_FILE" | awk '{print $1}')"
TOPICS_HASH="$(sha256sum "$TOPICS_FILE" | awk '{print $1}')"

cat > "${TRIAL_DIR}/provenance.env" <<EOF
trial_id=${TRIAL_ID}
scenario_id=${SCENARIO_ID}
platform_id=${PLATFORM_ID}
timestamp_utc=${STAMP}
software_commit=${SOFTWARE_COMMIT}
config_sha256=${CONFIG_HASH}
verified_topics_sha256=${TOPICS_HASH}
ros_distro=${ROS_DISTRO:-UNSET}
hostname=$(hostname)
EOF

cp -- "$CONFIG_FILE" "${TRIAL_DIR}/frozen_config.snapshot"
cp -- "$TOPICS_FILE" "${TRIAL_DIR}/verified_topics.snapshot.txt"
ros2 node list > "${TRIAL_DIR}/ros2_nodes.txt"
ros2 topic list -t > "${TRIAL_DIR}/ros2_topics.txt"

mapfile -t TOPICS < <(grep -Ev '^[[:space:]]*(#|$)' "$TOPICS_FILE")
[[ ${#TOPICS[@]} -gt 0 ]] || { echo "verified topics file contains no topics" >&2; exit 2; }

cat <<EOF
Physical trial capture is armed.
trial_id: ${TRIAL_ID}
scenario_id: ${SCENARIO_ID}
platform_id: ${PLATFORM_ID}
artifact_dir: ${TRIAL_DIR}

Start the robot trial only after the safety operator confirms the physical scene.
Stop ros2 bag with Ctrl-C after the run. This script does not assign recovery_success.
EOF

set +e
ros2 bag record --output "$BAG_DIR" "${TOPICS[@]}"
BAG_STATUS=$?
set -e

if [[ "$BAG_STATUS" -ne 0 ]]; then
  echo "ros2 bag record failed with status ${BAG_STATUS}; trial is not evidence-ready" >&2
  exit "$BAG_STATUS"
fi

if [[ ! -s "${BAG_DIR}/metadata.yaml" ]]; then
  echo "bag metadata.yaml missing or empty; trial is not evidence-ready" >&2
  exit 1
fi

sha256sum "${BAG_DIR}/metadata.yaml" > "${TRIAL_DIR}/bag_metadata.sha256"
touch "${TRIAL_DIR}/CAPTURE_COMPLETE"

echo "Capture complete: ${TRIAL_DIR}"
echo "Outcome remains UNASSIGNED. Finalize it only from the frozen endpoint rule and retained evidence."
