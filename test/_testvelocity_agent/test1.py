'''import logging
from unittest.mock import MagicMock

from core.agents.velocity_agent.agent import VelocityAgent

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def redis_mock():
    mock = MagicMock()
    mock.get_window_count = MagicMock()
    return mock


@pytest.fixture
def kafka_mock():
    mock = MagicMock()
    mock.send = MagicMock()
    return mock
def test_redis_connection_failure_fallback(redis_mock, kafka_mock, caplog):
    """
    Scenario:
    Redis throws connection failure

    Expected:
    - Agent does NOT crash
    - Risk score returns fallback (0.3)
    - Warning is logged
    """

    # Arrange: force Redis failure
    redis_mock.get_window_count.side_effect = Exception("Redis connection failed")

    agent = VelocityAgent(redis_mock, kafka_mock)

    # Capture logs
    with caplog.at_level(logging.WARNING):

        result = agent.process({
            "user_id": "u3",
            "transaction_id": "t4"
        })

    # Assert fallback behavior
    assert result.risk_score == 0.3
    assert result.window_count in [0, 1]  # depending on your fallback design

    # Assert warning log was emitted
    assert "Redis failure" in caplog.text or "Redis" in caplog.text

    # Ensure system still publishes to Kafka (important in streaming systems)
    kafka_mock.send.assert_called_once()'''
