"""Pure helpers for RecoverNav physical event-marker evidence."""

from __future__ import annotations

from datetime import datetime


def parse_event_marker_payload(payload: str) -> dict[str, str]:
    """Parse the frozen ``event_id=...;utc=...`` marker payload.

    The parser is intentionally strict so malformed or ambiguous physical event
    markers fail closed rather than being repaired during analysis.
    """

    if not isinstance(payload, str) or not payload:
        raise ValueError("event marker payload must be a non-empty string")

    parts = payload.split(";")
    if len(parts) != 2:
        raise ValueError("event marker payload must contain exactly event_id and utc")

    values: dict[str, str] = {}
    for part in parts:
        key, separator, value = part.partition("=")
        if not separator or not key or not value:
            raise ValueError("event marker payload contains an invalid field")
        if key in values:
            raise ValueError(f"duplicate event marker field: {key}")
        values[key] = value

    if set(values) != {"event_id", "utc"}:
        raise ValueError("event marker payload fields must be exactly event_id and utc")

    if not values["event_id"].strip():
        raise ValueError("event_id must be non-empty")

    utc = values["utc"]
    if not utc.endswith("Z"):
        raise ValueError("event marker utc must end in Z")
    try:
        datetime.fromisoformat(utc[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("event marker utc must be valid ISO-8601 UTC") from exc

    return values
