"""Validation helpers for physical RecoverNav evidence artifacts.

These checks are intentionally conservative. They verify provenance and the
presence of raw physical-run artifacts; they do not infer outcomes or fabricate
missing data.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

_REQUIRED_FIELDS = (
    "trial_id",
    "scenario_id",
    "timestamp_utc",
    "platform_id",
    "software_commit",
    "config_hash",
    "raw_log_ref",
    "pre_event_rho",
    "recovery_success",
    "event_id",
    "event_trigger_time_s",
    "data_split",
)


def _valid_iso8601_utc(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _valid_commit(value: object) -> bool:
    if not isinstance(value, str) or not 7 <= len(value) <= 40:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)


def validate_trial_evidence(record: Mapping[str, Any], artifact_root: str | Path) -> list[str]:
    """Return validation errors for one physical Study A trial artifact.

    ``raw_log_ref`` must resolve beneath ``artifact_root`` and point to an
    existing non-empty artifact. A ROS 2 bag directory is considered present
    only when it contains ``metadata.yaml``.
    """

    errors: list[str] = []
    root = Path(artifact_root).resolve()

    for field in _REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if errors:
        return errors

    if not _valid_iso8601_utc(record["timestamp_utc"]):
        errors.append("timestamp_utc must be an ISO-8601 UTC timestamp ending in Z")

    if not _valid_commit(record["software_commit"]):
        errors.append("software_commit must be a 7-40 character hexadecimal Git commit")

    rho = record["pre_event_rho"]
    if not isinstance(rho, (int, float)) or isinstance(rho, bool) or not 0.0 <= rho <= 1.0:
        errors.append("pre_event_rho must be numeric and in [0, 1]")

    event_time = record["event_trigger_time_s"]
    if (
        not isinstance(event_time, (int, float))
        or isinstance(event_time, bool)
        or event_time < 0.0
    ):
        errors.append("event_trigger_time_s must be a non-negative number")

    if not isinstance(record["recovery_success"], bool):
        errors.append("recovery_success must be boolean")

    raw_ref = record["raw_log_ref"]
    if not isinstance(raw_ref, str) or not raw_ref.strip():
        errors.append("raw_log_ref must be a non-empty relative path")
        return errors

    candidate = (root / raw_ref).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        errors.append("raw_log_ref must resolve inside artifact_root")
        return errors

    if not candidate.exists():
        errors.append("raw_log_ref does not exist")
        return errors

    if candidate.is_dir():
        metadata = candidate / "metadata.yaml"
        if not metadata.is_file() or metadata.stat().st_size == 0:
            errors.append("raw ROS bag directory must contain non-empty metadata.yaml")
    elif candidate.stat().st_size == 0:
        errors.append("raw_log_ref points to an empty file")

    return errors
