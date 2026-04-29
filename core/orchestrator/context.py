# context.py

class TransactionContext:
    def __init__(self, transaction: dict):
        self.transaction = transaction
        self.agent_results = []
        self.risk_score = 0.0

    def add_result(self, result):
        self.agent_results.append(result)

    def finalize(self):
        return {
            "risk_score": self.risk_score,
            "agent_results": self.agent_results
        }