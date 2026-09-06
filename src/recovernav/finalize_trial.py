"""Finalize a physical Study A trial from retained capture artifacts.

This module never infers experimental outcomes. Operator/analysis measurements
must be supplied explicitly after the physical run and are accepted only when
they match the retained capture provenance and pass evidence validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from recovernav.evidence import validate_trial_evidence

_REQUIRED_MEASUREMENTS = (
    "event_id",
    "pre_event_rho",
    "recovery_success",
    "event_trigger_time_s",
    "data_split",
)

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

    for field in ("trial_id", "scenario_id", "platform_id", "timestamp_utc", "software_commit"):
        if field not in provenance:
            raise ValueError(f"capture provenance missing field: {field}")
    if "config_sha256" not in provenance:
        raise ValueError("capture provenance missing field: config_sha256")

    missing = [field for field in _REQUIRED_MEASUREMENTS if field not in measurements]
    if missing:
        raise ValueError(f"missing measured fields: {', '.join(missing)}")

    if measurements["data_split"] not in _ALLOWED_SPLITS:
        raise ValueError("data_split must be commissioning, validation, or held_out")

    record: dict[str, Any] = {
        "trial_id": provenance["trial_id"],
        "timestamp_utc": provenance["timestamp_utc"],
        "scenario_id": provenance["scenario_id"],
        "event_id": measurements["event_id"],
        "platform_id": provenance["platform_id"],
        "software_commit": provenance["software_commit"],
        "config_hash": provenance["config_sha256"],
        "pre_event_rho": measurements["pre_event_rho"],
        "recovery_success": measurements["recovery_success"],
        "event_trigger_time_s": measurements["event_trigger_time_s"],
        "data_split": measurements["data_split"],
        "raw_log_ref": str(relative_capture / "bag"),
    }

    optional_fields = (
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
    for field in optional_fields:
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
        raise ValueError("measurements file must contain a JSON object")

    output = Path(output_path)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing record: {output}")

    record = build_trial_record(capture_dir, artifact_root, measurements)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
