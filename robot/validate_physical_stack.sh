#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <verified_topics_file>" >&2
  exit 2
fi

BINDINGS="$1"
[[ -f "$BINDINGS" ]] || { echo "missing bindings file: $BINDINGS" >&2; exit 2; }
command -v ros2 >/dev/null || { echo "ros2 not found" >&2; exit 1; }

mapfile -t LIVE_TOPICS < <(ros2 topic list)
mapfile -t LIVE_NODES < <(ros2 node list)

fail=0
while IFS= read -r topic; do
  [[ -z "$topic" || "$topic" =~ ^# ]] && continue
  if ! printf '%s\n' "${LIVE_TOPICS[@]}" | grep -Fxq -- "$topic"; then
    echo "MISSING TOPIC: $topic" >&2
    fail=1
    continue
  fi
  type="$(ros2 topic type "$topic" 2>/dev/null || true)"
  if [[ -z "$type" ]]; then
    echo "NO TYPE: $topic" >&2
    fail=1
  else
    echo "OK TOPIC: $topic [$type]"
  fi
done < "$BINDINGS"

if [[ ${#LIVE_NODES[@]} -eq 0 ]]; then
  echo "NO ROS 2 NODES DISCOVERED" >&2
  fail=1
else
  echo "ROS 2 nodes discovered: ${#LIVE_NODES[@]}"
fi

# Nav2 presence is checked from the live graph rather than assumed from package names.
if ! printf '%s\n' "${LIVE_NODES[@]}" | grep -Eq '/?(planner_server|controller_server|bt_navigator)(/|$)'; then
  echo "NO EXPECTED NAV2 CORE NODE DISCOVERED" >&2
  fail=1
else
  echo "Nav2 core node discovered"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "PHYSICAL STACK VALIDATION FAILED" >&2
  exit 1
fi

echo "PHYSICAL STACK VALIDATION PASSED"
