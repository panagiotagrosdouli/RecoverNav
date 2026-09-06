from pathlib import Path

from recovernav.evidence import validate_trial_evidence


def _record(raw_log_ref: str) -> dict[str, object]:
    return {
        "trial_id": "trial-001",
        "scenario_id": "scenario-001",
        "timestamp_utc": "2026-09-06T00:00:00Z",
        "platform_id": "physical-platform",
        "software_commit": "abcdef1",
        "config_hash": "config123",
        "raw_log_ref": raw_log_ref,
        "pre_event_rho": 0.5,
        "recovery_success": True,
        "event_id": "event-001",
        "event_trigger_time_s": 2.0,
        "data_split": "commissioning",
    }


def _valid_bag(root: Path) -> Path:
    bag = root / "bag"
    bag.mkdir()
    (bag / "metadata.yaml").write_text("rosbag2_bagfile_information:\n", encoding="utf-8")
    (bag / "bag_0.mcap").write_bytes(b"physical-bag-test-fixture")
    return bag


def test_valid_ros_bag_artifact_passes(tmp_path: Path) -> None:
    _valid_bag(tmp_path)

    assert validate_trial_evidence(_record("bag"), tmp_path) == []


def test_missing_raw_log_is_rejected(tmp_path: Path) -> None:
    errors = validate_trial_evidence(_record("missing-bag"), tmp_path)

    assert "raw_log_ref does not exist" in errors


def test_empty_ros_bag_metadata_is_rejected(tmp_path: Path) -> None:
    bag = tmp_path / "bag"
    bag.mkdir()
    (bag / "metadata.yaml").write_text("", encoding="utf-8")
    (bag / "bag_0.mcap").write_bytes(b"physical-bag-test-fixture")

    errors = validate_trial_evidence(_record("bag"), tmp_path)

    assert "raw ROS bag directory must contain non-empty metadata.yaml" in errors


def test_missing_ros_bag_storage_is_rejected(tmp_path: Path) -> None:
    bag = tmp_path / "bag"
    bag.mkdir()
    (bag / "metadata.yaml").write_text("rosbag2_bagfile_information:\n", encoding="utf-8")

    errors = validate_trial_evidence(_record("bag"), tmp_path)

    assert "raw ROS bag directory must contain non-empty .db3 or .mcap storage data" in errors


def test_raw_log_cannot_escape_artifact_root(tmp_path: Path) -> None:
    errors = validate_trial_evidence(_record("../outside"), tmp_path)

    assert "raw_log_ref must resolve inside artifact_root" in errors


def test_invalid_timestamp_and_commit_are_rejected(tmp_path: Path) -> None:
    _valid_bag(tmp_path)
    record = _record("bag")
    record["timestamp_utc"] = "not-a-time"
    record["software_commit"] = "not-a-commit"

    errors = validate_trial_evidence(record, tmp_path)

    assert "timestamp_utc must be an ISO-8601 UTC timestamp ending in Z" in errors
    assert "software_commit must be a 7-40 character hexadecimal Git commit" in errors
