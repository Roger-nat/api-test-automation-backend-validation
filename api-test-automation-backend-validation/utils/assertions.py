from __future__ import annotations

from typing import Any


def assert_status(response, expected: int) -> None:
    assert response.status_code == expected, (
        f"Expected HTTP {expected}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_json_keys(response, *keys: str) -> dict[str, Any]:
    body = response.json()
    missing = [key for key in keys if key not in body]
    assert not missing, f"Missing response keys: {missing}. Response: {body}"
    return body


def assert_error(response, expected_status: int, message_contains: str | None = None) -> dict[str, Any]:
    assert_status(response, expected_status)
    body = response.json()
    assert "detail" in body
    if message_contains:
        assert message_contains.lower() in str(body["detail"]).lower()
    return body
