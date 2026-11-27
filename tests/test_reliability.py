from mcp_agent.reliability import retry_count, retry_delay


def test_retry_delay_grows_exponentially():
    assert retry_delay(1) == 0.25
    assert retry_delay(2) == 0.5
    assert retry_delay(3) == 1.0


def test_retry_count_is_bounded():
    assert retry_count(-1) == 0
    assert retry_count(2) == 2
    assert retry_count(99) == 5
