'''import time
from core.agents.velocity_agent.agent import VelocityAgent
from core.orchestrator.context import TransactionContext


def test_velocity_performance():
    agent = VelocityAgent()

    num_transactions = 1000
    transactions = []

    # Generate test data
    for i in range(num_transactions):
        transactions.append({
            "user_id": f"user_{i}",
            "tx_count_last_2min": i % 10  # mix of values (0–9)
        })

    start_time = time.time()

    results = []
    for tx in transactions:
        context = TransactionContext(tx)
        result = agent.run(context)
        results.append(result)

    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / num_transactions

    print("\n=== PERFORMANCE TEST ===")
    print(f"Total Transactions: {num_transactions}")
    print(f"Total Time: {total_time:.6f} sec")
    print(f"Avg Time per Tx: {avg_time:.8f} sec")

    # Basic performance assertion (adjust as needed)
    assert total_time < 1.0   # should run under 1 second'''