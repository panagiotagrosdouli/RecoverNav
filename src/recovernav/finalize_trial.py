"""Finalize a physical Study A trial from retained capture artifacts.

This module never infers experimental outcomes. Operator/analysis measurements
must be supplied explicitly after the physical run and are accepted only when
they match retained capture provenance and pass evidence validation. Event
identity and timing are derived from extracted ROS-bag marker evidence.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from recovernav.evidence import validate_trial_evidence

_REQUIRED_MEASUREMENTS = (
    "pre_event_rho",
    "recovery_success",
    "data_split",
)
_OPTIONAL_MEASUREMENTS = (
    "video_ref",
    "pre_event_escape_capacity",
    "clearance_only_score",
    "estimator_runtime_ms",
    "recovery_time_s",
    "human_intervention",
    "collision_or_contact",
    "localization_failure",
    "terminal_safety_stop",
    "excluded",
    "exclusion_reason",
    "operator_notes",
)
_ALLOWED_MEASUREMENTS = set(_REQUIRED_MEASUREMENTS) | set(_OPTIONAL_MEASUREMENTS)
_ALLOWED_SPLITS = {"commissioning", "validation", "held_out"}


def _read_provenance(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition("=")
        if not separator or not key or not value:
            raise ValueError(f"invalid provenance line: {line!r}")
        values[key] = value
    return values


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_frozen_snapshots(capture: Path, provenance: dict[str, str]) -> None:
    required = {
        "config_sha256": capture / "frozen_config.snapshot",
        "verified_topics_sha256": capture / "verified_topics.snapshot.txt",
    }
    for provenance_field, snapshot in required.items():
        if provenance_field not in provenance:
            raise ValueError(f"capture provenance missing field: {provenance_field}")
        if not snapshot.is_file():
            raise ValueError(f"capture snapshot is missing: {snapshot.name}")
        if _sha256(snapshot) != provenance[provenance_field]:
            raise ValueError(f"capture snapshot hash mismatch: {snapshot.name}")


def _read_event_evidence(capture: Path) -> dict[str, Any]:
    path = capture / "event_evidence.json"
    if not path.is_file():
        raise ValueError("capture event_evidence.json is missing")
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        raise TypeError("event_evidence.json must contain a JSON object")

    required = {
        "event_id",
        "event_trigger_time_s",
        "event_topic",
        "event_message_type",
        "timing_reference",
    }
    missing = sorted(required - evidence.keys())
    if missing:
        raise ValueError(f"event evidence missing fields: {', '.join(missing)}")
    if evidence["event_topic"] != "/recovernav/event_marker":
        raise ValueError("unexpected event marker topic")
    if evidence["event_message_type"] != "std_msgs/msg/String":
        raise ValueError("unexpected event marker message type")
    if evidence["timing_reference"] != "seconds_from_first_recorded_bag_message":
        raise ValueError("unexpected event timing reference")
    return evidence


def build_trial_record(
    capture_dir: str | Path,
    artifact_root: str | Path,
    measurements: dict[str, Any],
) -> dict[str, Any]:
    """Build and validate a Study A record from one completed physical capture."""

    capture = Path(capture_dir).resolve()
    root = Path(artifact_root).resolve()

    try:
        relative_capture = capture.relative_to(root)
    except ValueError as exc:
        raise ValueError("capture_dir must be inside artifact_root") from exc

    if not (capture / "CAPTURE_COMPLETE").is_file():
        raise ValueError("capture is not marked complete")

    provenance_path = capture / "provenance.env"
    if not provenance_path.is_file():
        raise ValueError("capture provenance.env is missing")
    provenance = _read_provenance(provenance_path)
    event_evidence = _read_event_evidence(capture)

    for field in ("trial_id", "scenario_id", "platform_id", "timestamp_utc", "software_commit"):
        if field not in provenance:
            raise ValueError(f"capture provenance missing field: {field}")
    _verify_frozen_snapshots(capture, provenance)

    unknown = sorted(set(measurements) - _ALLOWED_MEASUREMENTS)
    if unknown:
        raise ValueError(f"unknown measurement fields: {', '.join(unknown)}")

    missing = [field for field in _REQUIRED_MEASUREMENTS if field not in measurements]
    if missing:
        raise ValueError(f"missing measured fields: {', '.join(missing)}")

    if measurements["data_split"] not in _ALLOWED_SPLITS:
        raise ValueError("data_split must be commissioning, validation, or held_out")

    record: dict[str, Any] = {
        "trial_id": provenance["trial_id"],
        "timestamp_utc": provenance["timestamp_utc"],
        "scenario_id": provenance["scenario_id"],
        "event_id": event_evidence["event_id"],
        "platform_id": provenance["platform_id"],
        "software_commit": provenance["software_commit"],
        "config_hash": provenance["config_sha256"],
        "pre_event_rho": measurements["pre_event_rho"],
        "recovery_success": measurements["recovery_success"],
        "event_trigger_time_s": event_evidence["event_trigger_time_s"],
        "data_split": measurements["data_split"],
        "raw_log_ref": str(relative_capture / "bag"),
    }

    for field in _OPTIONAL_MEASUREMENTS:
        if field in measurements:
            record[field] = measurements[field]

    errors = validate_trial_evidence(record, root)
    if errors:
        raise ValueError("trial evidence validation failed: " + "; ".join(errors))

    if record.get("excluded") is True and not record.get("exclusion_reason"):
        raise ValueError("excluded trials require a non-empty exclusion_reason")

    return record


def finalize_trial_record(
    capture_dir: str | Path,
    artifact_root: str | Path,
    measurements_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Write one validated final record without overwriting an existing file."""

    measurements = json.loads(Path(measurements_path).read_text(encoding="utf-8"))
    if not isinstance(measurements, dict):
        raise TypeError("measurements file must contain a JSON object")

    output = Path(output_path)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing record: {output}")

    record = build_trial_record(capture_dir, artifact_root, measurements)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
