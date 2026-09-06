#!/usr/bin/env python3
"""Extract RecoverNav event-marker evidence from a physical ROS 2 bag."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from recovernav.event_marker import parse_event_marker_payload

EVENT_TOPIC = "/recovernav/event_marker"
EXPECTED_TYPE = "std_msgs/msg/String"


def extract_event_marker(bag_dir: Path) -> dict[str, object]:
    """Read exactly one event marker and derive its position on the bag timeline."""

    try:
        import rosbag2_py
        from rclpy.serialization import deserialize_message
        from rosidl_runtime_py.utilities import get_message
    except ImportError as exc:
        raise RuntimeError(
            "ROS 2 Python bag dependencies are unavailable; run on the robot ROS 2 environment"
        ) from exc

    if not (bag_dir / "metadata.yaml").is_file():
        raise ValueError("bag directory must contain metadata.yaml")

    storage_options = rosbag2_py.StorageOptions(uri=str(bag_dir), storage_id="")
    converter_options = rosbag2_py.ConverterOptions("", "")
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = {topic.name: topic.type for topic in reader.get_all_topics_and_types()}
    if EVENT_TOPIC not in topic_types:
        raise ValueError(f"bag does not contain required event topic: {EVENT_TOPIC}")
    if topic_types[EVENT_TOPIC] != EXPECTED_TYPE:
        raise ValueError(
            f"event topic type mismatch: expected {EXPECTED_TYPE}, got {topic_types[EVENT_TOPIC]}"
        )

    message_type = get_message(EXPECTED_TYPE)
    first_timestamp_ns: int | None = None
    markers: list[tuple[int, str]] = []

    while reader.has_next():
        topic, data, timestamp_ns = reader.read_next()
        if first_timestamp_ns is None:
            first_timestamp_ns = timestamp_ns
        if topic != EVENT_TOPIC:
            continue
        message = deserialize_message(data, message_type)
        markers.append((timestamp_ns, message.data))

    if first_timestamp_ns is None:
        raise ValueError("bag contains no messages")
    if len(markers) != 1:
        raise ValueError(f"expected exactly one event marker, found {len(markers)}")

    marker_timestamp_ns, payload = markers[0]
    parsed = parse_event_marker_payload(payload)
    trigger_time_s = (marker_timestamp_ns - first_timestamp_ns) / 1_000_000_000
    if trigger_time_s < 0:
        raise ValueError("event marker timestamp precedes first recorded bag message")

    return {
        "event_id": parsed["event_id"],
        "marker_utc": parsed["utc"],
        "event_topic": EVENT_TOPIC,
        "event_message_type": EXPECTED_TYPE,
        "bag_first_timestamp_ns": first_timestamp_ns,
        "event_marker_timestamp_ns": marker_timestamp_ns,
        "event_trigger_time_s": trigger_time_s,
        "timing_reference": "seconds_from_first_recorded_bag_message",
        "marker_payload": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag_dir", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()

    if args.output_json.exists():
        raise FileExistsError(f"refusing to overwrite: {args.output_json}")

    evidence = extract_event_marker(args.bag_dir.resolve())
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
