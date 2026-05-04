#manual testing code for velocity agent
'''from core.agents.velocity_agent.agent import VelocityAgent
from core.orchestrator.context import TransactionContext

def run():
    agent = VelocityAgent()

    print("=== Velocity Agent Tester ===")

    while True:
        try:
            user_id = input("\nEnter user_id (or 'exit'): ")
            if user_id.lower() == "exit":
                break

            tx_count = int(input("Enter tx_count_last_2min: "))

            transaction = {
                "user_id": user_id,
                "tx_count_last_2min": tx_count
            }

            context = TransactionContext(transaction)

            result = agent.run(context)

            print("\n--- RESULT ---")
            print("Score :", result.score)
            print("Reason:", result.reason)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    run()''' #only if main can also be removed to automate the tests

# Automated tests for VelocityAgent automatically detects test_ prefix and runs the tests
'''import pytest
from unittest.mock import MagicMock
from core.agents.velocity_agent.agent import VelocityAgent

# FIXTURES

@pytest.fixture
def mock_redis():
    r = MagicMock()

    # default behavior: empty window
    r.zadd.return_value = 1
    r.zremrangebyscore.return_value = 1
    r.zcount.return_value = 0
    return r


@pytest.fixture
def mock_producer():
    p = MagicMock()
    p.send.return_value = None
    p.flush.return_value = None
    return p


@pytest.fixture
def agent(mock_redis, mock_producer):
    return VelocityAgent(mock_redis, mock_producer)


# TEST CASES

def test_normal_low_frequency(agent, mock_redis):
    mock_redis.zcount.return_value = 1  # 1 txn/hr
    score = agent.score("u1", "t1")
    assert 0.0 <= score <= 0.2


def test_burst_frequency(agent, mock_redis):
    # simulate 6 txns in 2 min
    mock_redis.zcount.side_effect = lambda *args, **kwargs: 6
    score = agent.score("u1", "t2")
    assert score >= 0.8


def test_edge_zero_transactions(agent, mock_redis):
    mock_redis.zcount.return_value = 0
    score = agent.score("u_zero", "t0")
    assert score == 0.0


def test_moderate_activity(agent, mock_redis):
    mock_redis.zcount.side_effect = lambda *args, **kwargs: 3
    score = agent.score("u2", "t3")
    assert 0.0 < score < 0.8


def test_redis_failure_returns_safe_default(mock_redis, mock_producer):
    mock_redis.zadd.side_effect = Exception("Redis down")
    agent = VelocityAgent(mock_redis, mock_producer)

    score = agent.score("u_fail", "t_fail")
    assert score == 0.1


def test_kafka_publish_called(agent, mock_producer, mock_redis):
    agent.score("u3", "t4")
    assert mock_producer.send.called


def test_latency_under_limit(agent, mock_redis):
    score = agent.score("u4", "t5")
    assert isinstance(score, float)'''

'''
import pytest
import logging
from unittest.mock import MagicMock

from core.agents.velocity_agent.agent import VelocityAgent
from core.agents.velocity_agent.rules import VelocityRules

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("velocity_test")

@pytest.fixture
def redis_mock():
    r = MagicMock()
    r.get_window_count = MagicMock()
    return r


@pytest.fixture
def kafka_mock():
    k = MagicMock()
    k.send = MagicMock()
    return k

def test_normal_frequency(redis_mock, kafka_mock):
    """
    Expected: low/medium risk (normal behavior)
    """

    redis_mock.get_window_count.return_value = 2

    agent = VelocityAgent(redis_mock, kafka_mock)

    result = agent.process({
        "user_id": "user_1",
        "transaction_id": "txn_1"
    })


    print(f"""
        USER: {result.user_id}
        WINDOW: {result.window_count}
        RISK: {result.risk_score}
        """)
    assert 0.2 < result.risk_score < 0.8

def test_burst_frequency(redis_mock, kafka_mock):
    """
    Expected: high risk (>= 0.8)
    """

    redis_mock.get_window_count.return_value = 6

    agent = VelocityAgent(redis_mock, kafka_mock)

    result = agent.process({
        "user_id": "user_1",
        "transaction_id": "txn_2"
    })

    print(f"""
    USER: {result.user_id}
    WINDOW: {result.window_count}
    RISK: {result.risk_score}
    """)
    assert result.risk_score >= 0.8

def test_zero_transactions(redis_mock, kafka_mock):

    redis_mock.get_window_count.return_value = 0  

    agent = VelocityAgent(redis_mock, kafka_mock)

    result = agent.process({
        "user_id": "u2",
        "transaction_id": "t3"
    })

    print(f"""
    USER: {result.user_id}
    WINDOW: {result.window_count}
    RISK: {result.risk_score}
    """)
    assert result.risk_score <= 0.1
'''
