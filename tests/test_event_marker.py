import pytest

from recovernav.event_marker import parse_event_marker_payload


def test_parse_valid_event_marker() -> None:
    parsed = parse_event_marker_payload("event_id=blockage_a;utc=2026-09-06T06:45:00Z")
    assert parsed == {"event_id": "blockage_a", "utc": "2026-09-06T06:45:00Z"}


@pytest.mark.parametrize(
    "payload",
    [
        "",
        "event_id=blockage_a",
        "event_id=blockage_a;utc=not-a-time",
        "event_id=;utc=2026-09-06T06:45:00Z",
        "utc=2026-09-06T06:45:00Z;event_id=blockage_a;extra=x",
    ],
)
def test_invalid_event_marker_is_rejected(payload: str) -> None:
    with pytest.raises(ValueError):
        parse_event_marker_payload(payload)
