import json
from pathlib import Path

import pytest

from recovernav.finalize_trial import build_trial_record, finalize_trial_record


def _capture(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "artifacts"
    capture = root / "trial_001"
    bag = capture / "bag"
    bag.mkdir(parents=True)
    (bag / "metadata.yaml").write_text("rosbag2_bagfile_information:\n", encoding="utf-8")
    (capture / "CAPTURE_COMPLETE").write_text("", encoding="utf-8")
    provenance = """trial_id=trial_001
scenario_id=scenario_a
platform_id=robot_real_01
timestamp_utc=2026-09-06T06:00:00Z
software_commit=8e0a7bf64f18afd70e143eb98fcbdfdc6a8b5d2f
config_sha256=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
"""
    (capture / "provenance.env").write_text(provenance, encoding="utf-8")
    event_evidence = {
        "event_id": "event_01",
        "event_trigger_time_s": 12.0,
        "event_topic": "/recovernav/event_marker",
        "event_message_type": "std_msgs/msg/String",
        "timing_reference": "seconds_from_first_recorded_bag_message",
    }
    (capture / "event_evidence.json").write_text(
        json.dumps(event_evidence), encoding="utf-8"
    )
    return root, capture


def _measurements() -> dict[str, object]:
    return {
        "pre_event_rho": 0.4,
        "recovery_success": True,
        "data_split": "commissioning",
    }


def test_build_record_uses_capture_and_event_provenance(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    record = build_trial_record(capture, root, _measurements())

    assert record["trial_id"] == "trial_001"
    assert record["scenario_id"] == "scenario_a"
    assert record["platform_id"] == "robot_real_01"
    assert record["event_id"] == "event_01"
    assert record["event_trigger_time_s"] == 12.0
    assert record["raw_log_ref"] == "trial_001/bag"


def test_missing_capture_complete_is_rejected(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    (capture / "CAPTURE_COMPLETE").unlink()

    with pytest.raises(ValueError, match="not marked complete"):
        build_trial_record(capture, root, _measurements())


def test_missing_event_evidence_is_rejected(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    (capture / "event_evidence.json").unlink()

    with pytest.raises(ValueError, match="event_evidence.json is missing"):
        build_trial_record(capture, root, _measurements())


def test_manual_event_timing_is_rejected(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    measurements = _measurements() | {"event_trigger_time_s": 99.0}

    with pytest.raises(ValueError, match="must come from event_evidence.json"):
        build_trial_record(capture, root, measurements)


def test_missing_measurement_is_rejected(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    measurements = _measurements()
    del measurements["recovery_success"]

    with pytest.raises(ValueError, match="missing measured fields"):
        build_trial_record(capture, root, measurements)


def test_excluded_trial_requires_reason(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    measurements = _measurements() | {"excluded": True}

    with pytest.raises(ValueError, match="exclusion_reason"):
        build_trial_record(capture, root, measurements)


def test_finalizer_refuses_overwrite(tmp_path: Path) -> None:
    root, capture = _capture(tmp_path)
    measurements_path = tmp_path / "measurements.json"
    measurements_path.write_text(json.dumps(_measurements()), encoding="utf-8")
    output_path = tmp_path / "record.json"
    output_path.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        finalize_trial_record(capture, root, measurements_path, output_path)
