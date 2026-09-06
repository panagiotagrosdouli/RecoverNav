#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <event_id>" >&2
  exit 2
fi

EVENT_ID="$1"
[[ -n "$EVENT_ID" ]] || { echo "event_id must be non-empty" >&2; exit 2; }
command -v ros2 >/dev/null || { echo "ros2 not found" >&2; exit 1; }

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PAYLOAD="event_id=${EVENT_ID};utc=${STAMP}"

ros2 topic pub --once /recovernav/event_marker std_msgs/msg/String "{data: '${PAYLOAD}'}"
echo "published /recovernav/event_marker: ${PAYLOAD}"
