"""Small, dependency-free authentication primitives for a future HTTP layer."""

import hashlib
import hmac
import os


def configured_api_key() -> str | None:
    """Return the optional service key without exposing it in logs or traces."""
    value = os.getenv("MCP_AGENT_API_KEY", "").strip()
    return value or None


def authorize(presented_key: str | None, expected_key: str | None = None) -> bool:
    """Validate a service key using a constant-time digest comparison."""
    expected = expected_key if expected_key is not None else configured_api_key()
    if not presented_key or not expected:
        return False
    return hmac.compare_digest(
        hashlib.sha256(presented_key.encode()).digest(),
        hashlib.sha256(expected.encode()).digest(),
    )
