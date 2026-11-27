def retry_delay(attempt: int, base_seconds: float = 0.25) -> float:
    """Return a small exponential backoff delay for a retry attempt."""
    return base_seconds * (2 ** max(attempt - 1, 0))


def retry_count(value: int) -> int:
    """Clamp retries to a safe bounded range."""
    return max(0, min(value, 5))
